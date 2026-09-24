"""Pruebas del ajuste real, tasas, selección de IPC y rechazo de datos inválidos."""
import tempfile, unittest
from pathlib import Path
import numpy as np
import pandas as pd
from ipc_x13 import ROOT, read_ipc, ajustar_ipc, executable
from phillips import load_data

class IPCX13Tests(unittest.TestCase):
    def test_monthly_input_validation(self):
        raw=pd.read_csv(ROOT/'ine_ipc_chile.csv')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'ine_ipc_chile.csv'
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
        self.assertEqual(meta['metodo'],'X-13ARIMA-SEATS / SEATS')
        self.assertEqual(len(meta['fuente_sha256']),64)
        # Cache: los cálculos no se revisan cuando no cambian datos, especificación o binario.
        second,_=ajustar_ipc()
        pd.testing.assert_frame_equal(adjusted,second)

if __name__=='__main__':unittest.main()
