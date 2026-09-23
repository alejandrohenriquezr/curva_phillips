# Inflación y empleo en Chile vistos a través de la curva de Phillips

Enero de 2024 a junio de 2026 | Análisis para LinkedIn

Entre enero de 2024 y junio de 2026, la relación contemporánea entre inflación y desocupación en esta muestra chilena fue prácticamente nula. La correlación de las 30 observaciones es −0,011. El resultado invita a mirar la trayectoria de ambas variables y las remuneraciones reales, sin convertir una asociación estadística de corto plazo en una conclusión causal.

El gráfico animado permite hacerlo: la desocupación ocupa el eje horizontal, la inflación anual del IPC el vertical y el área de cada burbuja representa la magnitud de la variación anual del índice de remuneraciones real. El rastro conserva el recorrido. En la muestra, todas las variaciones del IR real son positivas y, por eso, las burbujas aparecen en verde.

![Gráfico de Phillips](../resultados/phillips_estatico.png)

Área proporcional a la magnitud de la variación anual del IR real. ENE asignada al mes central. Línea horizontal: meta de inflación del 3%. Línea vertical: punto medio propio de 8,25% del rango NAIRU histórico 8,0–8,5% del BCCh para 2024-T3 [5].

## Una trayectoria que cambia de dirección

El punto inicial combina una inflación anual de 3,8%, una desocupación de 8,50% y un aumento anual del IR real de 2,78%. En junio de 2026, el punto final registra 4,3%, 9,53% y 3,27%, respectivamente. Entre los extremos, la desocupación aumenta 1,03 puntos porcentuales y la inflación 0,5 puntos. Sin embargo, esa comparación omite los cambios de dirección que aparecen durante el recorrido.

El último punto se sitúa arriba y a la derecha del cruce de referencias: la inflación de 4,3% supera la meta en 1,30 puntos porcentuales y la desocupación de 9,53% está 1,28 puntos sobre el punto medio histórico de 8,25%. Estas distancias describen posiciones en el gráfico; no identifican por sí solas un shock de oferta ni una brecha cíclica oficial.

## Qué puede decir una curva de Phillips

La intuición económica de la curva de Phillips relaciona las presiones inflacionarias con la holgura de la economía. Un mercado laboral más estrecho puede aumentar las presiones salariales y de costos. Pero la inflación observada también responde a expectativas, precios importados, tipo de cambio, productividad y perturbaciones de oferta. El análisis del Banco Central sobre la evidencia chilena subraya la necesidad de una especificación más amplia que una nube de inflación y desempleo [4].

La correlación cercana a cero no demuestra que la relación económica haya desaparecido. Puede reflejar fuerzas simultáneas, rezagos o una muestra breve. Tampoco permite estimar una NAIRU propia ni atribuir el movimiento a una decisión monetaria.

## El salario real agrega una dimensión relevante

El IR real crece en términos anuales en los 30 meses comunes, con variaciones entre 1,40% y 3,74%. En junio de 2026, el aumento de 3,27% convive con una desocupación elevada respecto del comienzo de la muestra. Esta coexistencia recuerda que el poder adquisitivo de la remuneración por hora y la posibilidad de acceder a un empleo son dimensiones distintas del bienestar laboral.

El indicador del INE mide remuneraciones reales por hora en su ámbito de cobertura. No equivale al ingreso laboral total de los hogares: no incorpora del mismo modo el desempleo, los cambios de horas trabajadas o todas las formas de ocupación. Además, el IR real utiliza el IPC como deflactor. No es una tercera variable estadísticamente independiente de la inflación y no debe volver a descontársele el IPC [3].

## Leer el gráfico con sus límites

La ENE entrega trimestres móviles que comparten dos meses entre observaciones consecutivas. Aquí se utiliza el mes central, respetando la convención de los archivos: junio de 2026 corresponde a mayo–julio de 2026. El ejercicio es retrospectivo; ese punto no representa lo que se conocía en tiempo real durante junio. El cuaderno permite contrastar la asignación al mes final.

La muestra se limita a la intersección disponible de las tres series: 30 meses desde enero de 2024 hasta junio de 2026. Los archivos contienen IPC hasta agosto de 2026 e IR real hasta julio, pero no se completan los datos faltantes de empleo ni se prolonga artificialmente la animación. Tampoco se utilizan promedios de divisiones del IPC: se selecciona exclusivamente el IPC General y su variación anual publicada.

Las tasas no están desestacionalizadas y los cambios a doce meses comparten información entre períodos. Estas dependencias, junto con el reducido tamaño de la muestra, impiden tratar los puntos como observaciones independientes para una inferencia simple. Una investigación econométrica requeriría un horizonte más largo, expectativas de inflación, controles de oferta, rezagos y una estrategia explícita de identificación.

## Qué significan las líneas de referencia

La minuta del BCCh citada en el IPoM de diciembre de 2024 presenta un rango NAIRU de 8,0–8,5% para el tercer trimestre de 2024, mediante filtros de Kalman multivariados y modelos VAR [5]. Usamos su punto medio, 8,25%, como convención visual propia, no como estimación puntual oficial ni como cifra de junio de 2026. La banda representa dispersión entre estimaciones, no un intervalo de confianza.

La referencia es histórica y utiliza desempleo desestacionalizado, mientras nuestros puntos usan ENE sin ajuste estacional. No suponemos que la NAIRU haya permanecido constante ni la equiparamos automáticamente a la tasa natural de largo plazo. Por su parte, la meta del 3% corresponde a un horizonte de dos años [6]; no exige que la inflación de cada mes sea exactamente 3%. Estas referencias orientan la lectura, pero no bastan para recomendar una tasa de interés.

## Fuentes y reproducibilidad

[1] INE. Encuesta Nacional de Empleo, series vigentes. https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion

[2] INE. Índice de Precios al Consumidor. https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor

[3] INE. Índices de Remuneraciones y Costos Laborales; serie empalmada del IR real. https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/remuneraciones-y-costos-laborales

[4] Banco Central de Chile. IPoM, junio de 2016, recuadro sobre evidencia de la curva de Phillips para Chile. https://www.bcentral.cl/documents/33528/133297/bcch_archivo_164644_es.pdf/5c004bf3-b159-1ff4-78aa-b286738295b6

[5] Banco Central de Chile. Minutas citadas en el IPoM diciembre de 2024. Holguras en el mercado laboral, secciones 1 y 4, páginas 34 y 38 del PDF. https://www.bcentral.cl/documents/33528/6735463/Minutas%2Bcitadas%2Ben%2Bel%2BIPoM%2Bdiciembre%2B2024.pdf/d24985ae-cb5e-2f03-4499-ecfad3d86ade

[6] Banco Central de Chile. IPoM junio de 2026. La meta de inflación y la Tasa de Política Monetaria, página 3 del PDF. https://www.bcentral.cl/documents/33528/8413153/IPoM%2Bjunio%2B2026.pdf/93388589-0929-4ad6-b166-10981ca34946

Cálculos propios con los CSV del INE incluidos en el proyecto. Corte de archivos recibido el 22 de septiembre de 2026. Código, datos y gráfico: https://github.com/alejandrohenriquezr/curva_phillips
