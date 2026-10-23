"""Comparación descriptiva de etapas y narración derivada del mismo corte."""
import math

ETAPAS = (
    ('prepandemia', 'Antes de la pandemia', None, '2020-02'),
    ('pandemia', 'Ventana de pandemia', '2020-03', '2023-08'),
    ('pospandemia', 'Después de la ventana de pandemia', '2023-09', None),
)
TASAS = ('desocupacion', 'ipc_anual', 'ir_real_anual', 'imacec_sa_anual')
NIVELES = ('imacec_sa', 'ir_indice_real')

def _numero(value):
    value=float(value)
    return value if math.isfinite(value) else None

def resumen_etapas(data):
    etapas=[]
    for codigo,nombre,desde,hasta in ETAPAS:
        d=data
        if desde: d=d.loc[d.mes.ge(desde)]
        if hasta: d=d.loc[d.mes.le(hasta)]
        if d.empty: continue
        metricas={}
        for col in (*TASAS,*NIVELES):
            valid=d.loc[d[col].notna()]
            if valid.empty: continue
            lo=valid.loc[valid[col].idxmin()]; hi=valid.loc[valid[col].idxmax()]
            metricas[col]={
                'inicio':_numero(d[col].iloc[0]), 'final':_numero(d[col].iloc[-1]),
                'media':_numero(valid[col].mean()),
                'minimo':_numero(lo[col]), 'mes_minimo':str(lo.mes),
                'maximo':_numero(hi[col]), 'mes_maximo':str(hi.mes),
            }
            if col in TASAS:
                metricas[col]['cambio_pp']=_numero(d[col].iloc[-1]-d[col].iloc[0])
            else:
                metricas[col]['cambio_nivel_pct']=_numero(100*(d[col].iloc[-1]/d[col].iloc[0]-1))
        corr=d.desocupacion.corr(d.ipc_anual) if len(d)>1 else float('nan')
        etapas.append({'codigo':codigo,'etapa':nombre,'desde':d.mes.iloc[0],'hasta':d.mes.iloc[-1],
                       'n':len(d),'correlacion':_numero(corr),'metricas':metricas,
                       'meses_ir_negativo':int(d.ir_real_anual.lt(0).sum()),
                       'meses_actividad_negativa':int(d.imacec_sa_anual.lt(0).sum())})
    pre=data.loc[data.mes.le('2020-02')]
    referencia=None
    if not pre.empty:
        base=pre.iloc[-1]; final=data.iloc[-1]
        referencia={'mes_base':base.mes,'mes_final':final.mes,
                    'desocupacion_cambio_pp':float(final.desocupacion-base.desocupacion),
                    'ipc_cambio_pp':float(final.ipc_anual-base.ipc_anual),
                    'imacec_nivel_cambio_pct':float(100*(final.imacec_sa/base.imacec_sa-1)),
                    'ir_real_nivel_cambio_pct':float(100*(final.ir_indice_real/base.ir_indice_real-1))}
    return {'etapas':etapas,'comparacion_previa':referencia,
            'regla':'Antes: hasta febrero de 2020; ventana de pandemia: marzo de 2020 a agosto de 2023; después: desde septiembre de 2023. Cortes descriptivos del gráfico, no identificación de efectos causales.'}

def f(value,digits=2):
    return 'no disponible' if value is None else f'{value:.{digits}f}'.replace('-', '−').replace('.', ',')

def diferencia(value,unidad='puntos porcentuales'):
    if abs(value)<0.005: return f'prácticamente sin diferencia ({f(value)} {unidad})'
    return f'{f(abs(value))} {unidad} '+('por encima' if value>0 else 'por debajo')

def secciones_evolucion(summary):
    """Texto de análisis, sin atribuir causalidad a las ventanas temporales."""
    evolucion=summary['evolucion']
    etapas={e['codigo']:e for e in evolucion['etapas']}
    out=[('h','Cómo cambió la relación entre inflación y empleo'),
         ('p','La comparación requiere separar la situación anterior al shock sanitario, la ventana de pandemia y el período posterior. Una correlación de toda la historia mezcla episodios con niveles y trayectorias diferentes. A continuación se comparan la evolución de cada indicador, las medias mensuales y los puntos de partida y llegada de cada etapa.'),
         ('p',evolucion['regla']+' Los períodos tienen duraciones distintas. Las medias de tasas interanuales resumen los meses de cada etapa; no son tasas acumuladas ni crecimiento anual compuesto. Los cambios de niveles se calculan como cocientes entre índices y no sumando tasas.')]
    for codigo,_,_,_ in ETAPAS:
        if codigo not in etapas: continue
        e=etapas[codigo]; m=e['metricas']
        out.extend([
            ('h',e['etapa']),
            ('p',f"Entre {e['desde']} y {e['hasta']} ({e['n']} meses), la desocupación media fue {f(m['desocupacion']['media'])}% y la inflación anual media {f(m['ipc_anual']['media'])}%. La variación anual media del IR real fue {f(m['ir_real_anual']['media'])}% y la del IMACEC desestacionalizado {f(m['imacec_sa_anual']['media'])}%. La correlación IPC–desocupación en esta ventana fue {f(e['correlacion'],3)}."),
            ('p',f"La desocupación pasó de {f(m['desocupacion']['inicio'])}% a {f(m['desocupacion']['final'])}% y la inflación anual de {f(m['ipc_anual']['inicio'])}% a {f(m['ipc_anual']['final'])}%. Entre el primer y el último mes de la etapa, el nivel del IMACEC desestacionalizado cambió {f(m['imacec_sa']['cambio_nivel_pct'])}% y el índice de remuneraciones reales {f(m['ir_indice_real']['cambio_nivel_pct'])}%. Hubo {e['meses_ir_negativo']} meses con caída interanual del IR real y {e['meses_actividad_negativa']} con caída interanual de la actividad desestacionalizada.")
        ])
    pre=etapas.get('prepandemia'); pan=etapas.get('pandemia'); post=etapas.get('pospandemia')
    last=summary['final']; ext=summary['extremos']
    out.append(('h','Evolución de los indicadores y recuperación'))
    if pre and pan:
        u=pan['metricas']['desocupacion']; pi=pan['metricas']['ipc_anual']
        out.append(('p',f"Empleo e inflación no alcanzaron sus máximos al mismo tiempo. Dentro de la ventana de pandemia, la desocupación llegó a {f(u['maximo'])}% en {u['mes_maximo']}, mientras la inflación máxima fue {f(pi['maximo'])}% en {pi['mes_maximo']}. La diferencia temporal muestra por qué una lectura de intercambio contemporáneo fijo puede resultar engañosa: el gráfico no controla los shocks de oferta, las expectativas ni los rezagos."))
        activity=pan['metricas']['imacec_sa']; wage=pan['metricas']['ir_real_anual']
        base_activity=pre['metricas']['imacec_sa']['final']
        drawdown=100*(activity['minimo']/base_activity-1)
        out.append(('p',f"Actividad y poder adquisitivo también siguieron tiempos distintos. El IMACEC desestacionalizado tocó un mínimo de {f(activity['minimo'],1)} en {activity['mes_minimo']} dentro de la ventana, equivalente a un cambio de {f(drawdown)}% respecto de {pre['hasta']}. La tasa anual del IR real registró su mínimo de esa ventana en {wage['mes_minimo']}, con {f(wage['minimo'])}%. Una tasa interanual positiva después del mínimo no demuestra, por sí sola, que se haya recuperado todo el nivel perdido."))
    if pre and post:
        mp=pre['metricas']; mq=post['metricas']
        du=mq['desocupacion']['media']-mp['desocupacion']['media']
        dpi=mq['ipc_anual']['media']-mp['ipc_anual']['media']
        out.append(('p',f"En la etapa posterior, la desocupación media quedó {diferencia(du)} de su media anterior a la pandemia; la inflación anual media quedó {diferencia(dpi)}. Estas diferencias de medias no equivalen al efecto causal de la pandemia: también cambian la composición de la muestra, las condiciones macroeconómicas y la extensión de cada ventana."))
        peak=ext['ipc_anual']['max']
        out.append(('p',f"En el último mes común, {last['mes']}, la inflación fue {f(last['ipc_anual'])}%, frente al máximo muestral de {f(peak['ipc_anual'])}% de {peak['mes']}; la diferencia es {f(last['ipc_anual']-peak['ipc_anual'])} puntos porcentuales. La desocupación de {f(last['desocupacion'])}% se compara con {f(mp['desocupacion']['final'])}% en {pre['hasta']}. Menor inflación y recuperación del nivel de actividad pueden coexistir con una situación laboral distinta de la previa."))
    base=evolucion['comparacion_previa']
    if base:
        out.append(('p',f"Comparando {base['mes_final']} con {base['mes_base']}, el nivel del IMACEC desestacionalizado cambió {f(base['imacec_nivel_cambio_pct'])}% y el índice de remuneraciones reales {f(base['ir_real_nivel_cambio_pct'])}%. Este contraste usa niveles de índices. En cambio, las tasas anuales del último mes fueron {f(last['imacec_sa_anual'])}% en IMACEC y {f(last['ir_real_anual'])}% en remuneraciones reales. El nivel recuperado y el impulso reciente son conceptos diferentes; no se interpreta el IMACEC como una medida por habitante o de actividad potencial."))
    out.append(('h','Conclusiones'))
    out.append(('p',f"Primera conclusión: la correlación agregada de {f(summary['correlacion'],3)} no resume una relación invariable entre inflación y desempleo. "+'Las correlaciones por etapa fueron: '+'; '.join(f"{f(e['correlacion'],3)} {dict(prepandemia='antes de la pandemia',pandemia='durante la ventana de pandemia',pospandemia='después de esa ventana')[e['codigo']]}" for e in evolucion['etapas'])+'.'+' La variación entre ventanas justifica analizar episodios y rezagos antes de extraer una interpretación estructural.'))
    if pre:
        gap=last['desocupacion']-pre['metricas']['desocupacion']['media']
        out.append(('p',f"Segunda conclusión: al cierre, la desocupación está {diferencia(gap)} de la media previa a la pandemia. Por su parte, la inflación se sitúa {diferencia(last['ipc_anual']-3)} de la referencia del 3%. Son comparaciones descriptivas: esa meta corresponde al horizonte de dos años y estas cifras no permiten estimar la NAIRU actual ni evaluar por sí solas una decisión de política monetaria."))
    out.append(('p',f"Tercera conclusión: la lectura de recuperación debe integrar actividad y remuneraciones reales, además del empleo y los precios. En {last['mes']}, el IMACEC desestacionalizado varía {f(last['imacec_sa_anual'])}% a doce meses y el IR real {f(last['ir_real_anual'])}%. Que sus tasas o niveles evolucionen de forma distinta impide hablar de una recuperación uniforme con un solo indicador."))
    out.append(('p','Cuarta conclusión: este ejercicio documenta trayectorias observadas, no identifica cuánto de cada cambio se debe a la pandemia ni establece causalidad entre desempleo e inflación. Para responder esas preguntas harían falta modelos con expectativas, oferta, productividad y rezagos, junto con pruebas de estabilidad. El último año puede ser parcial y el mes final depende de la intersección de las cuatro fuentes.'))
    return out
