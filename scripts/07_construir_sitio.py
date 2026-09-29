"""Convierte el notebook ejecutado a HTML y prepara un sitio estático publicable."""
from __future__ import annotations

from html import escape
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from curva_phillips.rutas import NOTEBOOKS_DIR, REPORTS_DIR, RESULTS_DIR, SITE_DIR


def notebook_mas_reciente() -> Path:
    notebooks=sorted(NOTEBOOKS_DIR.glob("*Curva_de_Phillips.ipynb"), key=lambda p:p.stat().st_mtime)
    if not notebooks:
        raise FileNotFoundError("No hay un cuaderno generado en cuadernos_jupyter/. Ejecute primero 03 y 04.")
    return notebooks[-1]


def copiar_si_existe(origen: Path, destino: Path) -> None:
    if origen.is_file():
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)


def main() -> int:
    notebook=notebook_mas_reciente()
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR/".nojekyll").write_text("", encoding="utf-8")

    subprocess.run(
        [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "html",
            "--output", "cuaderno_curva_phillips.html",
            "--output-dir", str(SITE_DIR),
            str(notebook),
        ],
        cwd=ROOT,
        check=True,
    )
    copiar_si_existe(notebook, SITE_DIR/"cuaderno_curva_phillips.ipynb")

    copied=[]
    for pattern in ("*.html","*.docx","*.md"):
        for path in REPORTS_DIR.glob(pattern):
            target=SITE_DIR/path.name
            copiar_si_existe(path,target)
            copied.append(target.name)

    for pattern in ("*_phillips_animado.html","*_phillips_estatico.png"):
        matches=sorted(RESULTS_DIR.glob(pattern), key=lambda p:p.stat().st_mtime)
        if matches:
            target=SITE_DIR/matches[-1].name
            copiar_si_existe(matches[-1],target)
            copied.append(target.name)

    links=[
        ("Cuaderno ejecutado (HTML)","cuaderno_curva_phillips.html"),
        ("Cuaderno original (.ipynb)","cuaderno_curva_phillips.ipynb"),
    ]
    preferred=[
        ("Informe anual","informe_phillips_anual.html"),
        ("Informe mensual","informe_phillips_mensual.html"),
        ("Informe anual y mensual","informe_phillips_dual.html"),
    ]
    for label,name in preferred:
        if (SITE_DIR/name).exists():
            links.append((label,name))
    for name in sorted(set(copied)):
        if name not in {n for _,n in links}:
            links.append((name,name))

    items="\n".join(f'<li><a href="{escape(href)}">{escape(label)}</a></li>' for label,href in links)
    html=f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Curva de Phillips de Chile</title>
<style>
body{{font-family:Arial,sans-serif;max-width:920px;margin:40px auto;padding:0 20px;color:#172033}}
h1{{font-size:28px}}li{{margin:10px 0}}a{{color:#24527a}}.nota{{color:#5d6675}}
</style>
</head>
<body>
<h1>Curva de Phillips de Chile</h1>
<p class="nota">Productos generados automáticamente. El cuaderno HTML corresponde al notebook ejecutado de la última corrida.</p>
<ul>{items}</ul>
</body></html>"""
    (SITE_DIR/"index.html").write_text(html,encoding="utf-8")
    print("Sitio generado:", SITE_DIR/"index.html")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
