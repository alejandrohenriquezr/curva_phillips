"""Entrada de ejecución para crear_articulo."""
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'codigo'))
sys.path.insert(0, str(ROOT / 'tests'))
runpy.run_module('crear_articulo', run_name='__main__')
