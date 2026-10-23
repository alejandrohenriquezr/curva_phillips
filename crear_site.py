"""Prepara la edición actual para GitHub Pages y lectura local."""
import html
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from docx import Document
import json
from pathlib import Path
import shutil
import markdown
from autoria import NOMBRE, credito_html
from salidas import archivo, FECHA

ROOT=Path(__file__).resolve().parent

def construir():
    site=ROOT/'site_pages'
    (site/'resultados').mkdir(parents=True,exist_ok=True)
    summary=json.loads((ROOT/'resultados'/archivo('resumen_economico.json')).read_text(encoding='utf-8'))
    for name in ('phillips_animado.html','phillips_estatico.png','datos_phillips.csv','cobertura.csv','meses_excluidos.csv','fuentes_sha256.json'):
        shutil.copy2(ROOT/'resultados'/archivo(name),site/'resultados'/archivo(name))
    # El documento de LinkedIn se conserva localmente, fuera del sitio público.
    (site/'articulo_linkedin.docx').unlink(missing_ok=True)
    shutil.copy2(ROOT/'informe'/archivo('articulo_linkedin.md'),site/'articulo_linkedin.md')
    shutil.copy2(ROOT/archivo('Curva_de_Phillips.ipynb'),site/'Curva_de_Phillips.ipynb')
    (site/'.nojekyll').write_text('',encoding='utf-8')
    css='''body{margin:0;background:#f7f7f2;color:#172b4d;font:17px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:40px 24px}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}h2{margin-top:2em}a{color:#2166ac}nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin:28px 0}iframe{width:100%;height:1320px;border:1px solid #d7dfe4;background:white;border-radius:8px}img{max-width:100%;height:auto}.autoria{border-left:3px solid #2166ac;padding-left:18px;font-size:15px}.meta{color:#516477}article{max-width:850px}footer{margin-top:40px;font-size:14px}'''
    def page(title,body):
        return (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<meta name="author" content="{html.escape(NOMBRE,quote=True)}">'
                f'<title>{html.escape(title)} | {html.escape(NOMBRE)}</title><style>{css}</style></head>'
                f'<body><main>{body}<footer>{credito_html()}<a href="https://github.com/alejandrohenriquezr/curva_phillips">Código y fuentes reproducibles</a></footer></main></body></html>')
    plot='resultados/'+archivo('phillips_animado.html')
    body=(f'<h1>Curva de Phillips de Chile</h1>{credito_html()}'
          f'<p class="meta">{summary["desde"]} a {summary["hasta"]} · {summary["n"]} meses comunes · Edición {FECHA}</p>'
          '<p>Inflación, desocupación, remuneraciones reales y actividad. Análisis descriptivo con las últimas fuentes oficiales disponibles; la muestra termina en el último mes común completo.</p>'
          '<nav aria-label="Documentos"><a href="articulo.html">Leer el artículo</a>'
          '<a href="articulo_linkedin.md" download>Texto Markdown</a><a href="Curva_de_Phillips.ipynb" download>Cuaderno ejecutado</a>'
          f'<a href="{plot}">Abrir gráfico completo</a></nav>'
          f'<iframe src="{plot}" title="Gráfico interactivo de Phillips por {html.escape(NOMBRE)}" loading="lazy"></iframe>'
          '<p>El gráfico permite reproducir y seleccionar meses. La asociación observada no identifica causalidad ni constituye una recomendación monetaria.</p>'
          f'<a href="resultados/{archivo("datos_phillips.csv")}" download>Descargar datos del análisis</a>')
    (site/'index.html').write_text(page('Curva de Phillips de Chile',body),encoding='utf-8')
    text=(ROOT/'informe'/archivo('articulo_linkedin.md')).read_text(encoding='utf-8')
    article=markdown.markdown(text).replace('../resultados/','resultados/')
    (site/'articulo.html').write_text(page('Artículo de LinkedIn','<a href="index.html">Volver al gráfico</a><article>'+article+'</article>'),encoding='utf-8')
    validar(site)
    print('Sitio preparado y enlaces verificados:',site/'index.html')
    return site

def validar(site):
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(); self.paths=[]
        def handle_starttag(self,tag,attrs):
            self.paths.extend(value for key,value in attrs if key in ('href','src') and value)
    for name in ('index.html','articulo.html'):
        text=(site/name).read_text(encoding='utf-8')
        if NOMBRE not in text:
            raise ValueError(f'Falta autoría en {name}')
        parser=Links(); parser.feed(text)
        for link in parser.paths:
            url=urlsplit(link)
            if url.scheme or url.netloc or not url.path: continue
            dest=(site/unquote(url.path)).resolve()
            if not dest.is_relative_to(site.resolve()) or not dest.is_file():
                raise ValueError(f'Enlace local inválido en {name}: {link}')
    doc=Document(ROOT/'informe'/archivo('Articulo_LinkedIn_Curva_Phillips.docx'))
    if doc.core_properties.author != NOMBRE or not any(NOMBRE in p.text for p in doc.paragraphs):
        raise ValueError('El Word no conserva la firma visible y sus metadatos')

if __name__=='__main__': construir()
