"""Un mismo sello de fecha y hora para todos los archivos de una ejecución."""
import os
from datetime import datetime

def normalizar_fecha(value=None):
    if not value:
        return datetime.now().strftime('%Y%m%d_%H_%M')
    if len(value)==8:
        datetime.strptime(value,'%Y%m%d')
        return value+datetime.now().strftime('_%H_%M')
    datetime.strptime(value,'%Y%m%d_%H_%M')
    if len(value)!=14:
        raise ValueError('Usa AAAAMMDD_HH_MM')
    return value

FECHA=normalizar_fecha(os.environ.get('PHILLIPS_FECHA'))
os.environ['PHILLIPS_FECHA']=FECHA

def archivo(nombre):
    mode=os.environ.get('PHILLIPS_IPC','original')
    if mode not in ('original','sa'):raise ValueError('PHILLIPS_IPC debe ser original o sa')
    suffix='_ipc_sa' if mode=='sa' else ''
    return f'{FECHA}{suffix}_{nombre}'
