# Publicación del cuaderno anual

La ejecución crea `cuadernos_jupyter/Curva_de_Phillips_anual.ipynb`, lo valida y ejecuta,
y exporta `site/cuaderno_curva_phillips.html`. El sitio enlaza únicamente los productos anuales
previstos; no copia indiscriminadamente carpetas con archivos de ejecuciones antiguas.

El workflow de CI valida Windows y Linux y almacena artefactos por plataforma. Para publicar
GitHub Pages, configure el origen como GitHub Actions y ejecute manualmente `pages.yml`
seleccionando `analisis_exclusivamente_anual`. Esto reemplaza el sitio público del repositorio:
la creación de la variante no ejecuta ese despliegue automáticamente.
