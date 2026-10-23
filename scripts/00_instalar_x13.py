"""Entrada de ejecución para instalar_x13."""
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'codigo'))
sys.path.insert(0, str(ROOT / 'tests'))
runpy.run_module('instalar_x13', run_name='__main__')
