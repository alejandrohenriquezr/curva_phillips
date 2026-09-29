# Despliegue del cuaderno Jupyter

El proyecto convierte el `.ipynb` ejecutado a HTML mediante `nbconvert`. Esto permite consultarlo desde un navegador sin iniciar Jupyter.

## Construcción local

```powershell
.\.venv\Scripts\python.exe scripts\07_construir_sitio.py
```

El resultado principal es `site/index.html`; el sitio contiene también el notebook original para descarga.

## GitHub Pages

Se incluye `.github/workflows/pages.yml`. La primera vez:

1. abrir **Settings > Pages**;
2. seleccionar **Source: GitHub Actions**;
3. abrir **Actions > Publicar informes y cuaderno**;
4. ejecutar **Run workflow**.

El workflow instala el proyecto, ejecuta el análisis, convierte el notebook a HTML y publica `site/`.

El despliegue es independiente del workflow de validación. Si Pages no está habilitado, las pruebas y la generación de artefactos siguen funcionando.
