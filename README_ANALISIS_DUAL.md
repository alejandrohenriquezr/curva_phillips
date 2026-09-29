# Análisis anual y mensual de la Curva de Phillips

Esta extensión del proyecto `curva_phillips` genera dos análisis econométricos y tres HTML:

- `resultados/informe_phillips_anual.html`: datos anuales 2011–2025; 2010 se usa como rezago.
- `resultados/informe_phillips_mensual.html`: 186 meses comunes, enero de 2011 a junio de 2026.
- `resultados/informe_phillips_dual.html`: las dos versiones anteriores reunidas en dos pestañas: **Datos anuales** y **Datos mensuales**.

La NAIRU referencial se fija en **8,25%** y el IPC corresponde a la serie oficial no desestacionalizada.

## Qué se estima

### Informe anual

La especificación central impone que la inflación no acelera cuando el desempleo coincide con la NAIRU:

```text
Δπ_t = β (u_t - 8,25) + ε_t
```

Con la tabla anualizada entregada para el proyecto, la estimación reproducida es aproximadamente:

```text
Δπ_t = -0,126 (u_t - 8,25)
```

El script también estima una curva estática, una versión de aceleración con constante, una versión con inflación rezagada y otra que incorpora actividad económica. Los errores estándar son HAC/Newey-West con un rezago.

### Informe mensual

La misma ecuación se replica con cambio de la inflación a doce meses respecto de doce meses atrás:

```text
Δ12π_t = β (u_t - 8,25) + ε_t
```

Además se comparan modelos en niveles con inflación rezagada, brecha de desempleo y actividad. El informe identifica el menor BIC solo entre modelos que comparten la misma variable dependiente. Los errores estándar son HAC/Newey-West con 12 rezagos.

## Instalación en Windows

### Opción 1: proyecto ya clonado

Copiar estos archivos a la raíz del repositorio `curva_phillips`:

```text
analisis_dual.py
datos_anualizados.csv
datos_anualizados.xlsx   # opcional; si existe se usa antes que el CSV
requirements-analisis.txt
INSTALAR_ANALISIS_DUAL.bat
EJECUTAR_ANALISIS_DUAL.bat
test_analisis_dual.py
```

Ejecutar una sola vez:

```bat
INSTALAR_ANALISIS_DUAL.bat
```

Luego generar los informes con:

```bat
EJECUTAR_ANALISIS_DUAL.bat
```

El BAT abre automáticamente `resultados\informe_phillips_dual.html`.

### Opción 2: clonar desde GitHub

```powershell
git clone -b analisis_anual_mensual https://github.com/alejandrohenriquezr/curva_phillips.git
cd curva_phillips
.\INSTALAR_ANALISIS_DUAL.bat
.\EJECUTAR_ANALISIS_DUAL.bat
```

## Ejecución manual

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-analisis.txt
.\.venv\Scripts\python.exe analisis_dual.py
```

Para usar explícitamente el XLSX original:

```powershell
.\.venv\Scripts\python.exe analisis_dual.py --anual datos_anualizados.xlsx
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest test_analisis_dual -v
```

Las pruebas verifican la pendiente anual con NAIRU impuesta, la cobertura mensual de 186 meses, el modelo mensual seleccionado por BIC y la presencia de las dos pestañas en el HTML combinado.

## Archivos de resultados

Además de los HTML se generan:

```text
resultados/modelos_anuales.csv
resultados/coeficientes_anuales.csv
resultados/modelos_mensuales.csv
resultados/coeficientes_mensuales.csv
resultados/resumen_modelos.json
```

## Interpretación

Los modelos son descriptivos. La NAIRU de 8,25% se mantiene fija por decisión del ejercicio y no se reestima para cada año o mes. AIC y BIC se comparan únicamente entre especificaciones con la misma variable dependiente. Los errores HAC corrigen la inferencia por autocorrelación y heterocedasticidad, pero no convierten las asociaciones en efectos causales.