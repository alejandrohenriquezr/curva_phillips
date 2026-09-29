"""Rutas únicas del proyecto."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "datos"
NOTEBOOKS_DIR = PROJECT_ROOT / "cuadernos_jupyter"
DOCS_DIR = PROJECT_ROOT / "documentacion"
REPORTS_DIR = PROJECT_ROOT / "informes"
RESULTS_DIR = PROJECT_ROOT / "resultados"
TOOLS_DIR = PROJECT_ROOT / "herramientas"
SITE_DIR = PROJECT_ROOT / "site"

for folder in (DATA_DIR, NOTEBOOKS_DIR, REPORTS_DIR, RESULTS_DIR):
    folder.mkdir(parents=True, exist_ok=True)
