# Instalación y uso

Requiere Python 3.10 o superior; CI utiliza 3.13. En Windows, `INSTALAR.bat` crea `.venv`,
instala dependencias, paquete editable, JupyterLab y kernel dentro del entorno, y ejecuta pruebas.
`EJECUTAR_TODO.bat` ejecuta `scripts/08_ejecutar_todo.py` y abre `site/index.html` sólo si termina bien.
`ABRIR_JUPYTER.bat` abre la carpeta de cuadernos usando el entorno virtual y `PYTHONPATH` del proyecto.

El cuaderno busca la raíz desde su carpeta y usa el mismo Excel que los informes. El verificador
fuerza el kernel al intérprete del pipeline. No requiere una ruta fija en el disco.

Para actualizar el Excel, sustituya `datos/datos_anualizados2.xlsx` y ejecute todo. El CSV y
el manifiesto se regeneran. Un cambio de cobertura exige revisar explícitamente las validaciones,
los cortes y el artículo; no se amplía silenciosamente. No hay opciones para otras frecuencias.

Linux/macOS: cree y active `.venv`, instale `requirements.txt` y `pip install -e .`, y ejecute
`python scripts/08_ejecutar_todo.py`. Las dependencias sólo se descargan durante la instalación.
