"""Descarga pública BDE del BCCh; no requiere credenciales. Ejecutar voluntariamente."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parent
SERIES = {
    'imacec_original': ('CCNN2018_IMACEC_01_A', 'F032.IMC.IND.Z.Z.EP18.Z.Z.0.M'),
    'imacec_sa': ('CCNN2018_IMACEC_03_A', 'F032.IMC.IND.Z.Z.EP18.Z.Z.1.M'),
}
MONTHS = dict(zip('Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic'.split(), range(1, 13)))

def parse_observations(page):
    table = re.search(r'<table[^>]*id="listaObsHtmlAll"[^>]*>(.*?)</table>', page, re.S)
    if not table:
        raise ValueError('BDE: no se encontró la tabla de observaciones; revisar formato de origen')
    rows = re.findall(r'<tr><td>([A-Za-z]+)\.(\d{4})</td><td>([\d.,]+)</td></tr>', table[1])
    if not rows:
        raise ValueError('BDE: tabla vacía o valores no reconocidos')
    result = pd.Series({pd.Timestamp(int(y), MONTHS[m], 1): float(v.replace('.', '').replace(',', '.')) for m,y,v in rows})
    if len(result) != len(rows):
        raise ValueError('BDE: meses duplicados')
    result = result.sort_index()
    if not result.index.equals(pd.date_range(result.index.min(), result.index.max(), freq='MS')) or (result <= 0).any():
        raise ValueError('BDE: serie incompleta o índices no positivos')
    return result

def main():
    columns, metadata = {}, {}
    for name,(table,code) in SERIES.items():
        url=f'https://si3.bcentral.cl/siete/ES/Siete/Cuadro/CAP_CCNN/MN_CCNN76/{table}?idSerie={code}'
        raw=urllib.request.urlopen(url, timeout=60).read()
        page=raw.decode('utf-8')
        if code not in page:
            raise ValueError('Identificador de serie no encontrado')
        columns[name]=parse_observations(page)
        updated=re.search(r'Actualizado:\s*([^<]+)', page)
        metadata[name]={'codigo':code,'url':url,'actualizacion_bcch':updated[1].strip() if updated else None,
                        'sha256_respuesta':hashlib.sha256(raw).hexdigest()}
    data=pd.DataFrame(columns).rename_axis('fecha')
    if data.isna().any().any():
        raise ValueError('Las dos series tienen coberturas diferentes')
    data.to_csv(ROOT/'bcch_imacec_chile.csv', date_format='%Y-%m-%d', encoding='utf-8-sig')
    metadata.update(descargado_utc=datetime.now(timezone.utc).isoformat(),base='Promedio 2018=100',
                    precision='Índices publicados en la tabla web con un decimal; tasas calculadas son aproximaciones y pueden diferir de tasas oficiales calculadas con mayor precisión.',
                    transformacion='Color: variación interanual del promedio de tres índices originales centrado en el mes ENE. Panel: variación en 12 meses del índice desestacionalizado oficial, junto con IPC anual. Cierres de diciembre: promedio anual original IMACEC e IPC diciembre/diciembre; tamaño y color normalizados con las variaciones en 12 meses.')
    (ROOT/'fuentes'/'imacec_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(data.tail(14).to_string())

if __name__=='__main__': main()
