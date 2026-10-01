"""Ejecuta generar_informe en la variante anual."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from curva_phillips.productos import generar_informe

if __name__ == "__main__":
    generar_informe()
