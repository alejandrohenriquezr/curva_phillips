"""Ejecuta validación, cuaderno, gráficos y Word con un único comando."""
import argparse
import importlib.util
from salidas import normalizar_fecha
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent

def main():
    for stream in [sys.stdout,sys.stderr]:
        if hasattr(stream,"reconfigure"): stream.reconfigure(encoding="utf8")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fecha',default=None,help='Prefijo AAAAMMDD_HH_MM; por defecto fecha y hora local al iniciar')
    p.add_argument('--actualizar-datos',action='store_true',help='Descargar fuentes actuales antes de procesar; puede exigir revisar el análisis del informe')
    p.add_argument('--python-documento',default=sys.executable,help='Python con python-docx; por defecto el mismo intérprete')
    args=p.parse_args()
    try: args.fecha=normalizar_fecha(args.fecha)
    except ValueError: p.error('--fecha debe ser AAAAMMDD_HH_MM, por ejemplo 20260924_07_32')
    modules=['pandas','numpy','plotly','matplotlib','nbformat','nbclient','ipykernel','notebook','requests','openpyxl']
    if args.python_documento==sys.executable: modules.append('docx')
    missing=[m for m in modules if importlib.util.find_spec(m) is None]
    print('Python del proceso:',sys.executable,flush=True)
    if missing:
        print('Faltan dependencias: '+', '.join(missing),file=sys.stderr)
        print('Instálalas en este mismo Python y vuelve a ejecutar:\n& "'+sys.executable+'" -m pip install -r "'+str(ROOT/'requirements-completo.txt')+'"',file=sys.stderr)
        return 1
    env=os.environ.copy();env['PHILLIPS_FECHA']=args.fecha;env['PYTHONUTF8']='1'
    (ROOT/'resultados').mkdir(exist_ok=True)
    log={'fecha_edicion':args.fecha,'python':sys.executable,'pasos':[],'estado':'en_proceso'}
    steps=[]
    if args.actualizar_datos:steps.extend([('Descarga INE',[sys.executable,'main.py']),('Descarga BCCh',[sys.executable,'actualizar_imacec.py'])])
    steps.extend([('Pruebas',[sys.executable,'-m','unittest','test_phillips','-v']),
                  ('Crear cuaderno',[sys.executable,'crear_cuaderno.py']),
                  ('Ejecutar cuaderno y exportar gráficos',[sys.executable,'verificar_cuaderno.py']),
                  ('Generar Word y Markdown',[args.python_documento,'crear_articulo.py'])])
    try:
        for label,command in steps:
            print(f'\n{label}',flush=True); start=time.monotonic()
            result=subprocess.run(command,cwd=ROOT,env=env,check=False)
            log['pasos'].append({'paso':label,'segundos':round(time.monotonic()-start,2),'codigo':result.returncode})
            if result.returncode:raise RuntimeError(f'Falló {label}; revisar el mensaje anterior. No se marca esta edición como completa.')
        outputs=[ROOT/f'{args.fecha}_Curva_de_Phillips.ipynb',ROOT/'resultados'/f'{args.fecha}_phillips_animado.html',ROOT/'informe'/f'{args.fecha}_Articulo_LinkedIn_Curva_Phillips.docx',ROOT/'informe'/f'{args.fecha}_articulo_linkedin.md']
        for path in outputs:
            if not path.is_file() or not path.stat().st_size:raise RuntimeError(f'Falta resultado: {path}')
        log['estado']='correcto';log['archivos']=[str(x) for x in outputs]
        print('\nProceso completo. Revisar el Word antes de publicar.\n'+'\n'.join(str(x) for x in outputs))
    except Exception as exc:
        log['estado']='error';log['error']=str(exc);raise
    finally:
        (ROOT/'resultados'/f'{args.fecha}_ejecucion.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':sys.exit(main())
