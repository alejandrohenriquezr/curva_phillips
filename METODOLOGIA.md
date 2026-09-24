# IMACEC y fórmulas del gráfico

El promedio es de **tres meses**, centrado en el mes de la ENE. Se utiliza la serie **original** del IMACEC para el color y la serie **desestacionalizada oficial** para el panel inferior. Ambas son índices empalmados, promedio 2018=100. No se vuelve a desestacionalizar ni se confunden niveles con tasas.

Sea $I_t$ el índice original y $S_t$ el índice desestacionalizado mensual:

$$\bar I_t=(I_{t-1}+I_t+I_{t+1})/3$$

$$g_t=100\left(\frac{\bar I_t}{\bar I_{t-12}}-1\right)$$

El color usa $g_t$: **variación interanual del promedio de niveles**, no promedio de tres tasas interanuales. Por ejemplo, junio de 2026 compara mayo–julio de 2026 con mayo–julio de 2025. Requiere el dato del mes siguiente: es una visualización retrospectiva, no una señal disponible en tiempo real en junio. Con la alineación alternativa al mes final se usa $(I_{t-2}+I_{t-1}+I_t)/3$.

El panel muestra $S_t$ en las mismas fechas de los puntos. El cursor y el punto activo siguen el selector y Play. La línea oscura llega al mes seleccionado; la gris muestra el resto de la muestra como contexto retrospectivo. La variación mensual, incluida en los datos para el análisis, es:

$$m_t=100(S_t/S_{t-1}-1)$$

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
