# Metodología anual

Fuente canónica: `datos/datos_anualizados2.xlsx`, hoja inicial, cuatro columnas originales.
El importador conserva todos los valores, exige años únicos y consecutivos 1997–2026,
valores numéricos finitos y desempleo entre 0 y 100. Exporta un CSV cronológico y un manifiesto SHA-256.
No escala porcentajes automáticamente ni corrige valores de PIB. El PIB se usa como variación
según la indicación del usuario; no representa una brecha de producto y no ha sido conciliado
con otras estadísticas. La validez económica depende de la comparabilidad de la fuente.

## Corte de 2026

La observación 2026 es julio 2026 frente a julio 2025. Se identifica en tablas, figuras,
artículo y cuaderno. La historia usa 1998–2025 (1997 aporta el primer rezago); la sensibilidad
usa 1998–2026. En esta última, restar IPC 2025 al IPC de julio de 2026 mezcla cortes distintos:
no es una aceleración anual homogénea. No se trata como cierre anual ni como pronóstico.

## Especificaciones

1. IPC en función de constante y brecha de desempleo.
2. Cambio de IPC en función de constante y brecha.
3. IPC con constante, inflación rezagada y brecha.
4. Especificación anterior más PIB.
5. Cambio de IPC con constante, brecha y PIB.
6. Cambio de IPC en función de brecha sin constante.

Brecha = desempleo − 8,25. El 8,25 es un supuesto del ejercicio, no una estimación histórica.
Se usa OLS con covarianza HAC, rezago 1, corrección de muestra y referencia t para p-valores
e intervalos al 95%. HAC es aproximado en muestras pequeñas. El signo esperado de la pendiente
de brecha es negativo. Los resultados describen asociaciones, no efectos causales.

Todos los modelos de un escenario tienen la misma muestra efectiva. AIC/BIC se comparan sólo
para igual dependiente y escenario. El R² sin constante es no centrado y no debe compararse
directamente con el R² centrado. No se selecciona automáticamente un modelo por su signo.

## Estabilidad

Ventanas predefinidas 1998–2009, 2010–2019, 2011–2025 y exclusión 2020–2023; exclusión de un año
por vez; referencia de desempleo 8,0/8,25/8,5 y HAC 0/1/2. Son sensibilidades exploratorias,
no tests formales de quiebre ni pruebas múltiples confirmatorias. Los rezagos se calculan antes
de las exclusiones y nunca se unen años separados. Las cifras no miden pobreza, salarios reales,
informalidad ni impactos distributivos; el artículo explica mecanismos y necesidades de información.
