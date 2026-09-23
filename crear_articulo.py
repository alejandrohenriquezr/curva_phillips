from pathlib import Path
import json
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parent
out=ROOT/'informe'; out.mkdir(exist_ok=True)
sections=[
('title','Inflación y empleo en Chile vistos a través de la curva de Phillips'),
('subtitle','Enero de 2024 a junio de 2026 | Análisis para LinkedIn'),
('p','Entre enero de 2024 y junio de 2026, la relación contemporánea entre inflación y desocupación en esta muestra chilena fue prácticamente nula. La correlación de las 30 observaciones es −0,011. El resultado invita a mirar la trayectoria de ambas variables y las remuneraciones reales, sin convertir una asociación estadística de corto plazo en una conclusión causal.'),
('p','El gráfico animado permite hacerlo: la desocupación ocupa el eje horizontal, la inflación anual del IPC el vertical y el área de cada burbuja representa la magnitud de la variación anual del índice de remuneraciones real. El rastro conserva el recorrido. En la muestra, todas las variaciones del IR real son positivas y, por eso, las burbujas aparecen en verde.'),
('image',''),
('caption','Cada punto combina el IPC y el IR real del mes con la ENE del trimestre móvil centrado en ese mes. El tamaño representa el valor absoluto de la variación anual del IR real; el gráfico interactivo distingue las caídas en naranja.'),
('break',''),
('h','Una trayectoria que cambia de dirección'),
('p','El punto inicial combina una inflación anual de 3,8%, una desocupación de 8,50% y un aumento anual del IR real de 2,78%. En junio de 2026, el punto final registra 4,3%, 9,53% y 3,27%, respectivamente. Entre los extremos, la desocupación aumenta 1,03 puntos porcentuales y la inflación 0,5 puntos. Sin embargo, esa comparación omite los cambios de dirección que aparecen durante el recorrido.'),
('p','En febrero de 2026, la inflación anual baja a 2,4%, mientras la desocupación se ubica en 8,93%. En junio, ambas variables son mayores: 4,3% y 9,53%. Este desplazamiento hacia arriba y hacia la derecha no encaja con una lectura mecánica según la cual más desempleo siempre debe coincidir con menos inflación. Es una descripción de cuatro meses, no una identificación del shock que los explica.'),
('h','Qué puede decir una curva de Phillips'),
('p','La intuición económica de la curva de Phillips relaciona las presiones inflacionarias con la holgura de la economía. Un mercado laboral más estrecho puede aumentar las presiones salariales y de costos. Pero la inflación observada también responde a expectativas, precios importados, tipo de cambio, productividad y perturbaciones de oferta. El análisis del Banco Central sobre la evidencia chilena subraya la necesidad de una especificación más amplia que una nube de inflación y desempleo [4].'),
('p','Por eso, la correlación cercana a cero no demuestra que esa relación económica haya desaparecido. Puede reflejar fuerzas que operan al mismo tiempo, rezagos, cambios de expectativas o una muestra demasiado breve. Tampoco permite estimar la tasa de desempleo compatible con inflación estable ni atribuir el movimiento a una decisión específica de política monetaria.'),
('h','El salario real agrega una dimensión relevante'),
('p','El IR real crece en términos anuales en los 30 meses comunes, con variaciones entre 1,40% y 3,74%. En junio de 2026, el aumento de 3,27% convive con una desocupación elevada respecto del comienzo de la muestra. Esta coexistencia recuerda que el poder adquisitivo de la remuneración por hora y la posibilidad de acceder a un empleo son dimensiones distintas del bienestar laboral.'),
('p','El indicador del INE mide remuneraciones reales por hora en su ámbito de cobertura. No equivale al ingreso laboral total de los hogares: no incorpora del mismo modo el desempleo, los cambios de horas trabajadas o todas las formas de ocupación. Además, el IR real utiliza el IPC como deflactor. No es una tercera variable estadísticamente independiente de la inflación y no debe volver a descontársele el IPC [3].'),
('break',''),
('h','Leer el gráfico con sus límites'),
('p','La ENE entrega trimestres móviles que comparten dos meses entre observaciones consecutivas. Aquí se utiliza el mes central, respetando la convención de los archivos: junio de 2026 corresponde a mayo–julio de 2026. El ejercicio es retrospectivo; ese punto no representa lo que se conocía en tiempo real durante junio. El cuaderno permite contrastar la asignación al mes final.'),
('p','La muestra se limita a la intersección disponible de las tres series: 30 meses desde enero de 2024 hasta junio de 2026. Los archivos contienen IPC hasta agosto de 2026 e IR real hasta julio, pero no se completan los datos faltantes de empleo ni se prolonga artificialmente la animación. Tampoco se utilizan promedios de divisiones del IPC: se selecciona exclusivamente el IPC General y su variación anual publicada.'),
('p','Las tasas no están desestacionalizadas y los cambios a doce meses comparten información entre períodos. Estas dependencias, junto con el reducido tamaño de la muestra, impiden tratar los puntos como observaciones independientes para una inferencia simple. Una investigación econométrica requeriría un horizonte más largo, expectativas de inflación, controles de oferta, rezagos y una estrategia explícita de identificación.'),
('h','Una herramienta para formular mejores preguntas'),
('p','La animación sirve para identificar episodios, contrastar hipótesis y comunicar que inflación, empleo y poder adquisitivo no evolucionan de manera uniforme. La evidencia de este corte muestra que pueden coexistir remuneraciones reales crecientes, una tasa de desocupación mayor e inflación que cambia de dirección. Una evaluación de política económica necesita explicar esa combinación, no inferir una regla estable a partir de dos ejes.'),
('p','¿Qué parte de estos movimientos corresponde a la demanda y cuál a costos, expectativas o cambios del mercado laboral? Esa es la pregunta que este gráfico ayuda a plantear y que un análisis posterior debería poner a prueba.'),
('h','Fuentes y reproducibilidad'),
('source','[1] INE. Encuesta Nacional de Empleo, series vigentes. https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion'),
('source','[2] INE. Índice de Precios al Consumidor. https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor'),
('source','[3] INE. Índices de Remuneraciones y Costos Laborales; serie empalmada del IR real. https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales'),
('source','[4] Banco Central de Chile. IPoM, junio de 2016, recuadro sobre evidencia de la curva de Phillips para Chile. https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6'),
('source','Cálculos propios con los CSV del INE incluidos en el proyecto. Corte de archivos recibido el 22 de septiembre de 2026. Código, datos y gráfico: https://github.com/alejandrohenriquezr/curva_phillips'),
]
refs=json.loads((ROOT/'referencias_macro.json').read_text(encoding='utf-8-sig'))
updated=[]
for kind,text in sections:
    if kind=='caption':
        text='Área proporcional a la magnitud de la variación anual del IR real. ENE asignada al mes central. Línea horizontal: meta de inflación del 3%. Línea vertical: punto medio propio de 8,25% del rango NAIRU histórico 8,0–8,5% del BCCh para 2024-T3 [5].'
    if kind=='p' and text.startswith('En febrero de 2026'):
        text='El último punto se sitúa arriba y a la derecha del cruce de referencias: la inflación de 4,3% supera la meta en 1,30 puntos porcentuales y la desocupación de 9,53% está 1,28 puntos sobre el punto medio histórico de 8,25%. Estas distancias describen posiciones en el gráfico; no identifican por sí solas un shock de oferta ni una brecha cíclica oficial.'
    if kind=='p' and text.startswith('Por eso, la correlación'):
        text='La correlación cercana a cero no demuestra que la relación económica haya desaparecido. Puede reflejar fuerzas simultáneas, rezagos o una muestra breve. Tampoco permite estimar una NAIRU propia ni atribuir el movimiento a una decisión monetaria.'
    if kind=='h' and text=='Una herramienta para formular mejores preguntas':
        text='Qué significan las líneas de referencia'
    if kind=='p' and text.startswith('La animación sirve'):
        text='La minuta del BCCh citada en el IPoM de diciembre de 2024 presenta un rango NAIRU de 8,0–8,5% para el tercer trimestre de 2024, mediante filtros de Kalman multivariados y modelos VAR [5]. Usamos su punto medio, 8,25%, como convención visual propia, no como estimación puntual oficial ni como cifra de junio de 2026. La banda representa dispersión entre estimaciones, no un intervalo de confianza.'
    if kind=='p' and text.startswith('¿Qué parte'):
        text='La referencia es histórica y utiliza desempleo desestacionalizado, mientras nuestros puntos usan ENE sin ajuste estacional. No suponemos que la NAIRU haya permanecido constante ni la equiparamos automáticamente a la tasa natural de largo plazo. Por su parte, la meta del 3% corresponde a un horizonte de dos años [6]; no exige que la inflación de cada mes sea exactamente 3%. Estas referencias orientan la lectura, pero no bastan para recomendar una tasa de interés.'
    if kind=='h' and text=='Fuentes y reproducibilidad':
        updated.append(('break',''))
    if kind=='source' and text.startswith('Cálculos propios'):
        updated.extend([
            ('source','[5] Banco Central de Chile. Minutas citadas en el IPoM diciembre de 2024. Holguras en el mercado laboral, secciones 1 y 4, páginas 34 y 38 del PDF. '+refs['nairu_url']),
            ('source','[6] Banco Central de Chile. IPoM junio de 2026. La meta de inflación y la Tasa de Política Monetaria, página 3 del PDF. '+refs['meta_url'])])
    updated.append((kind,text))
sections=updated

doc=Document()
s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
s.top_margin=Cm(1.8); s.bottom_margin=Cm(1.8); s.left_margin=Cm(2); s.right_margin=Cm(2)
normal=doc.styles['Normal']; normal.font.name='Calibri'; normal.font.size=Pt(10.5)
normal.paragraph_format.space_after=Pt(7); normal.paragraph_format.line_spacing=1.10
for name,size in [('Title',25),('Subtitle',11),('Heading 1',14)]:
    st=doc.styles[name]; st.font.name='Calibri'; st.font.size=Pt(size); st.font.color.rgb=RGBColor.from_string('000000')
    st.paragraph_format.space_after=Pt(8)
    if name=='Heading 1': st.paragraph_format.space_before=Pt(9)
md=[]
for kind,text in sections:
    if kind=='title': doc.add_paragraph(text,'Title'); md.append('# '+text)
    elif kind=='subtitle': doc.add_paragraph(text,'Subtitle'); md.append(text)
    elif kind=='h': doc.add_paragraph(text,'Heading 1'); md.append('## '+text)
    elif kind=='break': doc.add_page_break()
    elif kind=='image':
        pic=doc.add_picture(str(ROOT/'resultados'/'phillips_estatico.png'),width=Cm(17))
        pic._inline.docPr.set('descr','Recorrido de inflación y desocupación de Chile de enero de 2024 a junio de 2026, con áreas proporcionales al crecimiento anual del IR real.')
        md.append('![Gráfico de Phillips](../resultados/phillips_estatico.png)')
    else:
        p=doc.add_paragraph(text)
        if kind in ('caption','source'):
            for run in p.runs: run.font.size=Pt(8.5)
            p.paragraph_format.space_after=Pt(5)
        md.append(text)
for tree in (doc.element, doc.styles.element):
    for border in list(tree.xpath('//w:pBdr')):
        border.getparent().remove(border)
doc.core_properties.title=sections[0][1]
doc.core_properties.subject='Análisis descriptivo de inflación, desocupación y remuneraciones reales en Chile'
doc.core_properties.author=''
doc.save(out/'Articulo_LinkedIn_Curva_Phillips.docx')
(out/'articulo_linkedin.md').write_text('\n\n'.join(md)+'\n',encoding='utf8')
print('Artículo creado')

