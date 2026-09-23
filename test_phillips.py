"""Pruebas de fechas, selección de IPC, variación real y rastro de la animación."""
import unittest
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from phillips import load_data, build_figure, ROOT

class PhillipsTests(unittest.TestCase):
    def test_join_and_alignment(self):
        d,_,_=load_data()
        ipc=pd.read_csv(ROOT/'ine_ipc_chile.csv')
        ipc=ipc[ipc.Glosa.eq('IPC General')]
        self.assertEqual(len(d),30)
        self.assertEqual((d.mes.iloc[0],d.mes.iloc[-1]),('2024-01','2026-06'))
        self.assertEqual(d.Trimestre.iloc[-1],'May - Jul')
        self.assertEqual(d.fecha_final_ene.iloc[-1],pd.Timestamp('2026-07-01'))
        np.testing.assert_allclose(d.ipc_anual,ipc.iloc[:len(d)]['Variación 12 Meses (%)'])
        final,_,_=load_data(alignment='final')
        matched=d[['fecha_final_ene','desocupacion']].merge(final[['fecha','desocupacion']],left_on='fecha_final_ene',right_on='fecha')
        np.testing.assert_allclose(matched.desocupacion_x,matched.desocupacion_y)
    def test_frames_trail_and_signed_sizes(self):
        d,_,_=load_data()
        d=d.iloc[:3].copy()
        d['ir_real_anual']=[-2.,0.,4.]
        d['ir_magnitud']=d.ir_real_anual.abs()
        f=build_figure(d)
        self.assertEqual(len(f.frames),3)
        for i,frame in enumerate(f.frames):
            self.assertEqual(len(frame.data[0].x),i+1)
            self.assertEqual(frame.data[1].x[0],d.desocupacion.iloc[i])
        self.assertEqual(f.frames[0].data[1].marker.color[0],'#e26545')
        self.assertEqual(f.frames[1].data[1].marker.size[0],0)
        self.assertEqual(f.frames[2].data[1].marker.size[0]/f.frames[0].data[1].marker.size[0],2)
        self.assertEqual(f.frames[2].data[1].marker.sizemode,'area')
    def test_duplicate_month_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for source in ROOT.glob('ine_*_chile.csv'):
                (p/source.name).write_bytes(source.read_bytes())
            ir=pd.read_csv(p/'ine_ir_chile.csv')
            pd.concat([ir,ir.tail(1)]).to_csv(p/'ine_ir_chile.csv',index=False)
            with self.assertRaisesRegex(ValueError,'duplicadas'):
                load_data(p)

if __name__=='__main__': unittest.main()
