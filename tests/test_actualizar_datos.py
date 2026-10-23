"""Actualización íntegra, fallos de red, pérdida de cobertura y cortes futuros."""
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from actualizar_datos import actualizar, ROOT, SOURCES
from phillips import load_data, economic_summary


class ActualizarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'fuentes').mkdir()
        (self.root/'datos').mkdir()
        for name in SOURCES:
            shutil.copy2(ROOT/name, self.root/name)
        self.before = self.hashes()

    def hashes(self):
        return {name: hashlib.sha256((self.root/name).read_bytes()).hexdigest() for name in SOURCES}

    def ine(self, stage):
        for name in SOURCES[:3]:
            shutil.copy2(self.root/name, stage/name)

    def bcch(self, stage):
        for name in SOURCES[3:]:
            shutil.copy2(self.root/name, stage/name)

    def test_success_records_exact_sources(self):
        with patch('main.main',side_effect=self.ine), patch('actualizar_imacec.main',side_effect=self.bcch):
            manifest=actualizar(self.root)
        self.assertEqual(manifest['sha256'],self.before)
        self.assertTrue((self.root/'fuentes/actualizacion.json').is_file())

    def test_network_failure_preserves_all_sources(self):
        with patch('main.main',side_effect=self.ine), patch('actualizar_imacec.main',side_effect=TimeoutError('BCCh')):
            with self.assertRaises(TimeoutError): actualizar(self.root)
        self.assertEqual(self.hashes(),self.before)
        self.assertFalse((self.root/'fuentes/actualizacion.json').exists())

    def test_reduced_coverage_preserves_all_sources(self):
        import pandas as pd
        def truncated(stage):
            self.bcch(stage)
            path=stage/'datos/bcch_imacec_chile.csv'
            pd.read_csv(path).iloc[:-2].to_csv(path,index=False)
        with patch('main.main',side_effect=self.ine), patch('actualizar_imacec.main',side_effect=truncated):
            with self.assertRaisesRegex(ValueError,'cobertura|período común'): actualizar(self.root)
        self.assertEqual(self.hashes(),self.before)

    def test_replace_failure_rolls_back(self):
        original=Path.replace
        def fail(source,dest):
            if source.name=='ine_ir_chile.csv' and source.parent.parent.name.startswith('.actualizacion-'):
                raise OSError('disco')
            return original(source,dest)
        with patch('main.main',side_effect=self.ine), patch('actualizar_imacec.main',side_effect=self.bcch), patch.object(Path,'replace',fail):
            with self.assertRaises(OSError): actualizar(self.root)
        self.assertEqual(self.hashes(),self.before)

    def test_summary_extends_to_future_cutoff(self):
        import pandas as pd
        data,_,_=load_data(self.root)
        extra=data.tail(1).copy()
        extra['fecha']=pd.Timestamp('2027-02-01')
        extra['mes']='2027-02'
        summary=economic_summary(pd.concat([data,extra],ignore_index=True))
        self.assertEqual(summary['hasta'],'2027-02')
        self.assertEqual(summary['subperiodos'][-1]['hasta'],'2027-02')
        self.assertEqual(summary['subperiodos'][-1]['periodo'],'2024–2027')


if __name__=='__main__': unittest.main()
