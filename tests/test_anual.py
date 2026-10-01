import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from curva_phillips.analisis_anual import FUENTE, COLUMNAS, cargar_anual, analizar_anual, exportar_resultados
from curva_phillips.productos import figura_anual
from curva_phillips.articulo import secciones


class AnualTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = cargar_anual()
        cls.resultado = analizar_anual(cls.data)

    def test_excel_y_csv_sin_cambios(self):
        csv = cargar_anual(FUENTE.with_name('datos_anualizados.csv'))
        np.testing.assert_allclose(csv[list(COLUMNAS.values())], self.data[list(COLUMNAS.values())], rtol=1e-14)
        raw = pd.read_excel(FUENTE).rename(columns=COLUMNAS).sort_values('anio')
        np.testing.assert_array_equal(raw[list(COLUMNAS.values())].to_numpy(), self.data[list(COLUMNAS.values())].to_numpy())
        meta = json.loads((FUENTE.parent/'metadatos/fuente_anual.json').read_text(encoding='utf-8'))
        self.assertEqual(meta['sha256'], hashlib.sha256(FUENTE.read_bytes()).hexdigest())

    def test_corte_2026_y_cronologia(self):
        self.assertEqual(self.data.anio.tolist(), list(range(1997, 2027)))
        row = self.data.iloc[-1]
        self.assertFalse(row.comparable)
        self.assertEqual(row.corte, 'julio 2026 vs julio 2025')
        np.testing.assert_allclose([row.desocupacion, row.ipc_anual, row.pib_anual], [9.095917167455445, 4.1, -1.5])
        np.testing.assert_allclose(self.data.delta_ipc.iloc[1:], np.diff(self.data.ipc_anual))

    def test_rechaza_duplicados_faltantes_y_no_finitos(self):
        raw = pd.read_excel(FUENTE)
        variants = [pd.concat([raw, raw.iloc[:1]]), raw.iloc[:-1], raw.assign(IPC=np.inf), raw.assign(IPC=np.nan),
                    raw.assign(Año=raw['Año']+.5), raw.drop(columns='IPC')]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bad.csv'
            for invalid in variants:
                invalid.to_csv(path, index=False)
                with self.assertRaises(ValueError):
                    cargar_anual(path)

    def test_orden_original_no_cambia_modelos(self):
        raw = pd.read_excel(FUENTE).sample(frac=1, random_state=7)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'shuffled.csv'
            raw.to_csv(path, index=False)
            np.testing.assert_allclose(cargar_anual(path).delta_ipc.iloc[1:], self.data.delta_ipc.iloc[1:])

    def test_pendiente_restringida_formula_independiente(self):
        for scenario, last in [('historica', 2025), ('sensibilidad_2026', 2026)]:
            d = self.data.loc[self.data.anio.between(1998, last)]
            x, y = d.brecha_desempleo.to_numpy(), d.delta_ipc.to_numpy()
            expected = x @ y / (x @ x)
            fit = self.resultado['modelos'][scenario+'_nairu_restringida']
            self.assertAlmostEqual(fit.params.iloc[0], expected, places=12)
            self.assertEqual(int(fit.nobs), len(d))
            self.assertTrue(fit.use_t)
            self.assertTrue(fit.cov_kwds['use_correction'])

    def test_modelo_pib_y_muestras_comunes(self):
        r = self.resultado
        for scenario, n in [('historica', 28), ('sensibilidad_2026', 29)]:
            comp = r['comparacion'].loc[lambda d: d.escenario.eq(scenario)]
            self.assertEqual(comp.n.tolist(), [n]*6)
            fit = r['modelos'][scenario+'_persistencia_pib']
            d = self.data.loc[self.data.anio.between(1998, 2025 if scenario == 'historica' else 2026)]
            design = np.column_stack([np.ones(len(d)), d.ipc_rezago_1, d.brecha_desempleo, d.pib_anual])
            expected = np.linalg.lstsq(design, d.ipc_anual, rcond=None)[0]
            np.testing.assert_allclose(fit.params, expected, atol=1e-12)

    def test_sensibilidades_preservan_rezagos(self):
        d = self.data.loc[self.data.anio.between(1998, 2025) & ~self.data.anio.between(2020, 2023)]
        expected = np.dot(d.brecha_desempleo, d.delta_ipc)/np.dot(d.brecha_desempleo, d.brecha_desempleo)
        actual = self.resultado['estabilidad'].iloc[-1]
        self.assertAlmostEqual(actual.beta, expected, places=12)
        self.assertEqual(len(self.resultado['influencia']), 28)

    def test_animacion_y_exportacion_ordenadas(self):
        fig = figura_anual(self.data, True)
        ordered = self.data.sort_values(['desocupacion', 'anio'])
        self.assertEqual(len(fig.frames), 30)
        for i, frame in enumerate(fig.frames):
            np.testing.assert_array_equal(frame.data[0].x, ordered.desocupacion.iloc[:i+1])
        self.assertEqual(fig.layout.updatemenus[0].buttons[-1].args[0], ('0',))
        with tempfile.TemporaryDirectory() as tmp:
            exportar_resultados(self.resultado, tmp)
            csv = pd.read_csv(Path(tmp)/'datos_phillips.csv')
            self.assertTrue(csv.desocupacion.is_monotonic_increasing)
            self.assertEqual(csv.anio.tolist(), ordered.anio.tolist())
            summary = json.loads((Path(tmp)/'resumen_modelos.json').read_text(encoding='utf-8'))
            self.assertEqual(summary['observacion_2026']['anio'], 2026)

    def test_articulo_y_codigo_solo_anuales(self):
        text = '\n'.join(t for _, t in secciones(self.resultado)).lower()
        for forbidden in ['mensual', 'desestacional', 'x-13', 'imacec']:
            self.assertNotIn(forbidden, text)
        self.assertIn('julio', text)
        self.assertIn('dimensión social', text)
        self.assertIn('no es un efecto causal', text)
        root = FUENTE.parents[1]
        for folder in ['src', 'scripts']:
            for path in (root/folder).rglob('*.py'):
                self.assertNotIn('analisis_dual', path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
