"""Descarga las tres fuentes INE en la carpeta del proyecto; falla ante cualquier error."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from curva_phillips.extractors.ipc_extractor import IPCExtractor
from curva_phillips.extractors.ene_extractor import ENEExtractor
from curva_phillips.extractors.ir_extractor import IRExtractor

DATA_DIR=ROOT/"datos"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def main():
    pending=[]
    for cls,name in [(IPCExtractor,'ine_ipc_chile.csv'),(ENEExtractor,'ine_ene_chile.csv'),(IRExtractor,'ine_ir_chile.csv')]:
        data=cls().run()
        if data.empty:raise ValueError(f'Fuente vacía: {name}')
        pending.append((name,data))
    # No sustituir ninguna fuente si falla una descarga o transformación.
    for name,data in pending:
        path=DATA_DIR/name;temp=path.with_suffix('.tmp.csv')
        data.to_csv(temp,index=False,encoding='utf-8-sig');temp.replace(path)
        print(f'Guardado: {path}')

if __name__=='__main__':main()
