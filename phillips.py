"""Análisis reproducible de los CSV del INE; no descarga ni modifica las fuentes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
MESES = dict(zip(['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'], range(1,13)))
COL_U = 'Tasa de desocupación [1] - tasa (%)'

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
    parts_data = [('IPC',ipc,'ipc_anual'), ('IR real',ir,'ir_real_anual'), ('ENE',ene,'desocupacion')]
    coverage = pd.DataFrame([{'serie':name,'desde':d.fecha.min().strftime('%Y-%m'),'hasta':d.fecha.max().strftime('%Y-%m'),'filas':len(d),'faltantes':int(d[col].isna().sum())} for name,d,col in parts_data])
    union = ipc[['fecha','ipc_anual']].merge(ir[['fecha','ir_real_anual','estado_ir']],on='fecha',how='outer',validate='one_to_one').merge(ene[['fecha','desocupacion','Trimestre','fecha_central_ene','fecha_final_ene']],on='fecha',how='outer',validate='one_to_one').sort_values('fecha')
    missing = union[union[['ipc_anual','ir_real_anual','desocupacion']].isna().any(axis=1)].copy()
    data = union.dropna(subset=['ipc_anual','ir_real_anual','desocupacion']).reset_index(drop=True)
    if len(data)<2:
        raise ValueError('No hay suficientes meses comunes completos')
    values = data[['ipc_anual','ir_real_anual','desocupacion']].to_numpy()
    if not np.isfinite(values).all() or not data.desocupacion.between(0,100).all():
        raise ValueError('Valores no finitos o desocupación fuera de rango')
    expected = pd.date_range(data.fecha.min(),data.fecha.max(),freq='MS')
    if not data.fecha.equals(pd.Series(expected,name='fecha')):
        raise ValueError('Hay huecos en el período común; revisar antes de animar')
    data['mes'] = data.fecha.dt.strftime('%Y-%m')
    data['ir_magnitud'] = data.ir_real_anual.abs()
    data['ir_signo'] = np.where(data.ir_real_anual>=0,'Aumento','Caída')
    return data, coverage, missing

def build_figure(data):
    d = data.reset_index(drop=True)
    max_mag = max(float(d.ir_magnitud.max()),1e-9)
    # Plotly sizemode=area: área proporcional a |variación|, sin desplazar valores.
    sizeref = 2*max_mag/(48**2)
    colors = np.where(d.ir_real_anual>=0,'#0d9488','#e26545').tolist()
    custom = [[r.mes,str(r.Trimestre),float(r.ir_real_anual),str(r.estado_ir)] for r in d.itertuples()]
    hover = ('<b>%{customdata[0]}</b><br>Desocupación: %{x:.2f}%<br>IPC anual: %{y:.2f}%<br>IR real anual: %{customdata[2]:+.2f}%<br>ENE: %{customdata[1]} (mes central)<br>Estado IR: %{customdata[3]}<extra></extra>')
    def traces(i):
        return [go.Scatter(x=d.desocupacion.iloc[:i+1].tolist(),y=d.ipc_anual.iloc[:i+1].tolist(),mode='lines+markers',line=dict(color='#94a3b8',width=2),marker=dict(size=d.ir_magnitud.iloc[:i+1].tolist(),sizemode='area',sizeref=sizeref,color=colors[:i+1],opacity=.40),customdata=custom[:i+1],hovertemplate=hover,name='Rastro acumulado'),
                go.Scatter(x=[float(d.desocupacion.iloc[i])],y=[float(d.ipc_anual.iloc[i])],mode='markers',marker=dict(size=[float(d.ir_magnitud.iloc[i])],sizemode='area',sizeref=sizeref,color=[colors[i]],line=dict(color='#0f172a',width=2)),customdata=[custom[i]],hovertemplate=hover,name='Mes actual'),
                go.Scatter(x=[float(d.desocupacion.iloc[i])],y=[float(d.ipc_anual.iloc[i])],mode='markers',marker=dict(size=5,color='#0f172a'),hoverinfo='skip',name='Centro del punto',showlegend=False)]
    frames = [go.Frame(name=r.mes,data=traces(i),traces=[0,1,2],layout=dict(title=dict(text=f'Chile | inflación, empleo y remuneraciones<br><sup>{r.mes} · IR real anual {r.ir_real_anual:+.2f}%</sup>'))) for i,r in enumerate(d.itertuples())]
    fig = go.Figure(data=traces(0),frames=frames)
    def limits(s):
        margin=max((s.max()-s.min())*.18,.25)
        return [float(s.min()-margin),float(s.max()+margin)]
    fig.update_layout(template='plotly_white',height=900,font=dict(family='Arial',color='#172b4d',size=14),title=frames[0].layout.title,margin=dict(l=90,r=45,t=150,b=250),xaxis=dict(title='Tasa de desocupación (%) · trimestre móvil',range=limits(d.desocupacion),ticksuffix='%'),yaxis=dict(title='Variación anual del IPC (%)',range=limits(d.ipc_anual),ticksuffix='%'),showlegend=False,
        annotations=[dict(x=0,y=1.10,xref='paper',yref='paper',showarrow=False,xanchor='left',text='Área ∝ |IR real anual| · verde: aumento · naranja: caída'),dict(x=0,y=-.43,yanchor='top',xref='paper',yref='paper',showarrow=False,xanchor='left',text='Fuente: INE · ENE asignada al mes central · sin ajuste estacional<br>El centro oscuro permite localizar valores de IR iguales a cero.')],
        updatemenus=[dict(type='buttons',direction='left',x=1,y=-.19,xanchor='right',yanchor='top',buttons=[dict(label='▶ Play',method='animate',args=[None,dict(frame=dict(duration=650,redraw=True),transition=dict(duration=0),fromcurrent=True,mode='immediate')]),dict(label='❚❚ Pausa',method='animate',args=[[None],dict(mode='immediate',frame=dict(duration=0,redraw=False),transition=dict(duration=0))]),dict(label='↺ Reiniciar',method='animate',args=[[d.mes.iloc[0]],dict(mode='immediate',frame=dict(duration=0,redraw=True),transition=dict(duration=0))])])],
        sliders=[dict(active=0,x=0,y=-.18,len=1,currentvalue=dict(prefix='Mes: '),pad=dict(t=10),steps=[dict(label=m,method='animate',args=[[m],dict(mode='immediate',frame=dict(duration=0,redraw=True),transition=dict(duration=0))]) for m in d.mes])])
    fig.update_layout(title=dict(x=.065,y=.98,yanchor='top'))
    return fig

def export_results(data, coverage, missing, fig, out=ROOT/'resultados'):
    out=Path(out); out.mkdir(exist_ok=True)
    data.to_csv(out/'datos_phillips.csv',index=False,encoding='utf-8-sig')
    coverage.to_csv(out/'cobertura.csv',index=False,encoding='utf-8-sig')
    missing.to_csv(out/'meses_excluidos.csv',index=False,encoding='utf-8-sig')
    fig.write_html(out/'phillips_animado.html',include_plotlyjs=True,auto_play=False,config={'responsive':True,'displaylogo':False})
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('ine_*_chile.csv')}
    (out/'fuentes_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def static_chart(d, out=ROOT/'resultados'/'phillips_estatico.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5.6),layout='constrained')
    ax.plot(d.desocupacion,d.ipc_anual,c='#a8b3bf',lw=1.2,zorder=1)
    ax.scatter(d.desocupacion,d.ipc_anual,s=d.ir_magnitud*100,c=np.where(d.ir_real_anual>=0,'#0d9488','#e26545'),alpha=.55,edgecolors='white',zorder=2)
    for i,label in [(0,'Inicio'),(len(d)-1,'Final')]:
        r=d.iloc[i]
        ax.annotate(f'{label} {r.mes}',(r.desocupacion,r.ipc_anual),xytext=(7,9),textcoords='offset points',fontsize=10)
    ax.set(xlabel='Desocupación (%) · trimestre móvil, mes central',ylabel='IPC · variación anual (%)',title=f'Chile · {d.mes.iloc[0]} a {d.mes.iloc[-1]}')
    ax.grid(alpha=.15); ax.spines[['top','right']].set_visible(False)
    fig.text(.01,-.035,'Fuente: CSV del INE. Área proporcional a |IR real anual|. Verde: aumento; naranja: caída.',fontsize=9)
    fig.savefig(out,dpi=180,bbox_inches='tight'); plt.close(fig)

if __name__=='__main__':
    data,coverage,missing=load_data()
    fig=build_figure(data)
    export_results(data,coverage,missing,fig)
    static_chart(data)
    print(coverage.to_string(index=False))
    print(data[['mes','desocupacion','ipc_anual','ir_real_anual']].to_string(index=False))
    print('Correlación descriptiva:',data.desocupacion.corr(data.ipc_anual))


