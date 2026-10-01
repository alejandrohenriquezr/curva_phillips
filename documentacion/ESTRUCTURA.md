# Estructura de la variante anual

`datos/`: Excel fuente, CSV reproducible y metadatos de procedencia.

`src/curva_phillips/analisis_anual.py`: validación, importación, modelos y exportaciones.
`articulo.py`: narrativa compartida; `productos.py`: figuras, Word, HTML y cuaderno.
`rutas.py`: rutas relativas al repositorio, sin depender de C:\curva_phillips.

Scripts: 00 importa Excel; 03 crea cuaderno; 04 lo ejecuta; 05 genera artículo;
06 ejecuta análisis anual; 07 construye sitio; 08 ejecuta todo; 09 verifica productos.
La numeración conserva los puntos de entrada principales de la rama base.

`tests/`: integridad de datos, cronología, estimaciones y alcance.
`cuadernos_jupyter/`, `informes/`, `resultados/`, `site/`: productos regenerables.
