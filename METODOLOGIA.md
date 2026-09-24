# IMACEC y fórmulas del gráfico

El promedio es de **tres meses**, centrado en el mes de la ENE. Se utiliza la serie **original** del IMACEC para el color y la serie **desestacionalizada oficial** para el panel inferior. Ambas son índices empalmados, promedio 2018=100. No se vuelve a desestacionalizar ni se confunden niveles con tasas.

Sea $I_t$ el índice original y $S_t$ el índice desestacionalizado mensual:

$$\bar I_t=(I_{t-1}+I_t+I_{t+1})/3$$

$$g_t=100\left(\frac{\bar I_t}{\bar I_{t-12}}-1\right)$$

El color usa $g_t$: **variación interanual del promedio de niveles**, no promedio de tres tasas interanuales. Por ejemplo, junio de 2026 compara mayo–julio de 2026 con mayo–julio de 2025. Requiere el dato del mes siguiente: es una visualización retrospectiva, no una señal disponible en tiempo real en junio. Con la alineación alternativa al mes final se usa $(I_{t-2}+I_{t-1}+I_t)/3$.

El panel inferior muestra las tasas en 12 meses del IMACEC desestacionalizado y del IPC:

$$a_t=100(S_t/S_{t-12}-1),\qquad \pi_t=100(IPC_t/IPC_{t-12}-1).$$

La inflación se toma de la tasa oficial publicada. La variación mensual del IMACEC se conserva en los datos como $m_t=100(S_t/S_{t-1}-1)$, pero no es la serie del panel. El cursor y la línea oscura siguen el mes seleccionado; el resto es contexto retrospectivo.

En cada diciembre, un rombo marca el crecimiento del **promedio anual del IMACEC original**:

$$G_Y=100\left(\frac{\sum_{m=1}^{12} I_{Y,m}}{\sum_{m=1}^{12} I_{Y-1,m}}-1\right).$$

Un cuadrado marca la inflación **diciembre contra diciembre**. Coincide con la tasa IPC a 12 meses publicada en diciembre; no se suman tasas redondeadas. No se dibujan cierres de años incompletos.

Tamaño y color de los puntos de diciembre usan una normalización común a las **tasas mensuales en 12 meses**, sobre toda la muestra:

$$L=\max(0.1,\max_t|a_t|,\max_t|\pi_t|),\quad n_t=v_t/L,\quad A_t=k|n_t|.$$

El color usa naranja en $-1$, claro en $0$ y azul en $+1$. La forma identifica la serie. La coordenada vertical muestra el acumulado, mientras tamaño y color codifican la tasa a 12 meses: ambas se detallan en el tooltip. La escala permanece fija en todos los fotogramas.

Cada enero de Phillips lleva una etiqueta MM-AAAA, además de 03-2020 y 08-2023. Los círculos entre marzo de 2020 y agosto de 2023, inclusive, tienen borde segmentado: período de pandemia Covid-19 en Chile **definido para esta visualización**. No se identifica este intervalo con toda la vigencia jurídica de la alerta sanitaria. Véase [Gobierno de Chile, fin de alerta el 31 de agosto de 2023](https://www.gob.cl/noticias/fin-alerta-sanitaria-covid-19-coronavirus-enfermedades-respiratorias-mascarillas-teletrabajo/).

**Otras variables y referencias**

- Desocupación: $u_t=100D_t/F_t$, donde $D$ son personas desocupadas y $F$ la fuerza de trabajo del trimestre móvil. Se usa la tasa publicada por INE.
- Inflación anual: $\pi_t=100(IPC_t/IPC_{t-12}-1)$. Se utiliza la variación publicada del IPC General, sin dividir índices de bases distintas.
- IR real anual: $r_t=100(IR^R_t/IR^R_{t-12}-1)$; se toma `var_12`, ya deflactada. Área de burbuja $A_t=k|r_t|$, con $k$ fijo; el signo del IR se consulta en el tooltip, no en el color. Si $r_t=0$, un centro fijo permite ubicar el punto.
- Normalización del color: $L=\max(\max_t|g_t|,0.1)$; $z_t=(g_t+L)/(2L)$. Naranja en $-L$, tono claro en $0$ y azul en $+L$. Escala simétrica y fija en todos los fotogramas, con barra lateral en porcentajes.
- Referencia vertical $u^*=(8.0+8.5)/2=8.25\%$, punto medio propio del rango BCCh histórico, no estimación puntual oficial. Distancias ilustrativas: $u_t-u^*$ y $\pi_t-3$, en puntos porcentuales.

La correlación descriptiva usa Pearson sobre las fechas comunes, sin interpretación causal:

$$\rho_{u,\pi}=\frac{\sum_t(u_t-\bar u)(\pi_t-\bar\pi)}{\sqrt{\sum_t(u_t-\bar u)^2\sum_t(\pi_t-\bar\pi)^2}}$$

**Precisión y reproducibilidad.** La tabla web BDE publica índices con un decimal. Las tasas derivadas son aproximaciones calculadas con esos índices redondeados; no se presentan como tasas oficiales exactas. Las series pueden revisarse. El CSV local permite ejecutar el cuaderno sin conexión. La descarga y sus códigos, fecha y hashes están en `actualizar_imacec.py` y `fuentes/imacec_metadata.json`. El cuaderno no descarga ni sobrescribe las fuentes.

Series BCCh: `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` (original) y `F032.IMC.IND.Z.Z.EP18.Z.Z.1.M` (desestacionalizada). [Descripción oficial del IMACEC](https://www.bcentral.cl/areas/estadisticas/imacec).

Para actualizar voluntariamente: `python actualizar_imacec.py`, luego `python phillips.py` y `python verificar_cuaderno.py`. La actualización de INE sigue en `python main.py`. Revisar el Word si cambia el corte; el análisis narrativo corresponde a enero de 2011–junio de 2026.

El borde distingue el año fuera de la ventana de pandemia; dentro se conserva el borde gris segmentado. El relleno sigue codificando IMACEC. Las salidas comparten la fecha y hora local de inicio AAAAMMDD_HH_MM.

## Desestacionalización experimental del IPC

`ipc_x13.py` invoca el ejecutable oficial X-13ARIMA-SEATS y solicita explícitamente la descomposición SEATS (no X-11). Entrada: niveles mensuales positivos del IPC General empalmado, con fechas únicas y sin huecos. No se rellenan faltantes ni se concatenan índices de bases diferentes. Se usa toda la serie diciembre de 2009–agosto de 2026, no solo la intersección con ENE e IR.

Especificación: logaritmos, `automdl`, atípicos automáticos AO/LS/TC, horizonte interno de 36 meses y SEATS sin aproximación automática de modelos inadmisibles. No se añaden feriados extranjeros ni regresores de días hábiles. Los pronósticos internos sirven al filtro y no se agregan como observaciones a los gráficos. La serie final es `s11`, que conserva el irregular: no debe confundirse con la tendencia `s12` ni con una inflación subyacente. `s10` y `s13` se conservan para auditoría.

Para índice ajustado A_t: mensual = 100(A_t/A_{t-1}−1); anual = 100(A_t/A_{t-12}−1). El cierre de diciembre usa la tasa anual de la variante seleccionada. En modo original se conservan tasas oficiales y faltantes; no se reemplazan por cálculos con niveles redondeados. La tabla comparativa agrega el cálculo anual sobre niveles originales como control de redondeo.

La estimación no es oficial del INE. Se vuelve a estimar al cambiar los datos, especificación o ejecutable. Utiliza información de toda la muestra y sus extremos están sujetos a revisión; no es una estimación en tiempo real. Los diagnósticos se guardan sin ocultar advertencias ni sustituir fallos por otro método. La ejecución actual detecta un pico de días de negociación en residuos; debe evaluarse calendario chileno y estabilidad antes de un uso oficial. Desestacionalizar el IPC no transforma la ENE o el IR y no elimina los problemas causales de una curva de Phillips descriptiva.

Fuente del software y documentación: [U.S. Census Bureau](https://www.census.gov/data/software/x13as.X-13ARIMA-SEATS.html). [Manual de referencia](https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13as.pdf).
