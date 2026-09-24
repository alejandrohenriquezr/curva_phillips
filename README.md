# Curva de Phillips de Chile

Salidas con fecha y hora **AAAAMMDD_HH_MM**, con 186 meses comunes de enero de 2011 a junio de 2026. Datos locales del INE y del Banco Central de Chile. El análisis es descriptivo: no estima causalidad, NAIRU propia ni una recomendación monetaria.

## Ejecutar todo en VS Code

1. Abre la carpeta `C:\Proyectos\Curva_de_Phillips` en VS Code.
2. Instala las extensiones **Python** y **Jupyter** de Microsoft si faltan.
3. Ejecuta `INSTALAR.bat` una vez para instalar todas las dependencias, incluido Word.
4. En `Ctrl+Shift+P` → **Python: Select Interpreter**, selecciona `C:\Proyectos\Curva_de_Phillips\venv\Scripts\python.exe` (opción para introducir la ruta si no aparece).
5. Pulsa **Ctrl+Shift+B** y elige **Phillips: ejecutar todo**. También puedes usar F5 con **Phillips: proceso completo**.

Alternativa en la terminal PowerShell de VS Code, sin activar el entorno:

```powershell
cd C:\Proyectos\Curva_de_Phillips
.\venv\Scripts\python.exe orquestar.py
```

O ejecuta `EJECUTAR_TODO.bat`. El orquestador usa el mismo Python para pruebas, análisis, kernel y Word. Si falla una etapa, detiene la ejecución y registra el error. El parámetro opcional `--python-documento` permite usar otro Python con python-docx para Word; normalmente no es necesario.

El proceso comprende pruebas, creación del notebook, ejecución de todas las celdas (que genera tablas, PNG y HTML), y creación del Word y Markdown. El registro queda en `resultados/AAAAMMDD_HH_MM_ejecucion.json`. No publica automáticamente en GitHub ni LinkedIn.

## Archivos de esta edición

- `AAAAMMDD_HH_MM_Curva_de_Phillips.ipynb`: cuaderno explicado y ejecutado.
- `resultados/AAAAMMDD_HH_MM_phillips_animado.html`: gráfico autónomo con Play, pausa, reinicio y selector mensual; funciona sin conexión.
- `resultados/AAAAMMDD_HH_MM_phillips_estatico.png`: gráfico para el informe.
- `informe/AAAAMMDD_HH_MM_Articulo_LinkedIn_Curva_Phillips.docx`: informe actualizado.
- `informe/AAAAMMDD_HH_MM_articulo_linkedin.md`: texto del informe.
- `resultados/AAAAMMDD_HH_MM_datos_phillips.csv`, `AAAAMMDD_HH_MM_cierres_anuales.csv`, `AAAAMMDD_HH_MM_resumen_economico.json` y `AAAAMMDD_HH_MM_correlaciones_subperiodos.csv`: datos y cifras reproducibles.
- Cobertura, meses excluidos y hashes también llevan el prefijo de fecha.

Las versiones anteriores permanecen en la carpeta. Para trabajar con esta edición, abre el archivo que comienza con `AAAAMMDD_HH_MM_`. `ABRIR_JUPYTER.bat` abre Jupyter para elegir el cuaderno. Selecciona el kernel del entorno del proyecto en VS Code. GitHub no ejecuta el JavaScript de un notebook: descarga el HTML para usar la animación.

## Lectura del gráfico

Phillips: eje X = desocupación ENE; eje Y = IPC anual; área proporcional a la magnitud del IR real anual; color divergente centrado en cero = crecimiento interanual del promedio móvil 3m del IMACEC original. Etiquetas MM-AAAA en enero, marzo de 2020 y agosto de 2023. El borde tiene un color distinto por año, excepto durante pandemia. Círculos con borde segmentado: ventana de pandemia Covid-19 en Chile definida para el gráfico, marzo de 2020–agosto de 2023.

Panel inferior: IMACEC desestacionalizado e IPC en variación de 12 meses. En diciembre, rombos para el crecimiento del promedio anual del IMACEC original y cuadrados para inflación diciembre/diciembre. La posición vertical muestra el acumulado. Tamaño y color codifican la tasa a 12 meses normalizada con un máximo absoluto común a ambas series y fijo en toda la muestra. El tooltip explica ambas cifras; no se suman tasas. No hay punto de cierre para 2026, que es parcial.

La NAIRU de referencia, 8,25%, es el punto medio propio del rango BCCh 8,0–8,5% para 2024-T3, publicado en diciembre de 2024; no es una estimación oficial para cada año del gráfico. La horizontal es la meta de inflación del 3% a horizonte de dos años. Véanse [fórmulas y metodología](METODOLOGIA.md) y [fuentes](fuentes/REFERENCIAS.md).

## Datos y actualización voluntaria

La ejecución normal usa los cuatro CSV locales y no necesita internet. El IPC histórico empalmado tiene niveles desde diciembre de 2009, pero sus tasas anuales publicadas y el IR anual disponibles comienzan en enero de 2011. El extractor incorpora `Glosa = IPC General`. ENE se asigna al mes central: junio corresponde a mayo–julio. Es una comparación retrospectiva.

Para descargar fuentes nuevas antes de ejecutar:

```powershell
.\venv\Scripts\python.exe orquestar.py --actualizar-datos
```

Guarda una copia de los CSV si quieres conservar el corte: esta opción los sustituye. Si cambia la cobertura, el informe exige revisar el análisis histórico antes de regenerarse. Cambiar solo `--fecha` cambia los nombres, no actualiza datos ni reescribe conclusiones. El Word debe revisarse visualmente antes de publicar.

Los scripts principales son `orquestar.py`, `phillips.py` (cálculos y exportación), `graficos.py` (presentación y bordes SVG), `salidas.py` (prefijo), `crear_cuaderno.py`, `verificar_cuaderno.py` y `crear_articulo.py`. Los bordes segmentados se incorporan tanto al HTML independiente como al HTML del notebook mediante un script local de Plotly. No requieren extensiones adicionales.

## Si aparece ModuleNotFoundError de nbformat

El Python que ejecuta el proceso necesita todas las dependencias. En la terminal de VS Code:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-completo.txt
.\venv\Scripts\python.exe orquestar.py
```

Usa `python orquestar.py` si activaste ese entorno; el comando `py` puede seleccionar otro intérprete según su configuración. El orquestador muestra el ejecutable y detecta dependencias faltantes antes de las pruebas. No instala paquetes automáticamente. `INSTALAR.bat` y los lanzadores utilizan ahora el mismo `venv` de la carpeta.

Cada ejecución fija una fecha y hora local al inicio, por ejemplo `20260924_07_32`, compartida por todos sus archivos. Puedes indicarla con `--fecha 20260924_07_32`. Dos ejecuciones dentro del mismo minuto utilizan el mismo prefijo y reemplazan esa edición. La fecha es de generación, no el corte de las series.
