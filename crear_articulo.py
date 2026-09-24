from pathlib import Path
import json
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parent
out=ROOT/'informe'; out.mkdir(exist_ok=True)
summary=json.loads((ROOT/'resultados'/'resumen_economico.json').read_text(encoding='utf8'))
# Las cifras proceden del mismo resumen que exporta el cuaderno.
# La interpretación histórica se revisa si cambia la cobertura o el corte.
if (summary['desde'],summary['hasta']) != ('2011-01','2026-06'):
    raise ValueError('El corte cambió: revisar el análisis económico antes de regenerar el artículo.')
def f(value,digits=2): return f'{value:.{digits}f}'.replace('-', '−').replace('.', ',')
n=summary['n']; first=summary['inicio']; last=summary['final']; ext=summary['extremos']; obs=summary['observaciones']
periods=summary['subperiodos']
period_text='; '.join(f"{p['periodo']}: {f(p['correlacion'],3)} ({p['n']} meses)" for p in periods)
sections=[
('title','Inflación empleo y actividad en Chile entre 2011 y 2026'),
('subtitle','Enero de 2011 a junio de 2026 | Análisis para LinkedIn'),
('p',f"Ampliar el horizonte cambia la lectura de la curva de Phillips. En los {n} meses comunes, la correlación contemporánea entre inflación y desocupación es {f(summary['correlacion'],3)}, una asociación positiva débil. En 2024–2026 era prácticamente nula. La comparación por períodos muestra que este promedio no describe una relación estable ni permite inferir causalidad."),
('p','La visualización conecta inflación, empleo, remuneraciones reales y actividad: desocupación en el eje horizontal, inflación anual en el vertical, magnitud del cambio anual del IR real en el área y crecimiento interanual del promedio móvil de tres meses del IMACEC en el color. Naranja indica caída de actividad, claro cercanía a cero y azul crecimiento. El panel inferior muestra el nivel desestacionalizado.'),
('image',''),
('caption','Área proporcional al valor absoluto del IR real anual; su signo se consulta en el gráfico interactivo. Color del IMACEC con escala simétrica fija. ENE e IMACEC promedio 3m alineados al mes central. Referencias: inflación 3% y punto medio histórico NAIRU 8,25% [5–7].'),
('break',''),
('h','Lo que cambia al incorporar quince años de historia'),
('p',f"En {first['mes']}, el punto inicial registra inflación de {f(first['ipc_anual'],1)}%, desocupación de {f(first['desocupacion'])}% y aumento anual del IR real de {f(first['ir_real_anual'])}%. En {last['mes']}, los valores son {f(last['ipc_anual'],1)}%, {f(last['desocupacion'])}% y {f(last['ir_real_anual'])}%. La comparación de extremos oculta episodios con dinámicas muy distintas."),
('p',f"La desocupación alcanza su máximo muestral de {f(ext['desocupacion']['max']['desocupacion'])}% en {ext['desocupacion']['max']['mes']}, cuando la inflación es {f(ext['desocupacion']['max']['ipc_anual'],1)}%. El máximo de inflación llega después: {f(ext['ipc_anual']['max']['ipc_anual'],1)}% en {ext['ipc_anual']['max']['mes']}, con desempleo de {f(ext['ipc_anual']['max']['desocupacion'])}%. Esta separación temporal desaconseja interpretar la nube como un intercambio contemporáneo fijo."),
('h','El promedio agregado no representa todos los períodos'),
('p',f"Las correlaciones descriptivas por ventanas predefinidas son: {period_text}. El último período termina en junio de 2026. Estos cortes son una forma de comparar episodios; no son regímenes identificados econométricamente."),
('p','Que las tres correlaciones parciales sean negativas y la agregada positiva no es un error. La covariación total combina los movimientos dentro de cada período con las diferencias entre sus promedios. Por eso, mezclar episodios puede cambiar el signo de la asociación. No corresponde interpretar +0,124 como evidencia de que un aumento del desempleo cause más inflación, ni las correlaciones negativas como prueba causal de una curva de Phillips.'),
('h','La pregunta económica sigue abierta'),
('p','La curva de Phillips vincula presiones inflacionarias con holgura, expectativas y otros determinantes. Una comparación útil requiere controlar oferta, precios externos, productividad y rezagos [4]. La muestra ampliada permite observar más episodios, pero su extensión no resuelve por sí sola la identificación. Las tasas anuales y los trimestres móviles comparten información entre observaciones; la inflación y el empleo también responden a fuerzas comunes.'),
('break',''),
('h','El salario real también puede retroceder'),
('p',f"El IR real presenta caídas interanuales en {summary['ir_negativos']} de {n} meses. Su mínimo es {f(ext['ir_real_anual']['min']['ir_real_anual'])}% en {ext['ir_real_anual']['min']['mes']} y su máximo {f(ext['ir_real_anual']['max']['ir_real_anual'])}% en {ext['ir_real_anual']['max']['mes']}. La conclusión anterior de crecimiento en todos los meses solo era válida para 2024–2026. La ampliación revela pérdidas de poder adquisitivo que ese corte reciente no mostraba."),
('p','El área usa el valor absoluto: una caída salarial grande también produce una burbuja grande. El color representa actividad, no el signo del salario. El IR mide remuneraciones reales por hora en su cobertura y no equivale al ingreso total de los hogares ni incorpora el desempleo de la misma forma. Ya está deflactado por IPC: no debe descontarse nuevamente la inflación [3].'),
('h','Contracción rebote y efecto de base en la actividad'),
('p',f"El crecimiento interanual del promedio móvil del IMACEC alcanza {f(ext['imacec_promedio_anual']['min']['imacec_promedio_anual'])}% en {ext['imacec_promedio_anual']['min']['mes']} y {f(ext['imacec_promedio_anual']['max']['imacec_promedio_anual'])}% en {ext['imacec_promedio_anual']['max']['mes']}. Hay {summary['imacec_negativos']} meses con tasas negativas. El rebote interanual debe leerse junto con el nivel desestacionalizado: crecer respecto de una base deprimida no equivale a estar por encima de una trayectoria potencial."),
('p','La escala simétrica conserva los extremos históricos, por lo que variaciones pequeñas aparecen próximas al tono claro. La barra lateral y el tooltip permiten distinguirlas de cero. El IMACEC mide actividad; no estima por sí solo una brecha de producto ni la NAIRU.'),
('h','Qué muestra el último punto'),
('p',f"En {last['mes']}, el promedio móvil del IMACEC varía {f(last['imacec_promedio_anual'])}% interanual, mientras su nivel desestacionalizado es {f(last['imacec_sa'],1)} y su cambio mensual {f(last['imacec_sa_mensual'])}%. La actividad trimestral móvil ligeramente inferior a la de un año antes coexiste con inflación de {f(last['ipc_anual'],1)}%, desocupación de {f(last['desocupacion'])}% y crecimiento del IR real de {f(last['ir_real_anual'])}%. Frecuencias distintas pueden dar señales diferentes; esta combinación no identifica automáticamente un shock ni prescribe una tasa de interés."),
('break',''),
('h','Fechas cobertura y referencias'),
('p',f"El IPC histórico tiene niveles desde diciembre de 2009, pero las tasas anuales publicadas y el IR real anual disponibles comienzan en enero de 2011. La intersección conserva {n} meses hasta junio de 2026. Junio usa ENE e IMACEC promedio de mayo–julio: requiere conocer julio y es retrospectivo. No se rellenan faltantes. El panel muestra el IMACEC desestacionalizado mensual hasta la misma fecha central."),
('p','La línea vertical de 8,25% es nuestro punto medio del rango 8,0–8,5% para 2024-T3, publicado en la minuta del IPoM de diciembre de 2024 mediante estimaciones Kalman multivariadas y VAR [5]. No es una NAIRU oficial de 2026 ni de cada año desde 2011. La banda refleja dispersión entre estimaciones, no un intervalo de confianza. La referencia usa desempleo desestacionalizado, a diferencia de los puntos. Las distancias son ilustrativas, no brechas oficiales. La meta de inflación del 3% se refiere al horizonte de dos años [6].'),
('h','Fórmulas utilizadas'),
('p','Sean Iₜ el IMACEC original y Sₜ el desestacionalizado, ambos con promedio 2018=100. Promedio centrado: Īₜ = (Iₜ₋₁ + Iₜ + Iₜ₊₁) / 3. Color: gₜ = 100 × (Īₜ / Īₜ₋₁₂ − 1). Se comparan promedios de niveles, no promedios de tasas. Con alineación al mes final, la ventana es t−2, t−1 y t. Variación mensual: mₜ = 100 × (Sₜ / Sₜ₋₁ − 1); el panel representa Sₜ.'),
('p','Desocupación: uₜ = 100 × desocupados / fuerza de trabajo. Inflación: πₜ = 100 × (IPCₜ / IPCₜ₋₁₂ − 1), usando la tasa publicada. IR real: rₜ = 100 × (IRᴿₜ / IRᴿₜ₋₁₂ − 1). Área: Aₜ = k × |rₜ|. Color: L = máximo de |gₜ| en la muestra (mínimo 0,1); zₜ = (gₜ + L) / (2L). Naranja en −L, claro en 0 y azul en +L; escala fija en todos los fotogramas.'),
('p',f"Referencia vertical: u* = (8,0 + 8,5) / 2 = 8,25%. Distancias: uₜ − u* y πₜ − 3, en puntos porcentuales. Correlación de Pearson: ρ = Σ[(uₜ − ū)(πₜ − π̄)] / √{{Σ(uₜ − ū)² × Σ(πₜ − π̄)²}}. Las medias corresponden a cada ventana; la muestra completa tiene {n} observaciones. No se presentan pruebas de significancia ni una estimación causal."),
('p','Las tasas IMACEC se calculan con índices BDE publicados con un decimal y son aproximadas; las fuentes pueden revisarse [7]. El resumen numérico y las correlaciones se exportan con el cuaderno. El informe toma sus cifras de ese resumen para evitar diferencias entre tablas, gráficos y texto.'),
('break',''),('h','Fuentes y reproducibilidad')]
sections += [('source',
  '[1] INE. Encuesta Nacional de Empleo, series vigentes. '
  'https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion'),
 ('source',
  '[2] INE. IPC histórico empalmado, diciembre de 2009 a la fecha, base 2023. Variación anual publicada desde enero de 2011. URL exacta en '
  'extractors/ipc_extractor.py. https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor'),
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
  'Cálculos propios con los CSV locales del INE y del BCCh. IPC histórico empalmado incorporado en septiembre de 2026; fechas, cobertura y '
  'hashes en resultados. Código y datos: https://github.com/alejandrohenriquezr/curva_phillips')]

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
        pic._inline.docPr.set('descr','Recorrido de inflación y desocupación de Chile de enero de 2011 a junio de 2026, con áreas proporcionales al crecimiento anual del IR real, colores por IMACEC y panel temporal desestacionalizado.')
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

