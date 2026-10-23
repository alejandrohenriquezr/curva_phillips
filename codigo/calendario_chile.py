"""Feriados nacionales chilenos para regresión mensual de calendario."""
import holidays
import pandas as pd

def calendario(fecha):
    meses=pd.date_range(fecha.min(),fecha.max()+pd.DateOffset(months=36),freq='MS')
    feriados=holidays.country_holidays('CL',years=range(meses[0].year,meses[-1].year+1),language='es',categories=holidays.PUBLIC)
    eventos=[]; rows=[]
    for mes in meses:
        dias=pd.date_range(mes,mes+pd.offsets.MonthEnd(0),freq='D')
        habiles=sum(d.weekday()<5 and d.date() not in feriados for d in dias)
        festivos=sum(d.weekday()<5 and d.date() in feriados for d in dias)
        rows.append(dict(fecha=mes,dias_mes=len(dias),dias_habiles=habiles,feriados_lunes_viernes=festivos))
        for dia in dias:
            if dia.date() in feriados: eventos.append(dict(fecha=dia.date().isoformat(),nombre=feriados[dia.date()],dia_semana=dia.weekday()))
    tabla=pd.DataFrame(rows)
    # Centrado por mes sobre la muestra observada, conservado para las extensiones.
    observada=tabla.fecha.le(fecha.max())
    medias=tabla.loc[observada].groupby(tabla.loc[observada,'fecha'].dt.month).feriados_lunes_viernes.mean()
    tabla['feriados_centrados']=tabla.feriados_lunes_viernes-tabla.fecha.dt.month.map(medias)
    return tabla,pd.DataFrame(eventos)
