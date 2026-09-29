"""Ejecuta pruebas, cuaderno, informes y sitio con un único comando."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from curva_phillips.salidas import normalizar_fecha
from curva_phillips.rutas import NOTEBOOKS_DIR, REPORTS_DIR, RESULTS_DIR, SITE_DIR


def main() -> int:
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,"reconfigure"):
            stream.reconfigure(encoding="utf8")

    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fecha",default=None,help="Prefijo AAAAMMDD_HH_MM; por defecto fecha y hora local")
    p.add_argument("--ipc",choices=["original","sa"],default="original",help="IPC oficial o ajuste experimental X-13/SEATS")
    p.add_argument("--instalar-x13",action="store_true",help="Descarga X-13 antes del análisis")
    p.add_argument("--actualizar-datos",action="store_true",help="Actualiza INE e IMACEC antes de procesar")
    args=p.parse_args()
    try:
        args.fecha=normalizar_fecha(args.fecha)
    except ValueError:
        p.error("--fecha debe ser AAAAMMDD_HH_MM, por ejemplo 20260928_23_45")

    required=["pandas","numpy","plotly","matplotlib","statsmodels","nbformat","nbclient","nbconvert","ipykernel","notebook","requests","openpyxl","docx"]
    missing=[m for m in required if importlib.util.find_spec(m) is None]
    if missing:
        print("Faltan dependencias: "+", ".join(missing),file=sys.stderr)
        print(f'Execute: "{sys.executable}" -m pip install -r "{ROOT/"requirements.txt"}"',file=sys.stderr)
        return 1

    env=os.environ.copy()
    env["PHILLIPS_FECHA"]=args.fecha
    env["PHILLIPS_IPC"]=args.ipc
    env["PYTHONUTF8"]="1"

    for folder in (NOTEBOOKS_DIR,REPORTS_DIR,RESULTS_DIR):
        folder.mkdir(parents=True,exist_ok=True)

    if args.instalar_x13:
        subprocess.run([sys.executable,str(ROOT/"scripts"/"02_instalar_x13.py")],cwd=ROOT,env=env,check=True)
    if args.ipc=="sa":
        from curva_phillips.ipc_x13 import executable
        executable()

    steps=[]
    if args.actualizar_datos:
        steps.extend([
            ("Actualizar fuentes INE", [sys.executable,str(ROOT/"scripts"/"00_actualizar_datos_ine.py")]),
            ("Actualizar IMACEC BCCh", [sys.executable,str(ROOT/"scripts"/"01_actualizar_imacec.py")]),
        ])
    steps.extend([
        ("Pruebas", [sys.executable,"-m","unittest","discover","-s","tests","-v"]),
        ("Crear cuaderno", [sys.executable,str(ROOT/"scripts"/"03_generar_cuaderno.py")]),
        ("Ejecutar y verificar cuaderno", [sys.executable,str(ROOT/"scripts"/"04_verificar_cuaderno.py")]),
        ("Generar artículo", [sys.executable,str(ROOT/"scripts"/"05_generar_articulo.py")]),
        ("Generar análisis anual y mensual", [sys.executable,str(ROOT/"scripts"/"06_analisis_anual_mensual.py")]),
        ("Construir sitio estático", [sys.executable,str(ROOT/"scripts"/"07_construir_sitio.py")]),
    ])

    log={"fecha_edicion":args.fecha,"python":sys.executable,"ipc_ajuste":args.ipc,"pasos":[],"estado":"en_proceso"}
    prefix=args.fecha+("_ipc_sa" if args.ipc=="sa" else "")
    try:
        for label,command in steps:
            print(f"\n{label}",flush=True)
            start=time.monotonic()
            result=subprocess.run(command,cwd=ROOT,env=env,check=False)
            log["pasos"].append({"paso":label,"segundos":round(time.monotonic()-start,2),"codigo":result.returncode})
            if result.returncode:
                raise RuntimeError(f"Falló {label}; revisar el mensaje anterior.")

        expected=[
            NOTEBOOKS_DIR/f"{prefix}_Curva_de_Phillips.ipynb",
            RESULTS_DIR/f"{prefix}_phillips_animado.html",
            REPORTS_DIR/f"{prefix}_Articulo_LinkedIn_Curva_Phillips.docx",
            REPORTS_DIR/"informe_phillips_anual.html",
            REPORTS_DIR/"informe_phillips_mensual.html",
            REPORTS_DIR/"informe_phillips_dual.html",
            SITE_DIR/"index.html",
            SITE_DIR/"cuaderno_curva_phillips.html",
        ]
        missing_outputs=[str(p) for p in expected if not p.is_file() or not p.stat().st_size]
        if missing_outputs:
            raise RuntimeError("Faltan productos esperados: "+", ".join(missing_outputs))
        log["estado"]="correcto"
        log["archivos"]=[str(p.relative_to(ROOT)) for p in expected]
        print("\nProceso completo.")
        for path in expected:
            print(path.relative_to(ROOT))
        return 0
    except Exception as exc:
        log["estado"]="error"
        log["error"]=str(exc)
        raise
    finally:
        RESULTS_DIR.mkdir(parents=True,exist_ok=True)
        (RESULTS_DIR/f"{prefix}_ejecucion.json").write_text(json.dumps(log,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    raise SystemExit(main())
