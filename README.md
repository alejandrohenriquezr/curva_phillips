# Curva de Phillips de Chile

Proyecto reproducible para estudiar la Curva de Phillips en Chile con dos frecuencias. El análisis anual usa desempleo, IPC y PIB para 1997–2025; el análisis mensual usa ENE, IPC, IR real e IMACEC para enero de 2011–junio de 2026. Ambos mantienen una NAIRU referencial de 8,25% y generan informes HTML/Word, resultados tabulares, un cuaderno Jupyter ejecutado y un sitio estático listo para GitHub Pages.

## Estructura

```text
curva_phillips/
├─ datos/                  Fuentes CSV versionadas y metadatos
├─ scripts/                Entradas ejecutables 00_...py a 08_...py
├─ src/curva_phillips/     Código reutilizable
├─ tests/                  Pruebas automáticas
├─ documentacion/          Metodología, referencias y manuales
├─ cuadernos_jupyter/      Cuadernos generados (no versionados)
├─ informes/               HTML, Word y Markdown generados (no versionados)
├─ resultados/             CSV, JSON, PNG y HTML técnicos (no versionados)
├─ site/                   Sitio estático generado para publicación
├─ INSTALAR.bat
├─ EJECUTAR_TODO.bat
└─ ABRIR_JUPYTER.bat
```

Los directorios de salida permanecen vacíos en Git mediante `.gitkeep`. Cada ejecución los vuelve a poblar. Así se evitan notebooks, gráficos e informes históricos duplicados dentro del repositorio.

## Instalación en Windows

```powershell
git clone -b estructura_ordenada https://github.com/alejandrohenriquezr/curva_phillips.git
cd curva_phillips
.\INSTALAR.bat
```

El instalador crea `.venv`, instala las dependencias, instala el paquete local en modo editable, verifica Jupyter, registra el kernel `Python (curva_phillips)`, intenta instalar X-13ARIMA-SEATS y ejecuta las pruebas.

## Ejecución completa

```powershell
.\EJECUTAR_TODO.bat
```

Por defecto usa el IPC oficial original. Para la variante experimental desestacionalizada:

```powershell
.\EJECUTAR_TODO.bat --ipc sa
```

Para actualizar antes las fuentes INE y BCCh:

```powershell
.\EJECUTAR_TODO.bat --actualizar-datos
```

Al finalizar se genera `site/index.html`, que reúne los informes y la versión HTML del cuaderno.

## Jupyter

```powershell
.\ABRIR_JUPYTER.bat
```

El cuaderno ejecutado queda en `cuadernos_jupyter/`. El proceso también lo convierte a HTML mediante nbconvert para poder verlo sin Jupyter.

## Publicación del cuaderno

El workflow `.github/workflows/pages.yml` reconstruye el proyecto, convierte el notebook a HTML y publica `site/` con GitHub Pages. La primera vez se debe habilitar **Settings > Pages > Source: GitHub Actions** y luego ejecutar manualmente el workflow **Publicar informes y cuaderno**.

La publicación usa una copia HTML del notebook porque un archivo `.ipynb` no se renderiza como página web autónoma. El `.ipynb` original también se copia al sitio como descarga.

## Documentación

- [Instalación y uso](documentacion/INSTALACION_Y_USO.md)
- [Estructura técnica](documentacion/ESTRUCTURA.md)
- [Metodología](documentacion/METODOLOGIA.md)
- [Análisis anual y mensual](documentacion/ANALISIS_ANUAL_MENSUAL.md)
- [Despliegue del cuaderno](documentacion/DESPLIEGUE_CUADERNO.md)
- [Referencias](documentacion/REFERENCIAS.md)

## Validación automática

El workflow `Validar y generar productos` instala las dependencias, ejecuta las pruebas, genera el cuaderno, los informes y el sitio, y conserva todos los productos como artefacto descargable.

## Orden de la animación

El gráfico animado recorre las observaciones mensuales por **tasa de desocupación ascendente**, no por fecha. El panel inferior conserva IPC e IMACEC en orden cronológico y marca la fecha correspondiente a la observación activa. `resultados/datos_phillips.csv` se exporta en el mismo orden que la animación.

## Tabla anual vigente

`datos/datos_anualizados.csv` reproduce la nueva tabla entregada para el proyecto: **1997–2025**, con `Año`, `Tasa desocupación`, `IPC` y `PIB volumen a precios del año anterior encadenado`. El análisis anual ya no utiliza IR. El IR permanece únicamente en el componente mensual porque proviene de una fuente mensual independiente.
