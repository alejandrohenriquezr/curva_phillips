# Referencias macroeconómicas del gráfico

## Meta de inflación

3%, de acuerdo con el IPoM de junio de 2026, sección «La meta de inflación y la Tasa de Política Monetaria» (página 3 del PDF). La meta se refiere al horizonte de política de dos años, no a la exigencia de que cada registro mensual de inflación anual sea exactamente 3%.

Fuente: https://www.bcentral.cl/documents/33528/8413153/IPoM%2Bjunio%2B2026.pdf/93388589-0929-4ad6-b166-10981ca34946

## Referencia NAIRU

La minuta «Holguras en el mercado laboral», citada en el Recuadro II.1 del IPoM de diciembre de 2024, informa un rango de estimaciones de 8,0% a 8,5% para el tercer trimestre de 2024. Consultar las secciones 1 y 4 (páginas 34 y 38 del PDF). Los métodos incluyen filtros de Kalman multivariados y modelos VAR.

Fuente: https://www.bcentral.cl/documents/33528/6735463/Minutas%2Bcitadas%2Ben%2Bel%2BIPoM%2Bdiciembre%2B2024.pdf/d24985ae-cb5e-2f03-4499-ecfad3d86ade

El gráfico muestra una franja 8,0–8,5% y una línea vertical en **8,25% = (8,0% + 8,5%) / 2**. La línea es una convención visual calculada por este proyecto a partir del rango publicado; no es una estimación puntual oficial, ni una cifra publicada en el IPoM de junio de 2026. El rango no es un intervalo de confianza y no se confunde con el promedio muestral de desempleo.

Se mantiene la referencia histórica fija en toda la animación. La NAIRU es una variable no observable que puede cambiar con el tiempo y difiere conceptualmente de una tasa de desempleo natural invariable. La minuta distingue la NAIRU de la tasa de desempleo de largo plazo.

Las estimaciones de referencia utilizan datos desestacionalizados; los puntos emplean la ENE sin ajuste estacional. Por ello, las distancias exportadas son comparaciones ilustrativas y no estimaciones oficiales de holgura. La clasificación de cuadrantes no prueba causalidad ni autoriza una recomendación automática de política monetaria.

Verificación: 23 de septiembre de 2026. Se consultaron también el IPoM de junio de 2026 y sus minutas; no se identificó una NAIRU puntual publicada en esa edición. Se utiliza diciembre de 2024 como referencia verificable elegida para este ejercicio, sin afirmar que sea la estimación más reciente disponible del Banco Central.

## IMACEC

Se incorporan las series originales y desestacionalizadas empalmadas del BCCh, base promedio 2018=100. Identificadores, URLs BDE, fecha de actualización, descarga y hashes de las respuestas en [imacec_metadata.json](imacec_metadata.json). El CSV conserva los índices publicados con un decimal. Fórmulas y ventanas en [METODOLOGIA.md](../METODOLOGIA.md). El color es la variación anual del promedio móvil de tres meses de la serie original; el panel muestra la variación en 12 meses del índice desestacionalizado y la inflación anual del IPC. Los puntos de diciembre muestran el crecimiento del promedio anual original del IMACEC y la inflación diciembre/diciembre; tamaño y color usan la variación en 12 meses normalizada en toda la muestra.

## IPC histórico empalmado

Archivo INE: serie histórica empalmada diciembre de 2009 a la fecha, hoja `Serie_empalmada`, base 2023. Columnas: Año, Mes, Índice, Variación Mensual (%) y Variación 12 Meses (%). El extractor añade `Glosa = IPC General`. Se preservan las tasas anuales oficiales y los faltantes originales. El corte actual permite 186 meses comunes, enero de 2011 a junio de 2026. URL completa en `extractors/ipc_extractor.py`; versión del CSV identificada por SHA-256 en resultados.
