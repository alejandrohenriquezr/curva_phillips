"""Pruebas del ajuste real, tasas, selección de IPC y rechazo de datos inválidos."""
import tempfile, unittest, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from ipc_x13 import ROOT, read_ipc, ajustar_ipc, executable, specification
from phillips import load_data
from calendario_chile import calendario

class IPCX13Tests(unittest.TestCase):
    def test_calendario_nacional_y_centrado(self):
        fechas=pd.Series(pd.date_range('2020-01-01','2026-09-01',freq='MS'))
        cal,eventos=calendario(fechas)
        self.assertEqual(cal.fecha.iloc[-1],pd.Timestamp('2029-09-01'))
        nombres=set(eventos.fecha)
        self.assertIn('2022-09-16',nombres)  # feriado excepcional nacional
        self.assertIn('2023-01-02',nombres)  # regla Año Nuevo domingo
        self.assertIn('2024-06-20',nombres)  # solsticio móvil
        self.assertNotIn('2020-06-20',nombres)  # ley aún no existía
        mes=cal.loc[cal.fecha.eq('2022-09-01')].iloc[0]
        self.assertEqual(mes.feriados_lunes_viernes,2)  # 18 domingo no se duplica
        self.assertEqual(mes.dias_habiles,20)
        obs=cal.loc[cal.fecha.le(fechas.max())]
        np.testing.assert_allclose(obs.groupby(obs.fecha.dt.month).feriados_centrados.mean(),0,atol=1e-12)

    def test_detecta_feriado_sintetico(self):
        try: exe=executable()
        except FileNotFoundError: self.skipTest('Requiere binario X-13')
        d=read_ipc(); cal,_=calendario(d.fecha)
        d['ipc_indice_original'] *= np.exp(.03*cal.feriados_centrados.iloc[:len(d)].to_numpy())
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            (p/'ipc.spc').write_text(specification(d),encoding='ascii')
            result=subprocess.run([str(exe),'ipc','-s'],cwd=p,capture_output=True,timeout=120)
            self.assertEqual(result.returncode,0)
            diag=dict(line.split(':',1) for line in (p/'ipc.udg').read_text().splitlines() if ':' in line)
            self.assertEqual(diag['aictest.u'].strip(),'yes')
            self.assertIn('feriados_chile',(p/'ipc.mdl').read_text())

    def test_monthly_input_validation(self):
        raw=pd.read_csv(ROOT/'datos/ine_ipc_chile.csv')
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'datos').mkdir()
            path=Path(folder)/'datos/ine_ipc_chile.csv'
            for changed,message in [(raw.drop(index=20),'faltan meses'),(pd.concat([raw,raw.iloc[[10]]]),'duplicados'),(raw.assign(**{'Índice':0}),'positivos')]:
                changed.to_csv(path,index=False)
                with self.assertRaisesRegex(ValueError,message):read_ipc(folder)

    def test_seats_integration_and_selection(self):
        try: executable()
        except FileNotFoundError: self.skipTest('Instala X-13 para la prueba de integración real')
        adjusted,meta=ajustar_ipc()
        self.assertEqual(len(adjusted),len(read_ipc()))
        self.assertTrue(np.isfinite(adjusted.ipc_indice_sa).all())
        self.assertTrue((adjusted.ipc_indice_sa>0).all())
        self.assertGreater(float((adjusted.ipc_indice_sa-adjusted.ipc_indice_original).abs().max()),.001)
        np.testing.assert_allclose(adjusted.ipc_anual_sa.iloc[12:],100*(adjusted.ipc_indice_sa/adjusted.ipc_indice_sa.shift(12)-1).iloc[12:])
        np.testing.assert_allclose(adjusted.ipc_mensual_sa.iloc[1:],100*(adjusted.ipc_indice_sa/adjusted.ipc_indice_sa.shift(1)-1).iloc[1:])
        original,_,_=load_data(ipc_ajuste='original')
        sa,_,_=load_data(ipc_ajuste='sa')
        pd.testing.assert_series_equal(sa.fecha,original.fecha)
        np.testing.assert_allclose(original.ipc_anual,sa.ipc_anual_original)
        expected=adjusted.set_index('fecha').ipc_anual_sa.reindex(sa.fecha)
        np.testing.assert_allclose(sa.ipc_anual,expected)
        dec=sa.fecha.dt.month.eq(12)
        np.testing.assert_allclose(sa.loc[dec,'ipc_acumulado_diciembre'],sa.loc[dec,'ipc_anual'])
        for col in ['desocupacion','ir_real_anual','imacec_sa_anual']:
            np.testing.assert_allclose(sa[col],original[col])
        self.assertEqual(set(meta['seleccion_calendario']),{'dias_semana','feriados_chile'})
        self.assertTrue(set(meta['seleccion_calendario'].values()) <= {'yes','no'})
        self.assertEqual(len(meta['calendario_sha256']),64)
        self.assertEqual(meta['metodo'],'X-13ARIMA-SEATS / SEATS')
        self.assertEqual(len(meta['fuente_sha256']),64)
        # Cache: los cálculos no se revisan cuando no cambian datos, especificación o binario.
        second,_=ajustar_ipc()
        pd.testing.assert_frame_equal(adjusted,second)

if __name__=='__main__':unittest.main()
