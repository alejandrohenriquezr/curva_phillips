"""Genera los informes anual y mensual y sus tablas de resultados."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from curva_phillips.analisis_dual import main

if __name__ == "__main__":
    raise SystemExit(main())
