"""Valida y genera todos los productos anuales sin descargar datos externos."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src')
    env['PYTHONUTF8'] = '1'
    # Mantiene cachés y archivos de ejecución dentro del proyecto.
    for key, folder in [('JUPYTER_RUNTIME_DIR', '.runtime'), ('JUPYTER_CONFIG_DIR', '.jupyter'), ('IPYTHONDIR', '.ipython')]:
        env[key] = str(ROOT / folder)
        (ROOT / folder).mkdir(exist_ok=True)
    steps = [('Importar Excel', ['scripts/00_importar_anual.py']),
             ('Pruebas', ['-m', 'unittest', 'discover', '-s', 'tests', '-v']),
             ('Informe anual', ['scripts/06_analisis_anual.py']),
             ('Crear cuaderno', ['scripts/03_generar_cuaderno.py']),
             ('Ejecutar cuaderno', ['scripts/04_verificar_cuaderno.py']),
             ('Artículo', ['scripts/05_generar_articulo.py']),
             ('Sitio', ['scripts/07_construir_sitio.py']),
             ('Verificar productos', ['scripts/09_verificar_productos.py'])]
    log = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'estado': 'error', 'pasos': []}
    try:
        for name, command in steps:
            print(name, flush=True)
            start = time.monotonic()
            p = subprocess.run([sys.executable, *command], cwd=ROOT, env=env)
            log['pasos'].append({'paso': name, 'codigo': p.returncode, 'segundos': round(time.monotonic()-start, 2)})
            if p.returncode:
                raise RuntimeError('Falló: '+name)
        log['estado'] = 'correcto'
        return 0
    finally:
        (ROOT / 'resultados').mkdir(exist_ok=True)
        (ROOT / 'resultados/ejecucion_anual.json').write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    raise SystemExit(main())
