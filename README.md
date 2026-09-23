# Curva de Phillips de Chile

Cuaderno Jupyter y gráfico animado de desocupación, inflación anual e índice de remuneraciones real, con datos del INE incluidos en el repositorio.

## Abrir en Windows

1. En este equipo el entorno `%LOCALAPPDATA%\curva_phillips\venv` se configura durante la preparación del proyecto. Para una instalación nueva, instala Python 3.11 o superior y ejecuta `INSTALAR.bat` una vez.
2. Haz doble clic en **ABRIR_JUPYTER.bat**.
3. En el cuaderno, selecciona **Run → Run All Cells**. También puedes ejecutar una celda con **Shift + Enter**.
4. Pulsa **Play** en el gráfico; usa Pausa, Reiniciar o el selector de mes.
5. Mantén abierta la ventana que inició Jupyter. Para detener el servidor, presiona Ctrl+C en esa ventana y confirma cuando lo solicite.

En PowerShell, desde la carpeta del proyecto:

```powershell
& "$env:LOCALAPPDATA\curva_phillips\venv\Scripts\python.exe" -m notebook Curva_de_Phillips.ipynb
```

El acceso utiliza el Python del proyecto directamente. Evita el error `jupyter no se reconoce` sin depender del PATH global. Durante el diagnóstico, `python` resolvía a un alias de WindowsApps y `py` a `C:\Python313\python.exe`, que no tenía pip. Instalar un paquete con un pip de otro entorno no lo hace disponible para todos los Python.

## Ver el gráfico sin instalar nada

Descarga y abre `resultados/phillips_animado.html` en un navegador. Incluye Plotly y los datos, y funciona sin internet. GitHub muestra el archivo como código: usa **Download raw file** y luego abre la copia descargada. GitHub no reproduce JavaScript dentro de la vista del cuaderno.

## Archivos

- `Curva_de_Phillips.ipynb`: cuaderno explicado, con resultados de ejecución.
- `phillips.py`: limpieza, validación, gráfico y exportaciones.
- `resultados/phillips_animado.html`: gráfico con Play, pausa, reinicio, selector temporal y rastro.
- `resultados/phillips_estatico.png`: imagen del recorrido completo.
- `resultados/datos_phillips.csv`: observaciones utilizadas.
- `resultados/cobertura.csv`, `meses_excluidos.csv`, `fuentes_sha256.json`: trazabilidad.
- `informe/Articulo_LinkedIn_Curva_Phillips.docx`: artículo con análisis económico, gráfico y fuentes.
- `informe/articulo_linkedin.md`: texto editable del artículo.
- `requirements-notebook.txt`: dependencias del análisis (Python 3.11+).
- `requirements-notebook-lock.txt`: versiones exactas verificadas en Windows/Python 3.13.
- `requirements.txt`, `main.py`, `extractors/`: pipeline original de descarga, conservado.

## Metodología

Corte de los CSV recibidos: enero de 2024 a junio de 2026, 30 meses comunes. ENE se asigna al **mes central** del trimestre móvil, respetando `mes_año` del archivo original. Por tanto, junio de 2026 usa empleo de mayo–julio de 2026. Esta es una comparación retrospectiva, no una base de información en tiempo real. El cuaderno incluye sensibilidad al mes final, sobre las mismas fechas comunes.

Se selecciona exclusivamente `Glosa == "IPC General"` y su variación anual publicada. El IR es el índice **real** empalmado; se utiliza `var_12` sin volver a deflactarlo. Las series se unen por fecha con correspondencia uno a uno; faltantes se excluyen y documentan, nunca se rellenan con cero.

El **área**, no el radio, es proporcional a `abs(IR anual)`. Verde indica variaciones positivas y naranja negativas. Un centro oscuro fijo localiza valores cero. Todos los fotogramas usan los mismos ejes y la misma escala de tamaños. Los puntos del rastro retienen el tamaño correspondiente a su propia fecha.

La correlación es descriptiva: muestra corta, tasas sin ajuste estacional, trimestres superpuestos y ausencia de controles. No estima causalidad, NAIRU ni el efecto de una decisión monetaria. El IR real por hora tampoco equivale al ingreso total de todos los hogares.

## Ejecutar y comprobar

```powershell
& "$env:LOCALAPPDATA\curva_phillips\venv\Scripts\python.exe" phillips.py
& "$env:LOCALAPPDATA\curva_phillips\venv\Scripts\python.exe" -m unittest test_phillips -v
& "$env:LOCALAPPDATA\curva_phillips\venv\Scripts\python.exe" verificar_cuaderno.py
```

`verificar_cuaderno.py` ejecuta todas las celdas y guarda el cuaderno con resultados. Puede tardar en el primer inicio, especialmente en una unidad sincronizada con Google Drive.

## Actualización voluntaria

Guarda una copia de los CSV antes de actualizarlos. Desde el entorno ejecuta `python main.py` y revisa que los tres extractores hayan finalizado correctamente: el pipeline original captura errores por separado. Después ejecuta el cuaderno. La actualización puede cambiar el período común y las cifras por revisiones del INE. Revisa el artículo antes de reutilizarlo con otro corte.

No se publica automáticamente en LinkedIn. El Word está preparado para revisión y publicación por su autor.

## Fuentes

- [INE: ENE](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion).
- [INE: IPC](https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor).
- [INE: remuneraciones](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales).
- [Banco Central: evidencia de Phillips, IPoM junio de 2016](https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6).

Las URL exactas de los tabulados están en los extractores. Los archivos de datos se atribuyen al INE; no se les asigna una licencia nueva en este proyecto.


Para regenerar el Word, instala `requirements-document.txt` en un entorno Python y ejecuta `python crear_articulo.py` después de generar el gráfico. Revisa visualmente el documento antes de publicar.

