"""Descarga las tres fuentes INE en la carpeta del proyecto; falla ante cualquier error."""
from pathlib import Path
from extractors.ipc_extractor import IPCExtractor
from extractors.ene_extractor import ENEExtractor
from extractors.ir_extractor import IRExtractor

ROOT=Path(__file__).resolve().parent

def main():
    pending=[]
    for cls,name in [(IPCExtractor,'ine_ipc_chile.csv'),(ENEExtractor,'ine_ene_chile.csv'),(IRExtractor,'ine_ir_chile.csv')]:
        data=cls().run()
        if data.empty:raise ValueError(f'Fuente vacía: {name}')
        pending.append((name,data))
    # No sustituir ninguna fuente si falla una descarga o transformación.
    for name,data in pending:
        path=ROOT/name;temp=path.with_suffix('.tmp.csv')
        data.to_csv(temp,index=False,encoding='utf-8-sig');temp.replace(path)
        print(f'Guardado: {path}')

if __name__=='__main__':main()
