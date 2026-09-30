# Análisis anual y mensual de la Curva de Phillips

Esta extensión del proyecto `curva_phillips` genera dos análisis econométricos y tres HTML:

- `informes/informe_phillips_anual.html`: datos anuales 1986–2025; la ecuación de aceleración comienza en 1987. IR está disponible desde 2006 y actividad desde 2010.
- `informes/informe_phillips_mensual.html`: 186 meses comunes, enero de 2011 a junio de 2026.
- `informes/informe_phillips_dual.html`: las dos versiones anteriores reunidas en dos pestañas: **Datos anuales** y **Datos mensuales**.

La NAIRU referencial se fija en **8,25%** y el IPC corresponde a la serie oficial no desestacionalizada.

## Qué se estima

### Informe anual

La especificación central impone que la inflación no acelera cuando el desempleo coincide con la NAIRU:

```text
Δπ_t = β (u_t - 8,25) + ε_t
```

Con la tabla anualizada actualizada, la muestra larga reproduce aproximadamente:

```text
1987–2025: Δπ_t = -0,240 (u_t - 8,25)
```

Como contraste de comparabilidad, la ventana utilizada anteriormente se conserva:

```text
2011–2025: Δπ_t = -0,126 (u_t - 8,25)
```

El script también estima una curva estática, una versión de aceleración con constante, una versión con inflación rezagada, una especificación con IR y otra con actividad económica. Debido a la disponibilidad desigual de IR y actividad, cada modelo informa su tamaño muestral efectivo. Los errores estándar son HAC/Newey-West con un rezago.

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
scripts/06_analisis_anual_mensual.py
datos/datos_anualizados.csv
datos/datos_anualizados.xlsx   # opcional; si existe se usa antes que el CSV
requirements.txt
INSTALAR.bat
EJECUTAR_TODO.bat
test_scripts/06_analisis_anual_mensual.py
```

Ejecutar una sola vez:

```bat
INSTALAR.bat
```

Luego generar los informes con:

```bat
EJECUTAR_TODO.bat
```

El BAT abre automáticamente `site\index.html`, desde donde se accede al informe combinado y al cuaderno.

### Opción 2: clonar desde GitHub

```powershell
git clone -b estructura_ordenada https://github.com/alejandrohenriquezr/curva_phillips.git
cd curva_phillips
.\INSTALAR.bat
.\EJECUTAR_TODO.bat
```

## Ejecución manual

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/06_analisis_anual_mensual.py
```

Para usar explícitamente el XLSX original:

```powershell
.\.venv\Scripts\python.exe scripts/06_analisis_anual_mensual.py --anual datos/datos_anualizados.xlsx
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas verifican la muestra anual 1986–2025, la pendiente central 1987–2025, el contraste 2011–2025, la cobertura mensual de 186 meses, el modelo mensual seleccionado por BIC y la presencia de las dos pestañas en el HTML combinado.

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

Los modelos son descriptivos. La NAIRU de 8,25% se mantiene fija por decisión del ejercicio y no se reestima para cada año o mes. AIC y BIC se comparan únicamente entre especificaciones con la misma variable dependiente y la misma muestra efectiva. Los errores HAC corrigen la inferencia por autocorrelación y heterocedasticidad, pero no convierten las asociaciones en efectos causales.

## Advertencia sobre la NAIRU en la muestra larga

La referencia de 8,25% se mantiene fija por decisión del ejercicio. No debe interpretarse como una estimación histórica de la NAIRU válida para todo 1986–2025. La ampliación de la muestra sirve para evaluar estabilidad y sensibilidad de la relación de Phillips, no para atribuir a 8,25% el carácter de tasa natural constante durante cuatro décadas.
