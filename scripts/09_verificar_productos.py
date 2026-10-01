"""Verifica integridad de productos finales y enlaces locales."""
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

import nbformat

ROOT = Path(__file__).resolve().parents[1]
expected = ['cuadernos_jupyter/Curva_de_Phillips_anual.ipynb', 'informes/informe_phillips_anual.html',
            'informes/Articulo_LinkedIn_Phillips_anual.docx', 'informes/Articulo_LinkedIn_Phillips_anual.md',
            'resultados/phillips_anual_animado.html', 'resultados/resumen_modelos.json',
            'site/index.html', 'site/cuaderno_curva_phillips.html']
for name in expected:
    path = ROOT/name
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError('Producto faltante: '+name)
nb = nbformat.read(ROOT/expected[0], as_version=4)
nbformat.validate(nb)
for cell in nb.cells:
    if cell.cell_type == 'code':
        assert cell.execution_count is not None, 'Celda sin ejecutar'
        assert not any(o.output_type == 'error' for o in cell.outputs), 'Error en cuaderno'
for href in re.findall(r'href="([^"]+)"', (ROOT/'site/index.html').read_text(encoding='utf-8')):
    assert (ROOT/'site'/href).is_file(), 'Enlace roto: '+href
with zipfile.ZipFile(ROOT/expected[2]) as archive:
    assert archive.testzip() is None
    xml = ET.fromstring(archive.read('word/document.xml'))
    text = ''.join(xml.itertext())
    assert '2026' in text and 'dimensión social' in text
summary = json.loads((ROOT/'resultados/resumen_modelos.json').read_text(encoding='utf-8'))
assert len(summary['modelos']) == 12
assert summary['observacion_2026']['corte'] == 'julio 2026 vs julio 2025'
print('Productos anuales verificados: cuaderno ejecutado, Word, HTML, JSON y enlaces.')
