"""Nombres reproducibles de los archivos de cada edición."""
import os
from datetime import datetime
FECHA=os.environ.get('PHILLIPS_FECHA','20260924')
if len(FECHA)!=8 or not FECHA.isdigit():
    raise ValueError('PHILLIPS_FECHA debe ser AAAAMMDD')
datetime.strptime(FECHA,'%Y%m%d')
def archivo(nombre): return f'{FECHA}_{nombre}'
