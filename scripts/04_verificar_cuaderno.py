"""Ejecuta verificar_cuaderno en la variante anual."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from curva_phillips.productos import verificar_cuaderno

if __name__ == "__main__":
    verificar_cuaderno()
