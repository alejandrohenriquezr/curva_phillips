from pathlib import Path
import json
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parent
out=ROOT/'informe'; out.mkdir(exist_ok=True)
sections=[('title', 'Inflación y empleo en Chile vistos a través de la curva de Phillips'),
 ('subtitle', 'Enero de 2024 a junio de 2026 | Análisis para LinkedIn'),
 ('p',
  'Entre enero de 2024 y junio de 2026, la relación contemporánea entre inflación y desocupación en esta muestra chilena fue prácticamente '
  'nula. La correlación de las 30 observaciones es −0,011. El resultado invita a mirar la trayectoria de ambas variables y las '
  'remuneraciones reales, sin convertir una asociación estadística de corto plazo en una conclusión causal.'),
 ('p',
  'El gráfico combina cuatro dimensiones: desocupación en el eje horizontal, inflación anual en el vertical, variación anual del IR real '
  'en el área y crecimiento interanual del promedio de tres meses del IMACEC en el color. Naranja indica caída de actividad, un tono claro '
  'indica cercanía a cero y azul indica crecimiento. El panel inferior muestra el IMACEC desestacionalizado.'),
 ('image', ''),
 ('caption',
  'Área: magnitud del crecimiento anual del IR real. Color: variación interanual del promedio móvil 3m del IMACEC original, centrado como '
  'la ENE. Panel: nivel mensual desestacionalizado. Referencias: inflación 3% y punto medio NAIRU histórico 8,25% [5].'),
 ('break', ''),
 ('h', 'Una trayectoria que cambia de dirección'),
 ('p',
  'El punto inicial combina una inflación anual de 3,8%, una desocupación de 8,50% y un aumento anual del IR real de 2,78%. En junio de '
  '2026, el punto final registra 4,3%, 9,53% y 3,27%, respectivamente. Entre los extremos, la desocupación aumenta 1,03 puntos '
  'porcentuales y la inflación 0,5 puntos. Sin embargo, esa comparación omite los cambios de dirección que aparecen durante el recorrido.'),
 ('p',
  'El último punto se sitúa arriba y a la derecha del cruce de referencias: la inflación de 4,3% supera la meta en 1,30 puntos '
  'porcentuales y la desocupación de 9,53% está 1,28 puntos sobre el punto medio histórico de 8,25%. Estas distancias describen posiciones '
  'en el gráfico; no identifican por sí solas un shock de oferta ni una brecha cíclica oficial.'),
 ('h', 'Qué puede decir una curva de Phillips'),
 ('p',
  'La intuición económica de la curva de Phillips relaciona las presiones inflacionarias con la holgura de la economía. Un mercado laboral '
  'más estrecho puede aumentar las presiones salariales y de costos. Pero la inflación observada también responde a expectativas, precios '
  'importados, tipo de cambio, productividad y perturbaciones de oferta. El análisis del Banco Central sobre la evidencia chilena subraya '
  'la necesidad de una especificación más amplia que una nube de inflación y desempleo [4].'),
 ('p',
  'La correlación cercana a cero no demuestra que la relación económica haya desaparecido. Puede reflejar fuerzas simultáneas, rezagos o '
  'una muestra breve. Tampoco permite estimar una NAIRU propia ni atribuir el movimiento a una decisión monetaria.'),
 ('h', 'El salario real agrega una dimensión relevante'),
 ('p',
  'El IR real crece en términos anuales en los 30 meses comunes, con variaciones entre 1,40% y 3,74%. En junio de 2026, el aumento de '
  '3,27% convive con una desocupación elevada respecto del comienzo de la muestra. Esta coexistencia recuerda que el poder adquisitivo de '
  'la remuneración por hora y la posibilidad de acceder a un empleo son dimensiones distintas del bienestar laboral.'),
 ('p',
  'El indicador del INE mide remuneraciones reales por hora en su ámbito de cobertura. No equivale al ingreso laboral total de los '
  'hogares: no incorpora del mismo modo el desempleo, los cambios de horas trabajadas o todas las formas de ocupación. Además, el IR real '
  'utiliza el IPC como deflactor. No es una variable estadísticamente independiente de la inflación y no debe volver a descontársele el '
  'IPC [3].'),
 ('break', ''),
 ('h', 'Leer el gráfico con sus límites'),
 ('p',
  'La ENE entrega trimestres móviles que comparten dos meses entre observaciones consecutivas. Aquí se utiliza el mes central, respetando '
  'la convención de los archivos: junio de 2026 corresponde a mayo–julio de 2026. El ejercicio es retrospectivo; ese punto no representa '
  'lo que se conocía en tiempo real durante junio. El cuaderno permite contrastar la asignación al mes final.'),
 ('p',
  'La intersección de las cuatro variables conserva 30 meses, de enero de 2024 a junio de 2026. El IMACEC llega hasta julio de 2026 y '
  'permite calcular el promedio centrado en junio. No se rellenan faltantes ni se prolonga artificialmente la animación. Para inflación se '
  'utiliza exclusivamente el IPC General y su variación anual publicada.'),
 ('p',
  'La ENE, el IPC, el IR y el IMACEC usado para el color no están desestacionalizados; el panel inferior sí utiliza la serie ajustada '
  'oficial y los cambios a doce meses comparten información entre períodos. Estas dependencias, junto con el reducido tamaño de la '
  'muestra, impiden tratar los puntos como observaciones independientes para una inferencia simple. Una investigación econométrica '
  'requeriría un horizonte más largo, expectativas de inflación, controles de oferta, rezagos y una estrategia explícita de '
  'identificación.'),
 ('h', 'Qué significan las líneas de referencia'),
 ('p',
  'La minuta del BCCh citada en el IPoM de diciembre de 2024 presenta un rango NAIRU de 8,0–8,5% para el tercer trimestre de 2024, '
  'mediante filtros de Kalman multivariados y modelos VAR [5]. Usamos su punto medio, 8,25%, como convención visual propia, no como '
  'estimación puntual oficial ni como cifra de junio de 2026. La banda representa dispersión entre estimaciones, no un intervalo de '
  'confianza.'),
 ('p',
  'La referencia es histórica y utiliza desempleo desestacionalizado, mientras nuestros puntos usan ENE sin ajuste estacional. No '
  'suponemos que la NAIRU haya permanecido constante ni la equiparamos automáticamente a la tasa natural de largo plazo. Por su parte, la '
  'meta del 3% corresponde a un horizonte de dos años [6]; no exige que la inflación de cada mes sea exactamente 3%. Estas referencias '
  'orientan la lectura, pero no bastan para recomendar una tasa de interés.'),
 ('break', ''),
 ('h', 'La actividad aporta contexto a la relación entre inflación y empleo'),
 ('p',
  'El crecimiento interanual del promedio móvil del IMACEC original pasa de aproximadamente 3,20% en enero de 2024 a −0,30% en junio de '
  '2026. Su máximo en la muestra es 4,26% en abril de 2025. Los cinco puntos de febrero a junio de 2026 presentan tasas negativas, con un '
  'mínimo de −0,77% en abril. Los colores se acercan al tono claro porque estas contracciones son pequeñas frente al máximo positivo; la '
  'escala se mantiene simétrica alrededor de cero.'),
 ('p',
  'El último punto combina actividad trimestral móvil ligeramente inferior a la de un año antes, inflación de 4,3%, desocupación de 9,53% '
  'y crecimiento del IR real de 3,27%. Es una combinación compatible con actividad débil y presiones de precios persistentes, pero no '
  'identifica sus causas. Rezagos, oferta, composición sectorial, productividad y participación laboral pueden alterar el vínculo entre '
  'producción, empleo y salarios. El IMACEC no mide por sí solo la brecha de producto ni determina la NAIRU.'),
 ('p',
  'El panel permite separar el nivel de actividad de su crecimiento interanual. El IMACEC desestacionalizado sube de 113,1 en mayo a 113,8 '
  'en junio de 2026, aproximadamente 0,62% mensual, aunque el promedio mayo–julio cae 0,30% frente a un año antes. No hay contradicción: '
  'se comparan frecuencias y ventanas distintas. El dato de julio entra en el promedio centrado en junio, pero no extiende el panel más '
  'allá de las fechas de la muestra.'),
 ('h', 'Fórmulas y decisiones de medición'),
 ('p',
  'Sea Iₜ el IMACEC original y Sₜ el desestacionalizado, ambos con promedio 2018=100. Promedio centrado: Īₜ = (Iₜ₋₁ + Iₜ + Iₜ₊₁) / 3. '
  'Color: gₜ = 100 × (Īₜ / Īₜ₋₁₂ − 1). Se divide el promedio de niveles entre el de un año antes; no se promedian tasas. Variación mensual '
  'del panel: mₜ = 100 × (Sₜ / Sₜ₋₁ − 1); la línea representa Sₜ, no mₜ.'),
 ('p',
  'Desocupación: uₜ = 100 × desocupados / fuerza de trabajo. Inflación: πₜ = 100 × (IPCₜ / IPCₜ₋₁₂ − 1), usando la variación publicada. IR '
  'real: rₜ = 100 × (IRᴿₜ / IRᴿₜ₋₁₂ − 1). Área: Aₜ = k × |rₜ|, con k fijo; su signo figura en el tooltip. Color: L = máximo de |gₜ| en la '
  'muestra (mínimo 0,1); zₜ = (gₜ + L) / (2L), con naranja en −L, claro en 0 y azul en +L.'),
 ('p',
  'Referencia vertical: u* = (8,0 + 8,5) / 2 = 8,25%. Distancias: uₜ − u* y πₜ − 3, en puntos porcentuales. El promedio centrado requiere '
  'conocer el mes siguiente. Las tasas IMACEC se calculan con índices BDE redondeados a un decimal y son aproximadas; las series oficiales '
  'pueden revisarse [7]. Código, fórmulas y metadatos permiten reproducir el corte local. La correlación descriptiva es la de Pearson: ρ = '
  'Σ[(uₜ − ū)(πₜ − π̄)] / √{Σ(uₜ − ū)² × Σ(πₜ − π̄)²}, con medias calculadas sobre los 30 meses comunes.'),
 ('break', ''),
 ('h', 'Fuentes y reproducibilidad'),
 ('source',
  '[1] INE. Encuesta Nacional de Empleo, series vigentes. '
  'https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion'),
 ('source',
  '[2] INE. Índice de Precios al Consumidor. '
  'https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor'),
 ('source',
  '[3] INE. Índices de Remuneraciones y Costos Laborales; serie empalmada del IR real. '
  'https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales'),
 ('source',
  '[4] Banco Central de Chile. IPoM, junio de 2016, recuadro sobre evidencia de la curva de Phillips para Chile. '
  'https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6'),
 ('source',
  '[5] Banco Central de Chile. Minutas citadas en el IPoM diciembre de 2024. Holguras en el mercado laboral, secciones 1 y 4, páginas 34 y '
  '38 del PDF. '
  'https://www.bcentral.cl/documents/33528/6735463/Minutas%2Bcitadas%2Ben%2Bel%2BIPoM%2Bdiciembre%2B2024.pdf/d24985ae-cb5e-2f03-4499-ecfad3d86ade'),
 ('source',
  '[6] Banco Central de Chile. IPoM junio de 2026. La meta de inflación y la Tasa de Política Monetaria, página 3 del PDF. '
  'https://www.bcentral.cl/documents/33528/8413153/IPoM%2Bjunio%2B2026.pdf/93388589-0929-4ad6-b166-10981ca34946'),
 ('source',
  '[7] Banco Central de Chile. BDE, IMACEC empalmado original y desestacionalizado, índices 2018=100. Series F032.IMC.IND.Z.Z.EP18.Z.Z.0.M '
  'y F032.IMC.IND.Z.Z.EP18.Z.Z.1.M. Actualización BDE 1 de septiembre de 2026; descarga 23 de septiembre de 2026. '
  'https://www.bcentral.cl/areas/estadisticas/imacec'),
 ('source',
  'Cálculos propios con los CSV del INE y del BCCh incluidos en el proyecto. Corte INE recibido el 22 de septiembre de 2026; IMACEC '
  'descargado el 23 de septiembre de 2026. Código, datos y gráfico: https://github.com/alejandrohenriquezr/curva_phillips')]

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
        pic._inline.docPr.set('descr','Recorrido de inflación y desocupación de Chile de enero de 2024 a junio de 2026, con áreas proporcionales al crecimiento anual del IR real, colores por IMACEC y panel temporal desestacionalizado.')
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

