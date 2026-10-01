"""Informes, figuras y cuaderno que comparten la misma fuente anual."""
from __future__ import annotations

from html import escape
import shutil
import sys

import nbformat
import numpy as np
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

from .analisis_anual import NAIRU, NOTA_2026, analizar_anual, cargar_anual, exportar_resultados
from .articulo import secciones
from .rutas import PROJECT_ROOT, REPORTS_DIR, RESULTS_DIR, NOTEBOOKS_DIR, SITE_DIR

CUADERNO = NOTEBOOKS_DIR / "Curva_de_Phillips_anual.ipynb"
CSS = """body{font:17px/1.65 Georgia,serif;color:#172b3b;background:#f3f6f8;margin:0}
main{max-width:1100px;padding:40px;margin:auto;background:white}h1,h2{font-family:Arial,sans-serif}
h1{font-size:36px}h2{margin-top:40px}p{max-width:850px}table{border-collapse:collapse;font:13px/1.5 Arial,sans-serif;width:100%}
th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}.tabla{overflow:auto}a{color:#145d8a}
@media(max-width:700px){main{padding:18px}h1{font-size:28px}}"""


def documento_html(titulo, cuerpo):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(titulo)}</title><style>{CSS}</style></head><body><main>{cuerpo}</main></body></html>'


def texto_html(r):
    tags = {"title": "h1", "subtitle": "p", "h": "h2", "p": "p"}
    return "\n".join(f"<{tags[k]}>{escape(v)}</{tags[k]}>" for k, v in secciones(r))


def figura_anual(data, animada=False):
    data = data.sort_values(["desocupacion", "anio"]).reset_index(drop=True)
    bound = max(data.pib_anual.abs().max(), 0.1)
    def puntos(d):
        return go.Scatter(x=d.desocupacion, y=d.ipc_anual, mode="markers+text",
            text=[f"{year}{'*' if year == 2026 else ''}" for year in d.anio], textposition="top center",
            marker={"size": 13, "color": d.pib_anual, "colorscale": "RdBu", "cmin": -bound, "cmax": bound,
                    "symbol": ["diamond" if year == 2026 else "circle" for year in d.anio],
                    "colorbar": {"title": "PIB (%)"}},
            customdata=d[["anio", "pib_anual", "corte"]].to_numpy(),
            hovertemplate="Año %{customdata[0]}<br>Desempleo %{x:.3f}%<br>IPC %{y:.2f}%<br>PIB %{customdata[1]:.2f}%<br>%{customdata[2]}<extra></extra>")
    fig = go.Figure(puntos(data.iloc[:1] if animada else data))
    fig.update_layout(template="plotly_white", height=600, showlegend=False,
        title="Inflación y desempleo anual · *2026: corte julio–julio",
        xaxis={"title": "Tasa de desocupación (%)", "range": [data.desocupacion.min()-.6, data.desocupacion.max()+.6]},
        yaxis={"title": "IPC (%)", "range": [data.ipc_anual.min()-1, data.ipc_anual.max()+2]},
        margin={"t": 80, "b": 140 if animada else 60})
    fig.add_vline(x=NAIRU, line_dash="dot", annotation_text="Referencia 8,25%")
    if animada:
        fig.frames = [go.Frame(name=str(i), data=[puntos(data.iloc[:i+1])]) for i in range(len(data))]
        opts = {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}
        fig.update_layout(updatemenus=[{"type": "buttons", "y": -.17, "x": 0,
            "buttons": [
                {"label": "Reproducir", "method": "animate", "args": [None, {"fromcurrent": True, "frame": {"duration": 500, "redraw": True}, "transition": {"duration": 0}}]},
                {"label": "Pausa", "method": "animate", "args": [[None], opts]},
                {"label": "Reiniciar", "method": "animate", "args": [["0"], opts]}]}],
            sliders=[{"currentvalue": {"prefix": "Desocupación (%) · año: "}, "pad": {"t": 45},
                "steps": [{"label": f"{row.desocupacion:.2f} · {row.anio}", "method": "animate", "args": [[str(i)], opts]}
                          for i, row in data.iterrows()]}])
    return fig


def figura_aceleracion(r):
    d = r["data"].loc[lambda x: x.anio.between(1998, 2025)]
    fit = r["modelos"]["historica_nairu_restringida"]
    x = np.linspace(d.brecha_desempleo.min(), d.brecha_desempleo.max(), 100)
    fig = go.Figure(go.Scatter(x=d.brecha_desempleo, y=d.delta_ipc, mode="markers+text", text=d.anio,
                              textposition="top center", name="1998–2025"))
    fig.add_trace(go.Scatter(x=x, y=x*fit.params.iloc[0], mode="lines", name="Ajuste restringido histórico"))
    row = r["data"].iloc[-1]
    fig.add_trace(go.Scatter(x=[row.brecha_desempleo], y=[row.delta_ipc], mode="markers", marker={"symbol": "diamond", "size": 14},
                            name="2026: diferencia entre cortes distintos"))
    fig.update_layout(template="plotly_white", title="Cambio del IPC y brecha de desempleo", height=500,
                      xaxis_title="Desocupación menos 8,25% (pp)", yaxis_title="Diferencia del IPC (pp)")
    return fig


def generar_informe(r=None):
    r = r or analizar_anual(cargar_anual())
    exportar_resultados(r)
    animada = figura_anual(r["data"], True)
    animada.write_html(RESULTS_DIR / "phillips_anual_animado.html", include_plotlyjs=True)
    cuerpo = texto_html(r) + f"<script>{get_plotlyjs()}</script>"
    for fig in [figura_anual(r["data"]), animada, figura_aceleracion(r)]:
        cuerpo += fig.to_html(full_html=False, include_plotlyjs=False)
    for key, title in [("descriptivos", "Promedios por períodos"), ("comparacion", "Modelos y muestras efectivas"),
                       ("coeficientes", "Coeficientes e intervalos HAC"), ("estabilidad", "Ventanas de sensibilidad"),
                       ("robustez", "Referencia de desempleo y rezagos HAC"), ("influencia", "Exclusión de un año por vez")]:
        cuerpo += f"<h2>{title}</h2><div class='tabla'>" + r[key].to_html(index=False, float_format=lambda v: f"{v:.4f}") + "</div>"
    cuerpo += "<p>AIC y BIC sólo se comparan para la misma dependiente y muestra. El R² sin constante es no centrado. Las sensibilidades son exploratorias.</p>"
    (REPORTS_DIR / "informe_phillips_anual.html").write_text(documento_html("Curva de Phillips anual", cuerpo), encoding="utf-8")
    return r


def generar_cuaderno():
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    nb = nbformat.v4.new_notebook(cells=[
        md("# Curva de Phillips anual\n\n1997–2025 y corte interanual de julio de 2026. " + NOTA_2026),
        code('''from pathlib import Path
import sys
root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'src/curva_phillips/analisis_anual.py').exists()), None)
if root is None:
    raise RuntimeError('Abra el cuaderno dentro del repositorio o instale el paquete con pip install -e .')
sys.path.insert(0, str(root / 'src'))
from curva_phillips.analisis_anual import cargar_anual, analizar_anual, exportar_resultados
from curva_phillips.productos import figura_anual, figura_aceleracion, texto_html
from IPython.display import display, HTML
datos = cargar_anual()
resultado = analizar_anual(datos)
display(datos)'''),
        code("display(HTML(texto_html(resultado)))"),
        md("## Modelos comparables\nTodos los modelos históricos usan 1998–2025; la extensión a 2026 es una sensibilidad. No comparar AIC/BIC entre distintas dependientes o muestras."),
        code("display(resultado['comparacion'])\ndisplay(resultado['coeficientes'])"),
        code("display(HTML(figura_anual(datos, animada=True).to_html(full_html=False, include_plotlyjs=True)))"),
        code("display(HTML(figura_aceleracion(resultado).to_html(full_html=False, include_plotlyjs=True)))"),
        md("## Estabilidad y límites\nLas exclusiones preservan los rezagos calculados en la cronología original. Estos contrastes exploratorios no identifican causalidad ni prueban cambios estructurales."),
        code("display(resultado['estabilidad'])\ndisplay(resultado['robustez'])\ndisplay(resultado['influencia'])\nexportar_resultados(resultado)"),
    ], metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
    nbformat.write(nb, CUADERNO)


def verificar_cuaderno():
    from nbclient import NotebookClient
    from jupyter_client import KernelManager
    nb = nbformat.read(CUADERNO, as_version=4)
    nbformat.validate(nb)
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    NotebookClient(nb, timeout=600, km=manager, resources={"metadata": {"path": str(NOTEBOOKS_DIR)}}).execute()
    nbformat.write(nb, CUADERNO)


def generar_articulo(r=None):
    from docx import Document
    from docx.shared import Cm, Pt, RGBColor
    r = r or analizar_anual(cargar_anual())
    contenido = secciones(r)
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2)
    sec.left_margin = sec.right_margin = Cm(2.4)
    for name in ["Normal", "Title", "Subtitle", "Heading 1"]:
        doc.styles[name].font.name = "Calibri"
        doc.styles[name].font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(11)
    doc.styles["Normal"].paragraph_format.space_after = Pt(8)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.12
    for kind, text in contenido:
        doc.add_paragraph(text, style={"title": "Title", "subtitle": "Subtitle", "h": "Heading 1", "p": "Normal"}[kind])
    doc.save(REPORTS_DIR / "Articulo_LinkedIn_Phillips_anual.docx")
    (REPORTS_DIR / "Articulo_LinkedIn_Phillips_anual.md").write_text("\n\n".join(
        ("# " if k == "title" else "## " if k == "h" else "") + text for k, text in contenido)+"\n", encoding="utf-8")


def construir_sitio():
    from nbconvert import HTMLExporter
    SITE_DIR.mkdir(exist_ok=True)
    # Copias explícitas: nunca incorpora salidas históricas de otras ediciones.
    for folder, name in [(REPORTS_DIR, "informe_phillips_anual.html"), (REPORTS_DIR, "Articulo_LinkedIn_Phillips_anual.docx"),
                         (RESULTS_DIR, "phillips_anual_animado.html"), (NOTEBOOKS_DIR, CUADERNO.name)]:
        shutil.copyfile(folder / name, SITE_DIR / name)
    html, _ = HTMLExporter().from_notebook_node(nbformat.read(CUADERNO, as_version=4))
    (SITE_DIR / "cuaderno_curva_phillips.html").write_text(html, encoding="utf-8")
    links = [("informe_phillips_anual.html", "Informe económico y social"), ("phillips_anual_animado.html", "Animación por desempleo"),
             ("Articulo_LinkedIn_Phillips_anual.docx", "Artículo Word"), (CUADERNO.name, "Cuaderno Jupyter"),
             ("cuaderno_curva_phillips.html", "Cuaderno ejecutado en HTML")]
    body = "<h1>Curva de Phillips anual en Chile</h1><p>1997–2025 y corte interanual de julio de 2026.</p><ul>"
    body += "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in links)+"</ul>"
    (SITE_DIR / "index.html").write_text(documento_html("Análisis anual", body), encoding="utf-8")
