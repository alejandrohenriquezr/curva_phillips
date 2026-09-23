"""Análisis reproducible de los CSV del INE y BCCh; no descarga ni modifica las fuentes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
REFERENCIAS = json.loads((ROOT/'referencias_macro.json').read_text(encoding='utf-8-sig'))
META_INFLACION = float(REFERENCIAS['meta_inflacion_pct'])
NAIRU_RANGO = tuple(float(v) for v in REFERENCIAS['nairu_rango_pct'])
NAIRU_REFERENCIA = sum(NAIRU_RANGO) / 2
# Esta referencia fija es el punto medio del rango histórico, no una NAIRU de 2026.

MESES = dict(zip(['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'], range(1,13)))
COL_U = 'Tasa de desocupación [1] - tasa (%)'
ACTIVITY_COLORS = [[0, '#d97706'], [.5, '#f7f7f2'], [1, '#2166ac']]

def load_imacec(root=ROOT, alignment='central'):
    """Promedio de niveles, luego variación anual; nunca promedio de tasas."""
    d=unique_months(pd.read_csv(Path(root)/'bcch_imacec_chile.csv',parse_dates=['fecha']), 'IMACEC')
    if not d.fecha.equals(pd.Series(pd.date_range(d.fecha.min(),d.fecha.max(),freq='MS'),name='fecha')):
        raise ValueError('IMACEC: faltan meses; no se permite desplazar el rezago calendario')
    if not np.isfinite(d[['imacec_original','imacec_sa']]).all().all() or (d[['imacec_original','imacec_sa']]<=0).any().any():
        raise ValueError('IMACEC: índices no finitos o no positivos')
    d['imacec_promedio_3m']=d.imacec_original.rolling(3,center=alignment=='central',min_periods=3).mean()
    d['imacec_promedio_anual']=100*(d.imacec_promedio_3m/d.imacec_promedio_3m.shift(12)-1)
    d['imacec_sa_mensual']=100*(d.imacec_sa/d.imacec_sa.shift(1)-1)
    d['imacec_inicio_promedio']=d.fecha-pd.DateOffset(months=1 if alignment=='central' else 2)
    d['imacec_fin_promedio']=d.fecha+pd.DateOffset(months=1 if alignment=='central' else 0)
    return d

def unique_months(df, name):
    if df.fecha.isna().any() or df.fecha.duplicated().any():
        raise ValueError(f'{name}: fechas ausentes o duplicadas')
    return df.sort_values('fecha').reset_index(drop=True)

def load_data(root=ROOT, alignment='central'):
    if alignment not in ('central', 'final'):
        raise ValueError('alignment debe ser central o final')
    root = Path(root)
    ipc = pd.read_csv(root/'ine_ipc_chile.csv')
    ipc = ipc.loc[ipc.Glosa.str.strip().eq('IPC General')].copy()
    ipc['fecha'] = pd.to_datetime(dict(year=ipc['Año'], month=ipc['Mes'], day=1))
    ipc = unique_months(ipc, 'IPC').rename(columns={'Variación 12 Meses (%)':'ipc_anual'})
    ir = pd.read_csv(root/'ine_ir_chile.csv')
    ir['fecha'] = pd.to_datetime(dict(year=ir['año'], month=ir['mes'], day=1))
    ir = unique_months(ir, 'IR').rename(columns={'var_12':'ir_real_anual', 'estado':'estado_ir'})
    # El IR ya es real: NO se vuelve a deflactar. Contraste por mes calendario.
    lag = ir.set_index('fecha')['índice'].copy()
    lag.index = lag.index + pd.DateOffset(years=1)
    computed = 100 * (ir.set_index('fecha')['índice'] / lag - 1)
    check = ir.set_index('fecha')['ir_real_anual'].subtract(computed).dropna()
    if not check.empty and check.abs().max() > 0.11:
        raise ValueError('IR anual inconsistente con los niveles a 12 meses')
    ene = pd.read_csv(root/'ine_ene_chile.csv')
    parts = ene['mes_año'].str.split(' ', expand=True)
    ene['fecha'] = pd.to_datetime(dict(year=parts[1].astype(int), month=parts[0].map(MESES), day=1))
    ene = unique_months(ene, 'ENE').rename(columns={COL_U:'desocupacion'})
    # Los CSV atribuyen ENE al mes central; final desplaza un mes hacia adelante.
    ene['fecha_central_ene'] = ene.fecha
    ene['fecha_final_ene'] = ene.fecha + pd.DateOffset(months=1)
    if alignment == 'final':
        ene['fecha'] = ene.fecha_final_ene
    imacec=load_imacec(root,alignment)
    parts_data = [('IPC',ipc,'ipc_anual'), ('IR real',ir,'ir_real_anual'), ('ENE',ene,'desocupacion'), ('IMACEC original',imacec,'imacec_original'), ('IMACEC desestacionalizado',imacec,'imacec_sa'), ('IMACEC promedio 3m interanual',imacec,'imacec_promedio_anual')]
    coverage = pd.DataFrame([{'serie':name,'desde':d.fecha.min().strftime('%Y-%m'),'hasta':d.fecha.max().strftime('%Y-%m'),'filas':len(d),'faltantes':int(d[col].isna().sum())} for name,d,col in parts_data])
    union = ipc[['fecha','ipc_anual']].merge(ir[['fecha','ir_real_anual','estado_ir']],on='fecha',how='outer',validate='one_to_one').merge(ene[['fecha','desocupacion','Trimestre','fecha_central_ene','fecha_final_ene']],on='fecha',how='outer',validate='one_to_one').sort_values('fecha')
    union=union.merge(imacec,on='fecha',how='outer',validate='one_to_one').sort_values('fecha')
    required=['ipc_anual','ir_real_anual','desocupacion','imacec_promedio_anual','imacec_sa']
    missing = union[union[required].isna().any(axis=1)].copy()
    data = union.dropna(subset=required).reset_index(drop=True)
    if len(data)<2:
        raise ValueError('No hay suficientes meses comunes completos')
    values = data[required].to_numpy()
    if not np.isfinite(values).all() or not data.desocupacion.between(0,100).all():
        raise ValueError('Valores no finitos o desocupación fuera de rango')
    expected = pd.date_range(data.fecha.min(),data.fecha.max(),freq='MS')
    if not data.fecha.equals(pd.Series(expected,name='fecha')):
        raise ValueError('Hay huecos en el período común; revisar antes de animar')
    data['mes'] = data.fecha.dt.strftime('%Y-%m')
    data['ir_magnitud'] = data.ir_real_anual.abs()
    data['ir_signo'] = np.where(data.ir_real_anual>=0,'Aumento','Caída')
    data['alineacion_ene']=alignment
    data['distancia_meta_ipc_pp'] = data.ipc_anual - META_INFLACION
    data['distancia_referencia_nairu_pp'] = data.desocupacion - NAIRU_REFERENCIA
    return data, coverage, missing

def build_figure(data):
    d=data.reset_index(drop=True)
    sizeref=2*max(float(d.ir_magnitud.max()),1e-9)/(48**2)
    bound=max(float(d.imacec_promedio_anual.abs().max()),.1)
    dates=d.fecha.dt.strftime('%Y-%m-%d').tolist()
    def limits(s):
        margin=max(float(s.max()-s.min())*.18,.25)
        return [float(s.min()-margin),float(s.max()+margin)]
    panel_range=limits(d.imacec_sa)
    custom=[[r.mes,str(r.Trimestre),float(r.ir_real_anual),str(r.estado_ir),float(r.imacec_promedio_anual),float(r.imacec_sa),r.imacec_inicio_promedio.strftime('%Y-%m'),r.imacec_fin_promedio.strftime('%Y-%m'),r.alineacion_ene] for r in d.itertuples()]
    hover=('<b>%{customdata[0]}</b><br>Desocupación: %{x:.2f}%<br>IPC anual: %{y:.2f}%'
           '<br>IR real anual: %{customdata[2]:+.2f}%<br>IMACEC promedio 3m interanual: %{customdata[4]:+.2f}%'
           '<br>Ventana IMACEC: %{customdata[6]} a %{customdata[7]}<br>IMACEC SA: %{customdata[5]:.1f}'
           '<br>ENE: %{customdata[1]} · alineación %{customdata[8]}<br>Estado IR: %{customdata[3]}<extra></extra>')
    def traces(i):
        return [
            go.Scatter(x=d.desocupacion.iloc[:i+1].tolist(),y=d.ipc_anual.iloc[:i+1].tolist(),mode='lines+markers',line=dict(color='#a1aab5',width=1.5),marker=dict(size=d.ir_magnitud.iloc[:i+1].tolist(),sizemode='area',sizeref=sizeref,color=d.imacec_promedio_anual.iloc[:i+1].tolist(),coloraxis='coloraxis',opacity=.85,line=dict(color='#64748b',width=.6)),customdata=custom[:i+1],hovertemplate=hover,name='Rastro'),
            go.Scatter(x=[float(d.desocupacion.iloc[i])],y=[float(d.ipc_anual.iloc[i])],mode='markers',marker=dict(size=[float(d.ir_magnitud.iloc[i])],sizemode='area',sizeref=sizeref,color=[float(d.imacec_promedio_anual.iloc[i])],coloraxis='coloraxis',line=dict(color='#0f172a',width=2.5)),customdata=[custom[i]],hovertemplate=hover,name='Mes actual'),
            go.Scatter(x=[float(d.desocupacion.iloc[i])],y=[float(d.ipc_anual.iloc[i])],mode='markers',marker=dict(size=4,color='#0f172a'),hoverinfo='skip'),
            go.Scatter(x=dates,y=d.imacec_sa.tolist(),xaxis='x2',yaxis='y2',mode='lines',line=dict(color='#cbd5e1',width=2),hovertemplate='%{x|%Y-%m}<br>IMACEC SA: %{y:.1f}<extra></extra>',name='Contexto completo'),
            go.Scatter(x=dates[:i+1],y=d.imacec_sa.iloc[:i+1].tolist(),xaxis='x2',yaxis='y2',mode='lines',line=dict(color='#334155',width=2),hovertemplate='%{x|%Y-%m}<br>IMACEC SA: %{y:.1f}<extra></extra>',name='Recorrido IMACEC'),
            go.Scatter(x=[dates[i]],y=[float(d.imacec_sa.iloc[i])],xaxis='x2',yaxis='y2',mode='markers',marker=dict(size=10,color=[float(d.imacec_promedio_anual.iloc[i])],coloraxis='coloraxis',line=dict(color='#0f172a',width=1)),hovertemplate='%{x|%Y-%m}<br>IMACEC SA: %{y:.1f}<extra></extra>',name='Mes activo IMACEC',cliponaxis=False),
            go.Scatter(x=[dates[i],dates[i]],y=panel_range,xaxis='x2',yaxis='y2',mode='lines',line=dict(color='#64748b',width=1,dash='dot'),hoverinfo='skip')]
    frames=[go.Frame(name=r.mes,data=traces(i),traces=list(range(7)),layout=dict(title=dict(text=f'Chile | inflación, empleo, salarios y actividad<br><sup>{r.mes} · IR real {r.ir_real_anual:+.2f}% · IMACEC promedio 3m {r.imacec_promedio_anual:+.2f}% interanual</sup>'))) for i,r in enumerate(d.itertuples())]
    fig=go.Figure(data=traces(0),frames=frames)
    animation=dict(mode='immediate',frame=dict(duration=0,redraw=True),transition=dict(duration=0))
    fig.update_layout(template='plotly_white',height=1080,font=dict(family='Arial',color='#172b4d',size=13),title=frames[0].layout.title,
        margin=dict(l=90,r=185,t=125,b=210),showlegend=False,
        xaxis=dict(domain=[0,1],anchor='y',title='Desocupación (%) · trimestre móvil ENE',range=limits(pd.concat([d.desocupacion,pd.Series(NAIRU_RANGO)])),ticksuffix='%'),
        yaxis=dict(domain=[.38,1],anchor='x',title='IPC · variación anual (%)',range=limits(pd.concat([d.ipc_anual,pd.Series([META_INFLACION])])),ticksuffix='%'),
        xaxis2=dict(domain=[0,1],anchor='y2',type='date',range=[dates[0],dates[-1]],tickformat='%b %Y',dtick='M3',tickangle=0),
        yaxis2=dict(domain=[0,.19],anchor='x2',title='Índice 2018=100',range=panel_range),
        coloraxis=dict(cmin=-bound,cmax=bound,cmid=0,cauto=False,colorscale=ACTIVITY_COLORS,colorbar=dict(title=dict(text='IMACEC promedio 3m<br>Variación interanual'),x=1.035,y=.69,len=.62,thickness=18,ticksuffix='%',tickvals=[-bound,-bound/2,0,bound/2,bound],ticktext=[f'{v:+.1f}%' if v else '0%' for v in [-bound,-bound/2,0,bound/2,bound]])),
        annotations=[dict(x=0,y=1.07,xref='paper',yref='paper',showarrow=False,xanchor='left',text='Área ∝ |IR real anual| · color: actividad (naranja − / claro 0 / azul +)'),
                     dict(x=0,y=.235,xref='paper',yref='paper',showarrow=False,xanchor='left',text='IMACEC desestacionalizado · nivel mensual · punto y cursor = mes activo'),
                     dict(x=0,y=-.225,xref='paper',yref='paper',showarrow=False,xanchor='left',yanchor='top',font=dict(size=11),text='Fuente: INE y BCCh · IMACEC: índices publicados con un decimal; tasas calculadas aproximadas.<br>Color: promedio móvil 3m de serie original, alineado con ENE. Panel: serie desestacionalizada.<br>* NAIRU: punto medio propio del rango 8,0–8,5% para 2024-T3 (dic. 2024); no estimación oficial 2026.')],
        updatemenus=[dict(type='buttons',direction='left',x=1,y=-.09,xanchor='right',yanchor='top',buttons=[dict(label='▶ Play',method='animate',args=[None,dict(frame=dict(duration=650,redraw=True),transition=dict(duration=0),fromcurrent=True,mode='immediate')]),dict(label='❚❚ Pausa',method='animate',args=[[None],dict(mode='immediate',frame=dict(duration=0,redraw=False),transition=dict(duration=0))]),dict(label='↺ Reiniciar',method='animate',args=[[d.mes.iloc[0]],animation])])],
        sliders=[dict(active=0,x=0,y=-.09,len=1,currentvalue=dict(prefix='Mes: '),pad=dict(t=10),steps=[dict(label=m,method='animate',args=[[m],animation]) for m in d.mes])])
    fig.add_shape(type='rect',x0=NAIRU_RANGO[0],x1=NAIRU_RANGO[1],y0=0,y1=1,xref='x',yref='y domain',fillcolor='rgba(124,58,237,0.06)',line_width=0,layer='below')
    fig.add_shape(type='line',x0=NAIRU_REFERENCIA,x1=NAIRU_REFERENCIA,y0=0,y1=1,xref='x',yref='y domain',line=dict(color='#7c3aed',dash='dashdot',width=2))
    fig.add_shape(type='line',x0=0,x1=1,y0=META_INFLACION,y1=META_INFLACION,xref='x domain',yref='y',line=dict(color='#2563eb',dash='dash',width=2))
    fig.add_annotation(x=NAIRU_REFERENCIA,y=.99,xref='x',yref='y domain',text='NAIRU ref. 8,25%*',showarrow=False,xanchor='left',yanchor='top',xshift=8,font=dict(color='#6d28d9',size=12),bgcolor='rgba(255,255,255,.85)')
    fig.add_annotation(x=1,y=META_INFLACION,xref='x domain',yref='y',text='Meta de inflación: 3%',showarrow=False,xanchor='right',yanchor='bottom',yshift=5,font=dict(color='#1d4ed8',size=12),bgcolor='rgba(255,255,255,.85)')
    fig.update_layout(title=dict(x=.06,y=.98,yanchor='top'))
    return fig

def export_results(data, coverage, missing, fig, out=ROOT/'resultados'):
    out=Path(out); out.mkdir(exist_ok=True)
    data.to_csv(out/'datos_phillips.csv',index=False,encoding='utf-8-sig')
    coverage.to_csv(out/'cobertura.csv',index=False,encoding='utf-8-sig')
    missing.to_csv(out/'meses_excluidos.csv',index=False,encoding='utf-8-sig')
    fig.write_html(out/'phillips_animado.html',include_plotlyjs=True,auto_play=False,config={'responsive':True,'displaylogo':False})
    (out/'referencias_macro.json').write_text(json.dumps(REFERENCIAS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [*ROOT.glob('ine_*_chile.csv'),ROOT/'bcch_imacec_chile.csv']}
    (out/'fuentes_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def static_chart(d, out=ROOT/'resultados'/'phillips_estatico.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    cmap=LinearSegmentedColormap.from_list('actividad',[v[1] for v in ACTIVITY_COLORS])
    bound=max(float(d.imacec_promedio_anual.abs().max()),.1)
    norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound)
    fig=plt.figure(figsize=(10,7.5),layout='constrained')
    gs=fig.add_gridspec(2,2,height_ratios=[3.5,1],width_ratios=[24,1])
    ax=fig.add_subplot(gs[0,0]); panel=fig.add_subplot(gs[1,0]); bar=fig.add_subplot(gs[0,1])
    ax.axvspan(*NAIRU_RANGO,color='#7c3aed',alpha=.06,zorder=0)
    ax.axvline(NAIRU_REFERENCIA,color='#7c3aed',ls='-.',lw=1.3,label='NAIRU ref. 8,25%*')
    ax.axhline(META_INFLACION,color='#2563eb',ls='--',lw=1.3,label='Meta de inflación 3%')
    ax.plot(d.desocupacion,d.ipc_anual,c='#a8b3bf',lw=1.1,zorder=1)
    points=ax.scatter(d.desocupacion,d.ipc_anual,s=d.ir_magnitud*85,c=d.imacec_promedio_anual,cmap=cmap,norm=norm,edgecolors='#64748b',linewidths=.4,zorder=2)
    for i,label in [(0,'Inicio'),(len(d)-1,'Final')]:
        r=d.iloc[i];ax.annotate(f'{label} {r.mes}',(r.desocupacion,r.ipc_anual),xytext=(5,9),textcoords='offset points',fontsize=9)
    ax.set(xlabel='Desocupación (%) · trimestre móvil, mes central',ylabel='IPC · variación anual (%)',title=f'Chile · {d.mes.iloc[0]} a {d.mes.iloc[-1]}')
    ax.legend(loc='lower left',fontsize=8)
    cb=fig.colorbar(points,cax=bar);cb.set_label('IMACEC promedio 3m · variación interanual (%)')
    panel.plot(d.fecha,d.imacec_sa,color='#334155',lw=1.5)
    panel.scatter(d.fecha.iloc[-1],d.imacec_sa.iloc[-1],c=[d.imacec_promedio_anual.iloc[-1]],cmap=cmap,norm=norm,edgecolors='#0f172a',s=35,zorder=3)
    panel.set(title='IMACEC desestacionalizado · nivel mensual',ylabel='2018=100',xlim=(d.fecha.iloc[0],d.fecha.iloc[-1]))
    panel.xaxis.set_major_locator(mdates.MonthLocator(interval=4));panel.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    for axis in [ax,panel]:
        axis.grid(alpha=.15);axis.spines[['top','right']].set_visible(False)
    fig.text(.01,-.04,'Fuente: INE y BCCh. Área ∝ |IR real anual|; color = crecimiento del promedio 3m de IMACEC original.\n* Referencia histórica 2024-T3 publicada en dic. 2024. IMACEC calculado con índices de un decimal.',fontsize=8.5)
    fig.savefig(out,dpi=180,bbox_inches='tight');plt.close(fig)

if __name__=='__main__':
    data,coverage,missing=load_data()
    fig=build_figure(data)
    export_results(data,coverage,missing,fig)
    static_chart(data)
    print(coverage.to_string(index=False))
    print(data[['mes','desocupacion','ipc_anual','ir_real_anual']].to_string(index=False))
    print('Correlación descriptiva:',data.desocupacion.corr(data.ipc_anual))


