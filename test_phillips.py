"""Pruebas de fechas, selección de IPC, variación real y rastro de la animación."""
import unittest
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from phillips import load_data, build_figure, load_imacec, ROOT

class PhillipsTests(unittest.TestCase):
    def test_join_and_alignment(self):
        d,_,_=load_data()
        ipc=pd.read_csv(ROOT/'ine_ipc_chile.csv')
        ipc=ipc[ipc.Glosa.eq('IPC General')]
        self.assertEqual(len(d),186)
        self.assertEqual((d.mes.iloc[0],d.mes.iloc[-1]),('2011-01','2026-06'))
        self.assertEqual(d.Trimestre.iloc[-1],'May - Jul')
        self.assertEqual(d.fecha_final_ene.iloc[-1],pd.Timestamp('2026-07-01'))
        ipc['fecha']=pd.to_datetime(dict(year=ipc['Año'],month=ipc['Mes'],day=1))
        expected=d[['fecha']].merge(ipc[['fecha','Variación 12 Meses (%)']],on='fecha',validate='one_to_one')
        np.testing.assert_allclose(d.ipc_anual,expected['Variación 12 Meses (%)'])
        final,_,_=load_data(alignment='final')
        matched=d[['fecha_final_ene','desocupacion']].merge(final[['fecha','desocupacion']],left_on='fecha_final_ene',right_on='fecha')
        np.testing.assert_allclose(matched.desocupacion_x,matched.desocupacion_y)
    def test_frames_trail_and_signed_sizes(self):
        d,_,_=load_data()
        d=d.iloc[:3].copy()
        d['ir_real_anual']=[-2.,0.,4.]
        d['ir_magnitud']=d.ir_real_anual.abs()
        d['imacec_promedio_anual']=[-3.,0.,2.]
        f=build_figure(d)
        self.assertEqual(len(f.frames),3)
        for i,frame in enumerate(f.frames):
            self.assertEqual(len(frame.data[0].x),i+1)
            self.assertEqual(frame.data[1].x[0],d.desocupacion.iloc[i])
        self.assertEqual(f.frames[0].data[1].marker.color[0],-3.)
        self.assertEqual((f.layout.coloraxis.cmin,f.layout.coloraxis.cmax,f.layout.coloraxis.cmid),(-3.,3.,0))
        self.assertEqual(f.layout.coloraxis.colorscale[1],(.5,'#f7f7f2'))
        for i,frame in enumerate(f.frames):
            self.assertEqual(frame.data[5].x[0],d.fecha.iloc[i].strftime('%Y-%m-%d'))
            self.assertEqual(frame.data[5].y[0],d.imacec_sa.iloc[i])
            self.assertEqual(len(frame.data[4].x),i+1)
        self.assertEqual(f.frames[1].data[1].marker.size[0],0)
        self.assertEqual(f.frames[2].data[1].marker.size[0]/f.frames[0].data[1].marker.size[0],2)
        self.assertEqual(f.frames[2].data[1].marker.sizemode,'area')
    def test_macro_references_and_distances(self):
        d,_,_=load_data()
        f=build_figure(d)
        shapes=f.layout.shapes
        self.assertEqual(len(shapes),3)
        self.assertEqual((shapes[0].x0,shapes[0].x1),(8.,8.5))
        self.assertEqual((shapes[1].x0,shapes[1].x1),(8.25,8.25))
        self.assertEqual((shapes[2].y0,shapes[2].y1),(3.,3.))
        np.testing.assert_allclose(d.distancia_meta_ipc_pp,d.ipc_anual-3)
        np.testing.assert_allclose(d.distancia_referencia_nairu_pp,d.desocupacion-8.25)
        for frame in f.frames:
            self.assertFalse(frame.layout.shapes)
        self.assertLess(f.layout.xaxis.range[0],8.)
        self.assertGreater(f.layout.xaxis.range[1],8.5)

    def test_imacec_calendar_average_and_annual_ratio(self):
        d=load_imacec().set_index('fecha')
        raw=pd.read_csv(ROOT/'bcch_imacec_chile.csv',parse_dates=['fecha']).set_index('fecha')
        current=raw.loc['2026-05-01':'2026-07-01','imacec_original'].mean()
        previous=raw.loc['2025-05-01':'2025-07-01','imacec_original'].mean()
        self.assertAlmostEqual(d.loc['2026-06-01','imacec_promedio_anual'],100*(current/previous-1))
        self.assertTrue(pd.isna(d.iloc[-1].imacec_promedio_anual))
        final=load_imacec(alignment='final').set_index('fecha')
        self.assertAlmostEqual(final.loc['2026-07-01','imacec_promedio_anual'],d.loc['2026-06-01','imacec_promedio_anual'])
        with tempfile.TemporaryDirectory() as folder:
            raw.drop(pd.Timestamp('2025-06-01')).to_csv(Path(folder)/'bcch_imacec_chile.csv')
            with self.assertRaisesRegex(ValueError,'faltan meses'):
                load_imacec(folder)

    def test_duplicate_month_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for source in [*ROOT.glob('ine_*_chile.csv'), ROOT/'bcch_imacec_chile.csv']:
                (p/source.name).write_bytes(source.read_bytes())
            ir=pd.read_csv(p/'ine_ir_chile.csv')
            pd.concat([ir,ir.tail(1)]).to_csv(p/'ine_ir_chile.csv',index=False)
            with self.assertRaisesRegex(ValueError,'duplicadas'):
                load_data(p)

if __name__=='__main__': unittest.main()
