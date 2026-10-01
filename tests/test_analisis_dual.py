"""Pruebas del análisis anual/mensual de Curva de Phillips."""

# -----------------------------------------------------------------------------
# Importaciones de pruebas.
# -----------------------------------------------------------------------------
import tempfile
import unittest
from pathlib import Path
from curva_phillips.rutas import DATA_DIR

from curva_phillips.analisis_dual import (
    analizar_anual,
    analizar_mensual,
    cargar_anual,
    generar_informes,
    preparar_mensual,
)


class AnalisisDualTests(unittest.TestCase):
    """Valida resultados numéricos clave y la estructura de los informes."""

    def test_anual_reproduce_pendiente_nairu(self):
        # La nueva tabla anual cubre 1997–2025, incorpora PIB y ya no contiene IR.
        data = cargar_anual(DATA_DIR / "datos_anualizados.csv")
        resultado = analizar_anual(data)
        self.assertEqual((int(data["anio"].min()), int(data["anio"].max())), (1997, 2025))
        self.assertIn("pib_anual", data.columns)
        self.assertNotIn("ir_real_anual", data.columns)
        self.assertEqual(int(resultado["central"].nobs), 28)
        self.assertAlmostEqual(
            float(resultado["central"].params["brecha_desempleo"]),
            -0.3628394815,
            places=6,
        )
        self.assertEqual(int(resultado["contraste_reciente"].nobs), 15)
        self.assertAlmostEqual(
            float(resultado["contraste_reciente"].params["brecha_desempleo"]),
            -0.1263520675,
            places=6,
        )
        self.assertIn("A4_expectativas_pib", resultado["modelos"])

    def test_mensual_cobertura_y_modelo_bic(self):
        # La intersección histórica validada del proyecto debe conservar 186 meses.
        data = preparar_mensual()
        resultado = analizar_mensual(data)
        self.assertEqual(len(data), 186)
        self.assertEqual((data["mes"].iloc[0], data["mes"].iloc[-1]), ("2011-01", "2026-06"))
        self.assertEqual(resultado["mejor_nivel"], "M3_adaptativa_actividad")
        self.assertAlmostEqual(
            float(resultado["central"].params["brecha_desempleo"]),
            -0.1640034543,
            places=5,
        )

    def test_html_dual_tiene_dos_pestanas(self):
        # Genera los informes en un directorio temporal y confirma ambas vistas.
        anual = analizar_anual(cargar_anual(DATA_DIR / "datos_anualizados.csv"))
        mensual = analizar_mensual(preparar_mensual())
        with tempfile.TemporaryDirectory() as tmp:
            rutas = generar_informes(anual, mensual, Path(tmp))
            html = rutas["dual"].read_text(encoding="utf-8")
            self.assertIn("Datos anuales", html)
            self.assertIn("Datos mensuales", html)
            self.assertIn('id="panel-anual"', html)
            self.assertIn('id="panel-mensual"', html)


if __name__ == "__main__":
    unittest.main()