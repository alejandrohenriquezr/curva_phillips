# Estructura del proyecto

El repositorio contiene código, fuentes reproducibles, pruebas y documentación. Los productos derivados no se versionan: se generan durante la ejecución y se conservan como artefactos de GitHub Actions o se publican con GitHub Pages.

| Carpeta | Contenido |
| --- | --- |
| `datos/` | CSV del INE/BCCh, tabla anual y metadatos de descarga. |
| `scripts/` | Entradas ejecutables ordenadas secuencialmente. |
| `src/curva_phillips/` | Lógica reutilizable, gráficos, X-13 y extractores. |
| `tests/` | Pruebas unitarias y de integración. |
| `documentacion/` | Metodología, referencias y manuales. |
| `cuadernos_jupyter/` | Notebook generado y ejecutado. |
| `informes/` | Informes anual, mensual, combinado, Word y Markdown. |
| `resultados/` | Datos procesados, gráficos, diagnósticos y tablas de modelos. |
| `site/` | Sitio estático temporal preparado para GitHub Pages. |

## Secuencia

1. `00_actualizar_datos_ine.py`
2. `01_actualizar_imacec.py`
3. `02_instalar_x13.py`
4. `03_generar_cuaderno.py`
5. `04_verificar_cuaderno.py`
6. `05_generar_articulo.py`
7. `06_analisis_anual_mensual.py`
8. `07_construir_sitio.py`
9. `08_ejecutar_todo.py`

La numeración expresa orden de uso; la lógica reutilizable no tiene prefijos numéricos porque se importa como paquete Python.
