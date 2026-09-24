from salidas import archivo, FECHA
import os
import json
from pathlib import Path
root=Path(__file__).resolve().parent
cells=[]
def md(text):
    for name in ['phillips_animado.html','phillips_estatico.png','datos_phillips.csv','cobertura.csv','meses_excluidos.csv','fuentes_sha256.json']:
        text=text.replace(name,archivo(name))
    cells.append(dict(cell_type='markdown',metadata={},source=text.splitlines(True)))
def code(text): cells.append(dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=text.splitlines(True)))
md('''# Curva de Phillips de Chile\n## Inflación, desocupación y remuneraciones reales\n\nLa muestra histórica común abarca enero de 2011 a junio de 2026 (186 meses). El IPC empalmado tiene niveles desde diciembre de 2009, pero sus tasas anuales publicadas y el IR anual comienzan en enero de 2011.\n\nEste cuaderno usa los cuatro CSV del INE y del Banco Central incluidos en la carpeta. **No necesitas descargar datos para ejecutarlo.**\n\n**Primera vez:** abre `ABRIR_JUPYTER.bat`, espera a que aparezca el navegador y selecciona **Run → Run All Cells** (Ejecutar todas las celdas). También puedes ejecutar cada celda con **Shift + Enter**. El asterisco `[*]` significa que Python está trabajando.\n\nEl gráfico al final incluye **Play**, pausa, reinicio y un selector mensual. Cada fotograma mantiene el rastro de los meses anteriores. El borde distingue el año fuera de pandemia; durante pandemia conserva el gris segmentado. El panel inferior incluye una leyenda para IMACEC e IPC. La versión HTML guardada en `resultados` funciona sin Jupyter y sin conexión.\n''')
code(f'''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, HTML
import importlib
import os
os.environ['PHILLIPS_FECHA'] = '{FECHA}'
# Cambia a 'original' o 'sa' y vuelve a ejecutar todas las celdas.
IPC_AJUSTE = '{os.environ.get('PHILLIPS_IPC','original')}'
os.environ['PHILLIPS_IPC'] = IPC_AJUSTE
import salidas, graficos
importlib.reload(salidas)
importlib.reload(graficos)
import phillips
importlib.reload(phillips)
from phillips import load_data, build_figure, export_results, static_chart, economic_summary, figure_html
print('Python:', sys.version.split()[0])
print('Proyecto:', Path.cwd().name)
''')
md('''## Qué representa cada variable\n\n- **Eje horizontal:** tasa de desocupación nacional de la ENE, en porcentaje, sin ajuste estacional. Es un trimestre móvil, no una estimación mensual independiente.\n- **Eje vertical:** variación a doce meses del **IPC General**, publicada en el CSV en modo `original` o calculada sobre el índice ajustado X-13/SEATS en modo `sa`. No se promedian divisiones del IPC ni se calcula un cambio a doce meses a partir de índices con bases distintas.\n- **Área de la burbuja:** proporcional al valor absoluto de la variación anual del índice de remuneraciones **real**, por hora. El signo del IR se consulta al pasar el cursor; el color representa el IMACEC, no el salario real. Un centro oscuro permite localizar una variación exactamente cero sin asignarle un área económica ficticia.\n\nEl IR ya está deflactado por IPC; restar nuevamente la inflación sería un error. Se usa `var_12`, contrastada con los niveles separados por doce meses.\n\n**Fechas:** seguimos la convención de los CSV: ENE se asigna al mes central (por ejemplo, mayo–julio corresponde a junio). Esto sirve para una comparación retrospectiva; el punto no representa información disponible en tiempo real en junio. La fecha final del trimestre también queda en la tabla.\n''')
code('''datos, cobertura, excluidos = load_data(ipc_ajuste=IPC_AJUSTE)
display(cobertura)
print(f'Período común: {datos.mes.iloc[0]} a {datos.mes.iloc[-1]} · {len(datos)} observaciones')
print(f'Meses excluidos por falta de alguna variable: {len(excluidos)}')
display(datos[['mes','Trimestre','fecha_final_ene','desocupacion','ipc_anual','ir_real_anual','imacec_promedio_anual','imacec_sa_anual','imacec_acumulado_anual','estado_ir']].tail(12).round(3))
''')
md('''## Elegir IPC original o desestacionalizado

En la primera celda cambia `IPC_AJUSTE` a `original` o `sa` y ejecuta todas las celdas. El modo SA requiere el ejecutable oficial: `python instalar_x13.py`. X-13 ajusta el nivel empalmado completo y calcula después tasas mensuales y de 12 meses. Exporta `ipc_comparacion.csv`, especificación y diagnóstico. Es experimental, revisable y no oficial del INE; no ajusta ENE ni IR. El indicador de diciembre usa el IPC seleccionado. Los archivos SA agregan `ipc_sa` para no reemplazar los originales.
''')
md('''## Comprobaciones antes de graficar\n\nEl código exige fechas únicas, uniones uno a uno, valores finitos y continuidad mensual. Nunca reemplaza faltantes por cero. La tabla `meses_excluidos.csv` permite auditar la intersección de las series. El archivo `fuentes_sha256.json` identifica la versión exacta de los CSV utilizados.\n''')
code('''assert not datos.fecha.duplicated().any()
assert datos[['desocupacion','ipc_anual','ir_real_anual','imacec_promedio_anual','imacec_sa']].notna().all().all()
assert datos.desocupacion.between(0,100).all()
print('Validaciones de las cuatro variables: correctas')
display(datos[['desocupacion','ipc_anual','ir_real_anual','imacec_promedio_anual','imacec_sa']].describe().round(3))
''')
md('## Referencias de inflación y desempleo\n\nLa línea horizontal señala la **meta de inflación del 3%** del BCCh, definida para un horizonte de dos años; no exige que cada dato mensual sea 3%.\n\nLa banda vertical representa el rango **8,0–8,5% para 2024-T3** publicado en la minuta *Holguras en el mercado laboral*, citada en el IPoM de diciembre de 2024 (páginas 34 y 38 del PDF). Reúne estimaciones mediante filtros de Kalman multivariados y modelos VAR. La línea **8,25%** es el punto medio calculado por este proyecto, **no una estimación puntual oficial ni una cifra del IPoM de junio de 2026**. La banda no es un intervalo de confianza.\n\nEs una referencia histórica fija, no una trayectoria estimada para 2011–2026. Además, la referencia utiliza desempleo desestacionalizado y nuestros puntos usan ENE sin ajuste estacional: las distancias son ilustrativas, no brechas cíclicas oficiales. NAIRU y tasa natural de largo plazo no son conceptos necesariamente idénticos.\n\nFuentes: [minuta BCCh diciembre de 2024](https://www.bcentral.cl/documents/33528/6735463/Minutas%2Bcitadas%2Ben%2Bel%2BIPoM%2Bdiciembre%2B2024.pdf/d24985ae-cb5e-2f03-4499-ecfad3d86ade) y [IPoM junio de 2026, meta de inflación, página 3](https://www.bcentral.cl/documents/33528/8413153/IPoM%2Bjunio%2B2026.pdf/93388589-0929-4ad6-b166-10981ca34946). Parámetros y trazabilidad: `referencias_macro.json` y `fuentes/REFERENCIAS.md`.\n')
md((root/'METODOLOGIA.md').read_text(encoding='utf8').replace('# IMACEC y fórmulas del gráfico','## IMACEC y fórmulas del gráfico',1))
md('''## Gráfico animado\n\nPulsa **Play** para recorrer la muestra y **Pausa** para detenerla. Puedes arrastrar el selector temporal; **Reiniciar** vuelve al primer mes. Pasa el cursor por una burbuja para ver las cifras y el trimestre de empleo.\n\nLos ejes, la escala de áreas y la escala divergente del color permanecen fijos durante toda la animación. El panel inferior compara IMACEC desestacionalizado e IPC en variación a 12 meses, con cierres anuales en diciembre. Su cursor está sincronizado con el mes activo. Cada enero lleva fecha y la ventana Covid tiene bordes segmentados. Al volver a una fecha anterior, el rastro también retrocede.\n''')
code('''figura = build_figure(datos)
export_results(datos, cobertura, excluidos, figura)
static_chart(datos)
# HTML embebido: evita depender de extensiones de Plotly o de una conexión a internet.
display(HTML(figure_html(figura, full_html=False)))
''')
md('''## Lectura económica y sensibilidad de fechas\n\nUna nube de puntos es una descripción, no una estimación causal de la curva de Phillips. La inflación depende también de expectativas, oferta, precios externos, tipo de cambio y política monetaria. La variación del IR real comparte el IPC como deflactor, por lo que no constituye una variable independiente de la inflación.\n\nLa comparación por subperíodos muestra cómo cambia la asociación según la ventana elegida. La ampliación incorpora caídas y rebotes de actividad y episodios de alta inflación. Las burbujas claras pueden representar variaciones pequeñas respecto de los extremos históricos, no necesariamente cero.\n\nLa correlación siguiente usa niveles contemporáneos, sin controles ni correcciones por autocorrelación. Los trimestres móviles se superponen y las tasas anuales también comparten meses. Por eso no se presentan pruebas de significancia ni recomendaciones de tasas de interés. Tampoco se estima una NAIRU propia; se incorpora únicamente la referencia histórica externa descrita arriba.\n\nPara explorar la convención temporal, también se calcula la correlación con ENE asignada al mes final, restringiendo ambas alternativas a las mismas fechas. Este contraste cambia el emparejamiento, no el dato original.\n''')
code('''alternativa, _, _ = load_data(alignment='final', ipc_ajuste=IPC_AJUSTE)
fechas_comunes = datos.fecha[datos.fecha.isin(alternativa.fecha)]
a = datos[datos.fecha.isin(fechas_comunes)]
b = alternativa[alternativa.fecha.isin(fechas_comunes)]
resumen = pd.DataFrame([
    {'alineación': 'Mes central', 'n': len(a), 'correlación IPC-desocupación': a.desocupacion.corr(a.ipc_anual)},
    {'alineación': 'Mes final', 'n': len(b), 'correlación IPC-desocupación': b.desocupacion.corr(b.ipc_anual)}
])
display(resumen.round(3))
estadisticas = economic_summary(datos)
print(f"Correlación muestra completa: {estadisticas['correlacion']:.3f}")
display(pd.DataFrame(estadisticas['subperiodos']).round(3))
print('Subperíodos descriptivos predefinidos; no son regímenes estimados ni pruebas causales.')
display(datos[['mes','distancia_meta_ipc_pp','distancia_referencia_nairu_pp']].tail(1).round(3))
display(datos.groupby(datos.fecha.dt.year)[['desocupacion','ipc_anual','ir_real_anual','imacec_promedio_anual','imacec_sa']].mean().round(3))
print('Advertencia: el último año puede ser parcial; no comparar promedios como años completos.')
''')
md('''## Archivos de salida y actualización\n\n- `resultados/phillips_animado.html`: gráfico interactivo independiente.\n- `resultados/phillips_estatico.png`: imagen para el artículo.\n- `resultados/datos_phillips.csv`: datos de cada burbuja.\n- `resultados/cobertura.csv` y `meses_excluidos.csv`: auditoría de cobertura.\n\nPara volver a trabajar, abre el mismo `.bat`. Para actualizar las fuentes, revisa primero los extractores y ejecuta `python main.py` desde el entorno del proyecto. Esto sustituye los CSV locales con la descarga vigente. Guarda una copia antes si quieres conservar el corte original y luego ejecuta todas las celdas. El informe Word es una fotografía del corte analizado y debe revisarse si cambian los datos.\n\n## Fuentes y referencias\n\n- [INE — Ocupación y desocupación](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion).\n- [INE — IPC](https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor).\n- [INE — Remuneraciones y costos laborales](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales).\n- [Banco Central de Chile — IPoM junio de 2016, evidencia de la curva de Phillips](https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6).\n\nLas URL exactas de los tabulados están en los extractores originales del proyecto.\n''')
nb=dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3 (ipykernel)',language='python',name='python3'),language_info=dict(name='python',version='3.13')),nbformat=4,nbformat_minor=5)
for i,c in enumerate(cells): c['id']=f'phillips-{i:02}'
(root/archivo('Curva_de_Phillips.ipynb')).write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf8')
print('Cuaderno creado')

