# Curva de Phillips anual en Chile

Variante independiente `analisis_exclusivamente_anual`, basada en `estructura_ordenada`.
La rama de origen se conserva. El Excel `datos/datos_anualizados2.xlsx` es la fuente canónica
y contiene 30 observaciones (1997–2026) de desempleo, IPC y PIB.

**2026 es julio 2026 respecto de julio 2025, no un año calendario completo.** Se conserva
exactamente como fue entregado. La historia hasta 2025 y la sensibilidad con 2026 se
identifican en cada modelo. No se sustituyen valores por fuentes externas.

## Ejecutar en Windows

```powershell
git fetch origin
git switch --track origin/analisis_exclusivamente_anual
.\INSTALAR.bat
.\EJECUTAR_TODO.bat
.\ABRIR_JUPYTER.bat
```

Si la rama ya existe localmente, use `git switch analisis_exclusivamente_anual` y
`git pull --ff-only`. Conserve sus cambios locales antes de cambiar de rama.

## Ejecutar en Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
python scripts/08_ejecutar_todo.py
```

Después de instalar dependencias, el procesamiento no necesita conexión a fuentes de datos.
Abra `site/index.html` para ver el informe, animación y cuaderno ejecutado, o descargar el Word.
La animación y `resultados/datos_phillips.csv` recorren desempleo de menor a mayor; los cálculos
y `datos_anuales_cronologicos.csv` mantienen el orden de los años.

## Productos y metodología

El pipeline valida el Excel, ejecuta las pruebas, estima modelos, ejecuta el cuaderno,
genera el artículo Word/Markdown y construye el sitio. Deja `resultados/ejecucion_anual.json`.
Los productos se regeneran y se publican como artefactos de CI; no se versionan.
Los modelos incorporan PIB, persistencia, intervalos HAC y sensibilidades de muestra.
Consulte [metodología](documentacion/METODOLOGIA.md),
[instalación](documentacion/INSTALACION_Y_USO.md) y [estructura](documentacion/ESTRUCTURA.md).

GitHub Actions valida el pipeline en Linux y Windows. GitHub Pages se publica únicamente
mediante ejecución manual del workflow, seleccionando esta rama; no se publica al hacer push.
