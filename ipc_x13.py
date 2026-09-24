"""IPC experimental desestacionalizado con el ejecutable oficial X-13 y SEATS.

Se ajustan niveles positivos completos; las tasas se calculan después.
No se sobrescribe el IPC del INE ni se usa una alternativa silenciosa a X-13.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess
import numpy as np
import pandas as pd
from salidas import archivo
ROOT=Path(__file__).resolve().parent


def executable():
    configured=os.environ.get('X13_EXECUTABLE')
    path=Path(configured) if configured else ROOT/'herramientas'/'x13'/('x13as_ascii.exe' if os.name=='nt' else 'x13as_ascii')
    if not path.is_file():
        raise FileNotFoundError('Falta X-13. Ejecuta python instalar_x13.py o configura X13_EXECUTABLE con la ruta del ejecutable oficial.')
    return path.resolve()


def read_ipc(root=ROOT):
    raw=pd.read_csv(Path(root)/'ine_ipc_chile.csv')
    raw=raw.loc[raw['Glosa'].str.strip().eq('IPC General')].copy()
    raw['fecha']=pd.to_datetime(dict(year=raw['Año'],month=raw['Mes'],day=1))
    raw=raw.sort_values('fecha').reset_index(drop=True)
    if raw.empty or raw.fecha.duplicated().any():raise ValueError('IPC: meses ausentes o duplicados')
    if not raw.fecha.equals(pd.Series(pd.date_range(raw.fecha.min(),raw.fecha.max(),freq='MS'),name='fecha')):
        raise ValueError('IPC: faltan meses; X-13 exige continuidad mensual')
    level=pd.to_numeric(raw['Índice'],errors='raise')
    if len(raw)<60 or not np.isfinite(level).all() or (level<=0).any():
        raise ValueError('IPC: se necesitan al menos 60 niveles mensuales positivos y finitos')
    return pd.DataFrame({'fecha':raw.fecha,'ipc_indice_original':level,'ipc_mensual_original':raw['Variación Mensual (%)'],'ipc_anual_original':raw['Variación 12 Meses (%)']})


def specification(d):
    start=d.fecha.iloc[0]
    values='\n'.join(f'{v:.12g}' for v in d.ipc_indice_original)
    return f'''series {{ title="IPC Chile experimental" start={start.year}.{start.month} period=12 data=(
{values}
) }}
transform {{ function=log }}
automdl {{ }}
outlier {{ types=(ao ls tc) }}
forecast {{ maxlead=36 }}
check {{ }}
seats {{ save=(s10 s11 s12 s13) }}
'''


def read_component(path):
    d=pd.read_csv(path,sep=r'\s+',skiprows=2,header=None,names=['fecha','valor'])
    d['fecha']=pd.to_datetime(d.fecha.astype(str),format='%Y%m')
    if d.fecha.duplicated().any():raise ValueError('X-13 devolvió fechas duplicadas')
    return d.set_index('fecha').valor


def ajustar_ipc(root=ROOT):
    root=Path(root);d=read_ipc(root);exe=executable();spec=specification(d)
    source_hash=hashlib.sha256((root/'ine_ipc_chile.csv').read_bytes()).hexdigest()
    exe_hash=hashlib.sha256(exe.read_bytes()).hexdigest()
    key=hashlib.sha256((source_hash+exe_hash+spec).encode()).hexdigest()
    cache=root/'.cache_x13'/key;cache.mkdir(parents=True,exist_ok=True)
    if not (cache/'completo.json').exists():
        (cache/'ipc.spc').write_text(spec,encoding='ascii')
        process=subprocess.run([str(exe),'ipc'],cwd=cache,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
        (cache/'ipc.stdout.txt').write_text(process.stdout+'\n'+process.stderr,encoding='utf8')
        errors=(cache/'ipc.err').read_text(errors='replace') if (cache/'ipc.err').exists() else ''
        if process.returncode or re.search(r'\bERROR:',errors) or not (cache/'ipc.s11').is_file():
            raise RuntimeError(f'Falló X-13; revisar {cache}/ipc.err. '+errors[-2000:])
        report=(cache/'ipc.out').read_text(errors='replace')
        model=re.search(r'Final automatic model choice\s*:\s*([^\n]+)',report)
        meta={'metodo':'X-13ARIMA-SEATS / SEATS','version':'1.1 build 62 (instalador del proyecto; verificar cabecera de ipc.out si se usa otro ejecutable)',
              'fuente_sha256':source_hash,'ejecutable_sha256':exe_hash,'spec_sha256':hashlib.sha256(spec.encode()).hexdigest(),
              'modelo_regarima':model.group(1).strip() if model else 'Consultar ipc.out',
              'desde':d.fecha.iloc[0].strftime('%Y-%m'),'hasta':d.fecha.iloc[-1].strftime('%Y-%m'),'n':len(d),
              'transformacion':'log','atipicos':'AO LS TC automáticos','calendario':'Sin regresores de días hábiles ni feriados chilenos',
              'advertencias':errors.strip(),'experimental':True,
              'nota':'Estimación retrospectiva de muestra completa; revisable al añadir datos. No es una serie oficial del INE.'}
        # Escribir el marcador solo si la serie final es válida.
        sa=read_component(cache/'ipc.s11').reindex(d.fecha)
        if not np.isfinite(sa).all() or (sa<=0).any():raise ValueError('X-13 produjo niveles inválidos')
        (cache/'completo.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    meta=json.loads((cache/'completo.json').read_text(encoding='utf8'))
    for suffix,col in [('s11','ipc_indice_sa'),('s12','ipc_tendencia'),('s10','ipc_factor_estacional'),('s13','ipc_irregular')]:
        d[col]=read_component(cache/f'ipc.{suffix}').reindex(d.fecha).to_numpy()
    if not np.isfinite(d.ipc_indice_sa).all() or (d.ipc_indice_sa<=0).any():raise ValueError('Salida X-13 incompleta')
    d['ipc_mensual_sa']=100*(d.ipc_indice_sa/d.ipc_indice_sa.shift(1)-1)
    d['ipc_anual_sa']=100*(d.ipc_indice_sa/d.ipc_indice_sa.shift(12)-1)
    d['ipc_anual_original_calculada']=100*(d.ipc_indice_original/d.ipc_indice_original.shift(12)-1)
    # Se preservan las tasas publicadas y sus faltantes: no se sustituyen por ratios redondeados.
    out=root/'resultados';out.mkdir(exist_ok=True)
    audit=out/archivo('x13');audit.mkdir(exist_ok=True)
    for p in cache.iterdir():
        if p.is_file():shutil.copy2(p,audit/p.name)
    d.to_csv(out/archivo('ipc_comparacion.csv'),index=False,encoding='utf-8-sig')
    (out/archivo('ipc_x13_metadatos.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    return d,meta


if __name__=='__main__':
    data,metadata=ajustar_ipc()
    print(data.tail(6).to_string(index=False))
    print('Modelo:',metadata['modelo_regarima'])
    print(metadata['advertencias'])
