import unittest
import numpy as np
import pandas as pd
from analisis_evolucion import resumen_etapas, secciones_evolucion
from phillips import load_data, economic_summary

class EvolucionTests(unittest.TestCase):
    def test_particion_exacta_y_medias(self):
        d,_,_=load_data()
        result=resumen_etapas(d)
        self.assertEqual(sum(e['n'] for e in result['etapas']),len(d))
        etapas={e['codigo']:e for e in result['etapas']}
        for code,mask in [('prepandemia',d.mes.le('2020-02')),('pandemia',d.mes.between('2020-03','2023-08')),('pospandemia',d.mes.ge('2023-09'))]:
            part=d.loc[mask]; e=etapas[code]
            self.assertEqual((e['desde'],e['hasta'],e['n']),(part.mes.iloc[0],part.mes.iloc[-1],len(part)))
            self.assertAlmostEqual(e['metricas']['desocupacion']['media'],part.desocupacion.mean())
            self.assertAlmostEqual(e['correlacion'],part.desocupacion.corr(part.ipc_anual))

    def test_cambios_de_nivel_no_suman_tasas(self):
        d,_,_=load_data()
        e=resumen_etapas(d)['etapas'][-1]
        part=d.loc[d.mes.ge('2023-09')]
        expected=100*(part.ir_indice_real.iloc[-1]/part.ir_indice_real.iloc[0]-1)
        self.assertAlmostEqual(e['metricas']['ir_indice_real']['cambio_nivel_pct'],expected)
        self.assertFalse(np.isclose(expected,part.ir_real_anual.sum()))

    def test_conclusiones_y_tasas_se_adaptan_al_corte(self):
        d,_,_=load_data()
        s=economic_summary(d)
        texts=secciones_evolucion(s)
        self.assertIn(('h','Conclusiones'),texts)
        self.assertTrue(any(s['hasta'] in text for _,text in texts))
        self.assertEqual(s['evolucion']['etapas'][-1]['hasta'],s['hasta'])
        base=d.loc[d.mes.eq('2020-02')].iloc[0]
        self.assertAlmostEqual(s['evolucion']['comparacion_previa']['imacec_nivel_cambio_pct'],100*(d.imacec_sa.iloc[-1]/base.imacec_sa-1))

if __name__=='__main__': unittest.main()
