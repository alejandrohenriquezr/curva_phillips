"""Una firma compartida por HTML, Word y Markdown."""
import html
import json
from pathlib import Path

AUTOR = json.loads((Path(__file__).resolve().parent/'autor.json').read_text(encoding='utf-8'))
NOMBRE = AUTOR['nombre']
FIRMA = f'Autor: {NOMBRE}'

def credito_html():
    return (f'<p class="autoria"><strong>{html.escape(FIRMA)}</strong><br>'
            f'{html.escape(AUTOR["nota"])}</p>')
