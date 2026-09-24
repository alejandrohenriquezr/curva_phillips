"""Presentación del gráfico: fechas, panel anual y bordes segmentados SVG."""
import numpy as np
import plotly.graph_objects as go

YEAR_COLORS=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf','#393b79','#637939','#8c6d31','#843c39','#7b4173','#3182bd','#31a354','#756bb1','#e6550d','#636363']

def border_color(year,pandemic=False):
    return '#334155' if pandemic else YEAR_COLORS[(int(year)-2011)%len(YEAR_COLORS)]

PANDEMIC_NOTE='Círculos con línea segmentada: período de pandemia de Covid-19 en Chile (03-2020–08-2023; ventana del gráfico).'
DASH_SCRIPT=r'''
(function(){
 const gd=document.getElementById('{plot_id}');
 function paint(){
  [0,1].forEach(k=>{
   const trace=gd._fullData[k]; if(!trace) return;
   const group=gd.querySelector('g.trace.scatter.trace'+trace.uid); if(!group) return;
   group.querySelectorAll('path.point').forEach((p,j)=>{
    const index=p.__data__ && Number.isInteger(p.__data__.i)?p.__data__.i:j;
    const c=gd.data[k].customdata[index]; const pandemic=c && c[9];
    p.style.strokeDasharray=pandemic?'4,2':'none';
    p.style.strokeWidth=pandemic?'2px':(k===1?'2.5px':'1.5px');
    p.style.stroke=c[10];
    p.setAttribute('data-pandemia',pandemic?'true':'false');
   });
  });
 }
 gd.on('plotly_afterplot',paint); gd.on('plotly_animated',paint);
 gd.on('plotly_sliderchange',()=>requestAnimationFrame(paint));
 paint(); requestAnimationFrame(paint);
})();
'''

def figure_html(fig,full_html=True):
    return fig.to_html(full_html=full_html,include_plotlyjs=True,auto_play=False,
                       post_script=DASH_SCRIPT,config={'responsive':True,'displaylogo':False})

def date_labels(data,xrange,yrange,width=1000,height=450):
    """Posiciones de etiquetas fijas para la muestra completa, con separación en píxeles."""
    selected=data[(data.fecha.dt.month==1)|data.mes.isin(['2020-03','2023-08'])]
    boxes=[]; labels=[]
    for i,r in selected.iterrows():
        x=(r.desocupacion-xrange[0])/(xrange[1]-xrange[0])*width
        y=(1-(r.ipc_anual-yrange[0])/(yrange[1]-yrange[0]))*height
        candidates=[(dx,dy) for radius in [30,55,85,120,160,200] for dx,dy in [(radius,-radius),(-radius,-radius),(radius,radius),(-radius,radius),(0,-radius),(0,radius)]]
        best=None
        for dx,dy in candidates:
            cx,cy=x+dx,y+dy
            if not (30<cx<width-30 and 12<cy<height-12): continue
            box=(cx-28,cy-9,cx+28,cy+9)
            overlap=sum(not(box[2]+5<b[0] or box[0]-5>b[2] or box[3]+4<b[1] or box[1]-4>b[3]) for b in boxes)
            score=overlap*10000+dx*dx+dy*dy
            if best is None or score<best[0]: best=(score,dx,dy,box)
        if best is None: best=(0,0,-25,(x-28,y-34,x+28,y-16))
        _,dx,dy,box=best;boxes.append(box)
        labels.append((int(i),dict(x=float(r.desocupacion),y=float(r.ipc_anual),xref='x',yref='y',
            text=r.fecha.strftime('%m-%Y'),showarrow=True,arrowhead=0,arrowwidth=.65,arrowcolor='#64748b',
            ax=dx,ay=dy,font=dict(size=10,color='#172b4d'),bgcolor='rgba(255,255,255,.88)',borderpad=1)))
    return labels

def annual_normalization(data):
    return max(float(np.abs(data[['imacec_sa_anual','ipc_anual']].to_numpy()).max()),.1)

def enhance(fig,data):
    d=data.reset_index(drop=True); dates=d.fecha.dt.strftime('%Y-%m-%d').tolist()
    limit=annual_normalization(d)
    vals=np.r_[d.imacec_sa_anual,d.ipc_anual,d.loc[d.fecha.dt.month==12,'imacec_acumulado_anual']]
    padding=max((vals.max()-vals.min())*.12,1)
    panel_range=[float(min(vals.min()-padding,0)),float(vals.max()+padding)]
    labels=date_labels(d,fig.layout.xaxis.range,fig.layout.yaxis.range)
    notes=list(fig.layout.annotations)
    notes[1].text='Variación en 12 meses: IMACEC desestacionalizado (azul) e IPC (rojo) · diciembre: acumulado anual'
    notes[1].y=.30
    notes[2].text=('Fuente: INE y BCCh. IMACEC calculado con índices de un decimal.<br>'
        'Diciembre: rombos = crecimiento del promedio anual IMACEC original; cuadrados = IPC dic./dic.<br>'
        'Área y color de esos puntos: tasa a 12 meses normalizada de toda la muestra; cero = área nula.<br>'+
        PANDEMIC_NOTE+'<br>* NAIRU 8,25%: punto medio propio del rango BCCh 2024-T3, no estimación oficial 2026.')
    notes[2].y=-.24
    notes[2].update(x=0,xanchor='left',align='left')
    def update_traces(i,old):
        traces=list(old)
        for k in [0,1]:
            records=[list(c) for c in traces[k].customdata]
            ids=range(i+1) if k==0 else [i]
            for c,j in zip(records,ids):
                c.extend([bool(d.pandemia.iloc[j]),border_color(d.fecha.iloc[j].year,d.pandemia.iloc[j])])
            traces[k].marker.line=dict(color=[c[10] for c in records],width=1.5 if k==0 else 2.5)
            traces[k].customdata=records
        for k in [3,4,5]:
            traces[k].y=(d.imacec_sa_anual.tolist() if k==3 else d.imacec_sa_anual.iloc[:i+1].tolist() if k==4 else [float(d.imacec_sa_anual.iloc[i])])
            traces[k].hovertemplate='%{x|%m-%Y}<br>IMACEC SA · 12 meses: %{y:+.2f}%<extra></extra>'
        traces[4].line.color='#2166ac'
        traces[5].marker=dict(size=6,color='#2166ac');traces[6].y=panel_range
        traces.extend([
          go.Scatter(x=dates,y=d.ipc_anual.tolist(),xaxis='x2',yaxis='y2',mode='lines',line=dict(color='#efd4d2',width=1.2),hovertemplate='%{x|%m-%Y}<br>IPC 12 meses: %{y:+.2f}%<extra></extra>',name='IPC contexto'),
          go.Scatter(x=dates[:i+1],y=d.ipc_anual.iloc[:i+1].tolist(),xaxis='x2',yaxis='y2',mode='lines',line=dict(color='#b33b37',width=2),hovertemplate='%{x|%m-%Y}<br>IPC 12 meses: %{y:+.2f}%<extra></extra>',name='IPC anual')])
        dec=d.iloc[:i+1].loc[lambda x:x.fecha.dt.month.eq(12)]
        for annual,rate,symbol,label in [('imacec_acumulado_anual','imacec_sa_anual','diamond','IMACEC promedio anual original'),('ipc_acumulado_diciembre','ipc_anual','square','IPC diciembre/diciembre')]:
            normalized=dec[rate]/limit
            traces.append(go.Scatter(x=dec.fecha.dt.strftime('%Y-%m-%d').tolist(),y=dec[annual].tolist(),xaxis='x2',yaxis='y2',mode='markers',
                marker=dict(symbol=symbol,size=normalized.abs().tolist(),sizemode='area',sizeref=2/(23**2),color=normalized.tolist(),coloraxis='coloraxis2',line=dict(color='#334155',width=1)),
                customdata=np.column_stack([dec[rate],normalized]).tolist(),
                hovertemplate=('%{x|%Y} · '+label+'<br>Acumulado del año: %{y:+.2f}%<br>Tasa 12 meses usada para tamaño/color: %{customdata[0]:+.2f}%<br>Normalizada: %{customdata[1]:+.3f}<extra></extra>'),name=label,cliponaxis=False))
        for k,t in enumerate(traces): t.showlegend=k in [4,8]
        traces[4].name='IMACEC · 12 meses';traces[8].name='IPC · 12 meses'
        return traces
    initial=update_traces(0,fig.data)
    # Agregar las cuatro trazas nuevas sin perder las originales.
    for k in range(7):fig.data[k].update(initial[k])
    fig.add_traces(initial[7:])
    for i,frame in enumerate(fig.frames):
        frame.data=update_traces(i,frame.data);frame.traces=list(range(11))
        frame.layout.annotations=notes+[dict(a,visible=j<=i) for j,a in labels]
    fig.update_layout(showlegend=True,legend=dict(orientation='h',x=0,y=.29,xanchor='left',yanchor='top',itemclick=False,itemdoubleclick=False),height=1280,margin=dict(l=90,r=220,t=125,b=320),
        yaxis=dict(domain=[.43,1]),yaxis2=dict(domain=[0,.255],title='Variación (%)',range=panel_range,ticksuffix='%'),
        coloraxis2=dict(cmin=-1,cmax=1,cmid=0,cauto=False,colorscale=[[0,'#d97706'],[.5,'#f7f7f2'],[1,'#2166ac']],
            colorbar=dict(title=dict(text='Puntos diciembre<br>12 meses normalizada'),x=1.04,y=.13,len=.30,thickness=15,tickvals=[-1,0,1],ticktext=['−1','0','+1'])),
        annotations=notes+[dict(a,visible=j==0) for j,a in labels])
    fig.layout.coloraxis.colorbar.y=.75;fig.layout.coloraxis.colorbar.len=.5
    fig.layout.meta={'normalizacion_panel_limite_pct':limit,'pandemia_desde':'2020-03','pandemia_hasta':'2023-08','fechas_etiquetas':[d.mes.iloc[j] for j,a in labels]}
    return fig
