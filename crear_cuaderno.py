import json
from pathlib import Path
root=Path(__file__).resolve().parent
cells=[]
def md(text): cells.append(dict(cell_type='markdown',metadata={},source=text.splitlines(True)))
def code(text): cells.append(dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=text.splitlines(True)))
md('''# Curva de Phillips de Chile\n## Inflación, desocupación y remuneraciones reales\n\nEste cuaderno usa los tres CSV incluidos en la carpeta. **No necesitas descargar datos para ejecutarlo.**\n\n**Primera vez:** abre `ABRIR_JUPYTER.bat`, espera a que aparezca el navegador y selecciona **Run → Run All Cells** (Ejecutar todas las celdas). También puedes ejecutar cada celda con **Shift + Enter**. El asterisco `[*]` significa que Python está trabajando.\n\nEl gráfico al final incluye **Play**, pausa, reinicio y un selector mensual. Cada fotograma mantiene el rastro de los meses anteriores. La versión HTML guardada en `resultados` funciona sin Jupyter y sin conexión.\n''')
code('''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, HTML
from phillips import load_data, build_figure, export_results, static_chart
print('Python:', sys.version.split()[0])
print('Proyecto:', Path.cwd().name)
''')
md('''## Qué representa cada variable\n\n- **Eje horizontal:** tasa de desocupación nacional de la ENE, en porcentaje, sin ajuste estacional. Es un trimestre móvil, no una estimación mensual independiente.\n- **Eje vertical:** variación a doce meses del **IPC General**, publicada en el CSV. No se promedian divisiones del IPC ni se calcula un cambio a doce meses a partir de índices con bases distintas.\n- **Área de la burbuja:** proporcional al valor absoluto de la variación anual del índice de remuneraciones **real**, por hora. Verde indica aumento y naranja caída. Un centro oscuro permite localizar una variación exactamente cero sin asignarle un área económica ficticia.\n\nEl IR ya está deflactado por IPC; restar nuevamente la inflación sería un error. Se usa `var_12`, contrastada con los niveles separados por doce meses.\n\n**Fechas:** seguimos la convención de los CSV: ENE se asigna al mes central (por ejemplo, mayo–julio corresponde a junio). Esto sirve para una comparación retrospectiva; el punto no representa información disponible en tiempo real en junio. La fecha final del trimestre también queda en la tabla.\n''')
code('''datos, cobertura, excluidos = load_data()
display(cobertura)
print(f'Período común: {datos.mes.iloc[0]} a {datos.mes.iloc[-1]} · {len(datos)} observaciones')
print(f'Meses excluidos por falta de alguna variable: {len(excluidos)}')
display(datos[['mes','Trimestre','fecha_final_ene','desocupacion','ipc_anual','ir_real_anual','estado_ir']].tail(12).round(3))
''')
md('''## Comprobaciones antes de graficar\n\nEl código exige fechas únicas, uniones uno a uno, valores finitos y continuidad mensual. Nunca reemplaza faltantes por cero. La tabla `meses_excluidos.csv` permite auditar la intersección de las series. El archivo `fuentes_sha256.json` identifica la versión exacta de los CSV utilizados.\n''')
code('''assert not datos.fecha.duplicated().any()
assert datos[['desocupacion','ipc_anual','ir_real_anual']].notna().all().all()
assert datos.desocupacion.between(0,100).all()
print('Validaciones de las tres series: correctas')
display(datos[['desocupacion','ipc_anual','ir_real_anual']].describe().round(3))
''')
md('''## Gráfico animado\n\nPulsa **Play** para recorrer la muestra y **Pausa** para detenerla. Puedes arrastrar el selector temporal; **Reiniciar** vuelve al primer mes. Pasa el cursor por una burbuja para ver las cifras y el trimestre de empleo.\n\nLos ejes y la escala de áreas permanecen fijos durante toda la animación. Al volver a una fecha anterior, el rastro también retrocede.\n''')
code('''figura = build_figure(datos)
export_results(datos, cobertura, excluidos, figura)
static_chart(datos)
# HTML embebido: evita depender de extensiones de Plotly o de una conexión a internet.
display(HTML(figura.to_html(full_html=False, include_plotlyjs=True, auto_play=False,
                           config={'responsive': True, 'displaylogo': False})))
''')
md('''## Lectura económica y sensibilidad de fechas\n\nUna nube de puntos es una descripción, no una estimación causal de la curva de Phillips. La inflación depende también de expectativas, oferta, precios externos, tipo de cambio y política monetaria. La variación del IR real comparte el IPC como deflactor, por lo que no constituye una tercera variable independiente de la inflación.\n\nLa correlación siguiente usa niveles contemporáneos, sin controles ni correcciones por autocorrelación. Los trimestres móviles se superponen y las tasas anuales también comparten meses. Por eso no se presentan pruebas de significancia, NAIRU ni recomendaciones de tasas de interés.\n\nPara explorar la convención temporal, también se calcula la correlación con ENE asignada al mes final, restringiendo ambas alternativas a las mismas fechas. Este contraste cambia el emparejamiento, no el dato original.\n''')
code('''alternativa, _, _ = load_data(alignment='final')
fechas_comunes = datos.fecha[datos.fecha.isin(alternativa.fecha)]
a = datos[datos.fecha.isin(fechas_comunes)]
b = alternativa[alternativa.fecha.isin(fechas_comunes)]
resumen = pd.DataFrame([
    {'alineación': 'Mes central', 'n': len(a), 'correlación IPC-desocupación': a.desocupacion.corr(a.ipc_anual)},
    {'alineación': 'Mes final', 'n': len(b), 'correlación IPC-desocupación': b.desocupacion.corr(b.ipc_anual)}
])
display(resumen.round(3))
display(datos.groupby(datos.fecha.dt.year)[['desocupacion','ipc_anual','ir_real_anual']].mean().round(3))
print('Advertencia: el último año puede ser parcial; no comparar promedios como años completos.')
''')
md('''## Archivos de salida y actualización\n\n- `resultados/phillips_animado.html`: gráfico interactivo independiente.\n- `resultados/phillips_estatico.png`: imagen para el artículo.\n- `resultados/datos_phillips.csv`: datos de cada burbuja.\n- `resultados/cobertura.csv` y `meses_excluidos.csv`: auditoría de cobertura.\n\nPara volver a trabajar, abre el mismo `.bat`. Para actualizar las fuentes, revisa primero los extractores y ejecuta `python main.py` desde el entorno del proyecto. Esto sustituye los CSV locales con la descarga vigente. Guarda una copia antes si quieres conservar el corte original y luego ejecuta todas las celdas. El informe Word es una fotografía del corte analizado y debe revisarse si cambian los datos.\n\n## Fuentes y referencias\n\n- [INE — Ocupación y desocupación](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion).\n- [INE — IPC](https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor).\n- [INE — Remuneraciones y costos laborales](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales).\n- [Banco Central de Chile — IPoM junio de 2016, evidencia de la curva de Phillips](https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6).\n\nLas URL exactas de los tabulados están en los extractores originales del proyecto.\n''')
nb=dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3 (ipykernel)',language='python',name='python3'),language_info=dict(name='python',version='3.13')),nbformat=4,nbformat_minor=5)
for i,c in enumerate(cells): c['id']=f'phillips-{i:02}'
(root/'Curva_de_Phillips.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf8')
print('Cuaderno creado')

