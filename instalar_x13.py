"""Instala el ejecutable oficial X-13 v1.1 build 62 (Windows o Linux)."""
from pathlib import Path
import hashlib, io, json, platform, tarfile, urllib.request, zipfile
ROOT=Path(__file__).resolve().parent

def instalar():
    windows=platform.system()=='Windows'
    if platform.system() not in ('Windows','Linux'):
        raise RuntimeError('Configura X13_EXECUTABLE con un ejecutable compatible con tu sistema.')
    base='https://www2.census.gov/software/x-13arima-seats/x13as/'
    url=base+('windows/program-archives/x13as_ascii-v1-1-b62.zip' if windows else 'unix-linux/program-archives/x13as_ascii-v1-1-b62.tar.gz')
    data=urllib.request.urlopen(url,timeout=120).read()
    if windows:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=[n for n in z.namelist() if n.endswith('/x13as_ascii.exe')]
            if len(names)!=1: raise RuntimeError('Archivo oficial inesperado')
            binary=z.read(names[0])
    else:
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as z:
            members=[m for m in z.getmembers() if m.isfile() and Path(m.name).name in ('x13as_ascii','x13as_ascii.exe')]
            if len(members)!=1: raise RuntimeError('Archivo oficial inesperado')
            binary=z.extractfile(members[0]).read()
    folder=ROOT/'herramientas'/'x13';folder.mkdir(parents=True,exist_ok=True)
    exe=folder/('x13as_ascii.exe' if windows else 'x13as_ascii')
    exe.write_bytes(binary);exe.chmod(0o755)
    (folder/'instalacion.json').write_text(json.dumps({'url':url,'version':'1.1 build 62','archivo_sha256':hashlib.sha256(data).hexdigest(),'ejecutable_sha256':hashlib.sha256(binary).hexdigest()},indent=2),encoding='utf8')
    print('X-13 instalado:',exe)
    return exe

if __name__=='__main__':instalar()
