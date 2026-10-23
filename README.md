# Curva de Phillips de Chile

Este repositorio estudia cómo evolucionan la inflación, la desocupación, las remuneraciones reales y la actividad económica en Chile. Combina fuentes oficiales del Instituto Nacional de Estadísticas (INE) y del Banco Central de Chile (BCCh), y genera un análisis reproducible, un gráfico interactivo y un artículo firmado por **Alejandro Henríquez R.**

El objetivo es describir las trayectorias de los indicadores y comparar su relación antes, durante y después de la ventana de pandemia. Se distinguen los cambios en niveles de los índices, las tasas interanuales y las diferencias en puntos porcentuales. El ejercicio no estima causalidad, una NAIRU propia ni recomendaciones de política monetaria.

## Qué responde el análisis

- ¿Cómo cambiaron el empleo, la inflación, los salarios reales y la actividad a lo largo de la muestra?
- ¿Qué diferencias hay entre la etapa previa a marzo de 2020, la ventana marzo de 2020–agosto de 2023 y el período desde septiembre de 2023?
- ¿Qué señales de recuperación o desaceleración muestran los niveles y las tasas del último mes común?
- ¿Cómo varía la correlación inflación–desocupación entre etapas y qué límites tiene su interpretación?

Las ventanas son cortes descriptivos coherentes con las marcas del gráfico. No identifican por sí solas los efectos de la pandemia. El informe incluye las fechas efectivamente disponibles, las medias por etapa, la evolución de cada indicador y conclusiones calculadas a partir de esa edición.

## Requisitos

Instala **Git** y **Python 3.13 de 64 bits**. En Windows también se admiten Python 3.11 y 3.12. La primera instalación y la actualización de fuentes requieren internet. El IPC original no necesita X-13.

## Clonar el repositorio

Abre una terminal en la carpeta donde quieras guardar el proyecto y ejecuta:

```powershell
git clone https://github.com/alejandrohenriquezr/curva_phillips.git
cd curva_phillips
```

El proyecto se mantiene en una sola rama, `main`. Si ya lo tienes clonado, entra en su carpeta y actualízalo antes de ejecutar:

```powershell
git switch main
git pull --ff-only
```

Conserva o confirma tus cambios locales antes de actualizar si Git indica que hay archivos modificados.

## Instalar y ejecutar en Windows

Desde la carpeta del repositorio, en PowerShell:

```powershell
.\lanzadores/00_instalar.bat
.\lanzadores/01_ejecutar_todo.bat
```

El instalador selecciona un Python compatible, crea `venv`, instala paquetes binarios y comprueba sus dependencias. Si encuentra un entorno incompatible, lo conserva como respaldo y crea otro. No necesitas compilar pandas ni instalar Visual Studio.

El segundo comando descarga las cuatro fuentes oficiales, las valida, ejecuta las pruebas y genera el cuaderno, los gráficos, el análisis por etapas, el artículo y el sitio. Si una descarga o validación falla, el proceso se detiene y no presenta el corte anterior como una actualización nueva.

También puedes ejecutar el mismo proceso directamente:

```powershell
.\venv\Scripts\python.exe scripts/06_ejecutar_todo.py
```

## Instalar y ejecutar en Linux o macOS

Desde la carpeta del repositorio:

```bash
python3.13 -m venv venv
./venv/bin/python -m pip install --only-binary=:all: -r dependencias/requirements-completo.txt
./venv/bin/python scripts/06_ejecutar_todo.py
```

## Abrir los resultados

Cada ejecución utiliza un prefijo de fecha y hora `AAAAMMDD_HH_MM`, compartido por todos sus resultados. Esa fecha identifica la edición; el corte estadístico es el último mes con datos completos en todas las fuentes necesarias.

| Carpeta o archivo | Contenido |
| --- | --- |
| `informe/` | Artículo Word para LinkedIn y su texto Markdown, con autoría, evolución por etapas y conclusiones |
| `resultados/` | Gráfico HTML independiente, PNG, datos combinados, cobertura, meses excluidos y registro de ejecución |
| `resultados/*_evolucion_etapas.csv` | Medias, extremos, variaciones de niveles y tasas para cada etapa |
| `resultados/*_resumen_economico.json` | Cifras utilizadas por el cuaderno y el artículo, incluidas las etapas pre y pospandemia |
| `cuadernos/*_Curva_de_Phillips.ipynb` | Cuaderno de esa edición con todas sus celdas ejecutadas |
| `site_pages/index.html` | Página con el gráfico integrado sin scroll interno y acceso al artículo |
| `site_pages/articulo.html` | Versión del artículo para lectura en el navegador |

Para abrir el sitio local con el gráfico interactivo, desde la carpeta del proyecto:

```powershell
.\venv\Scripts\python.exe -m http.server 8000 --directory site_pages
```

Después abre `http://localhost:8000` en tu navegador. Para terminar el servidor, pulsa `Ctrl+C`. En Linux o macOS usa `./venv/bin/python` en el mismo comando.

Los archivos generados no se versionan. El repositorio conserva el código, las pruebas, el cuaderno base y un corte de referencia de las fuentes. El Word queda en `informe/`; no se publica ni se enlaza en GitHub Pages.

## Usar el cuaderno y VS Code

En Windows, `lanzadores/02_abrir_jupyter.bat` abre Jupyter. Entra en `cuadernos/` y selecciona el cuaderno base o el de una edición y ejecuta todas las celdas. El cuaderno actualiza las fuentes por defecto. El orquestador descarga una sola vez y reutiliza ese mismo corte para sus etapas.

En VS Code, instala las extensiones Python y Jupyter, abre la carpeta del repositorio y selecciona el intérprete relativo `venv/Scripts/python.exe` en Windows o `venv/bin/python` en Linux/macOS. La tarea **Phillips: ejecutar todo** permite lanzar el proceso con `Ctrl+Shift+B`.

## Reproducir un corte sin actualizar

Para usar expresamente los CSV que ya están en la carpeta, sin descargarlos:

```powershell
.\lanzadores/01_ejecutar_todo.bat --sin-actualizar-datos
```

En el cuaderno, cambia `ACTUALIZAR_DATOS = False`. No es una actualización de fuentes: el registro identifica este modo como corte local. Para reproducir una edición anterior, conserva también sus CSV y metadatos, no solamente el HTML o el Word.

## Leer el gráfico y las comparaciones

El eje horizontal es la desocupación ENE y el vertical la inflación a doce meses. El área representa la magnitud de la variación anual del IR real; su signo se consulta en el tooltip. El color representa la variación interanual del promedio móvil centrado de tres niveles originales del IMACEC. El panel inferior compara tasas anuales de IMACEC desestacionalizado e IPC y marca los cierres de diciembre.

ENE se asigna al mes central del trimestre móvil. El promedio centrado de actividad necesita el mes siguiente: es una comparación retrospectiva, no una reconstrucción de la información conocida en tiempo real. No se rellenan faltantes ni se suman tasas interanuales para obtener crecimientos acumulados.

La línea del 3% es la meta de inflación a horizonte de dos años. La banda 8,0–8,5% y su punto medio 8,25% son una referencia histórica de NAIRU para 2024-T3, no una estimación actual del proyecto. Consulta [la metodología](documentos/METODOLOGIA.md) y [las referencias](fuentes/REFERENCIAS.md).

## IPC ajustado experimentalmente con X-13

Para instalar el ejecutable oficial de Census y generar la variante ajustada:

```powershell
.\lanzadores/01_ejecutar_todo.bat --ipc sa --instalar-x13
```

Después basta `--ipc sa`. El modo predeterminado es `--ipc original`. El ajuste X-13/SEATS es experimental, revisable y no oficial del INE. Conserva la especificación, las advertencias, las tablas y los hashes en los resultados de la edición. No ajusta ENE ni IR. Evalúa el calendario chileno mediante selección AICC. Las dos variantes utilizan nombres distintos y pueden coexistir.

## Publicar el sitio en GitHub Pages

El sitio público está en [GitHub Pages](https://alejandrohenriquezr.github.io/curva_phillips/). El repositorio tiene un único workflow: **Publicar análisis en GitHub Pages**.

1. Confirma y sube los cambios de código a `main`.
2. En GitHub, abre **Actions → Publicar análisis en GitHub Pages**.
3. Pulsa **Run workflow**, selecciona `main` y confirma la ejecución.
4. Espera a que terminen la generación y el despliegue; después comprueba el sitio.

El workflow descarga las fuentes oficiales y publica una edición nueva. No se ejecuta por cada push, por un PR ni por un horario periódico. Las ejecuciones históricas de Actions son registros, no procesos que sigan activos.

## Autoría y trazabilidad

La firma se configura en `autor.json`. Aparece en la cabecera del sitio y del gráfico independiente y en el texto y las propiedades del Word; el pie del sitio no la repite. Los datos se atribuyen al INE y al BCCh.

Las URL exactas de las fuentes están en `codigo/extractors/` y `actualizar_imacec.py`. La descarga conjunta, las coberturas y los hashes se registran en `fuentes/actualizacion.json` y se copian a los resultados de cada edición. Revisa el contenido y la presentación del artículo antes de publicarlo en LinkedIn; el proyecto no publica en esa red social.

Al publicar manualmente, la opción **Generar imágenes para revisar el Word** produce un artefacto temporal de revisión visual. No añade el Word al sitio ni activa ejecuciones automáticas.

## Organización

- `scripts/`: entradas numeradas; 00 instala X-13 opcional, 01 actualiza datos, 02 crea el cuaderno, 03 lo ejecuta, 04 genera el artículo y 05 prepara el sitio. 06 coordina todas las etapas; 07 renderiza el Word para revisión opcional.
- `lanzadores/`: 00 instala el entorno, 01 ejecuta el proceso completo y 02 abre Jupyter.
- `codigo/`: módulos reutilizables y extractores; conservan nombres importables por Python.
- `datos/`: CSV oficiales; `fuentes/`: fechas, referencias y hashes.
- `configuracion/`: autoría y referencias macroeconómicas.
- `dependencias/`: requisitos de instalación.
- `documentos/`: metodología; `cuadernos/`: notebooks generados.
- `tests/`: pruebas automatizadas.
- `informe/`, `resultados/` y `site_pages/`: salidas regenerables.

Los comandos se ejecutan desde la raíz. El comando habitual es `python scripts/06_ejecutar_todo.py`; no es necesario ejecutar cada etapa por separado.

El modo X-13 evalúa composición semanal y feriados nacionales de Chile mediante AICC; no impone su retención. Consulta la sección de calendario en [la metodología](documentos/METODOLOGIA.md). Las fechas, conteos, selección y diagnósticos quedan en la carpeta X-13 de cada edición.
