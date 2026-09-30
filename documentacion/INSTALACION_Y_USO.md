# Instalación y uso

## Primera instalación

```powershell
git clone -b estructura_ordenada https://github.com/alejandrohenriquezr/curva_phillips.git
cd curva_phillips
.\INSTALAR.bat
```

El instalador crea `.venv`, instala `requirements.txt`, instala el paquete `curva_phillips` en modo editable y comprueba Jupyter. Si Jupyter no responde, instala explícitamente Notebook, JupyterLab y nbconvert. También registra el kernel `Python (curva_phillips)`.

## Ejecución

```powershell
.\EJECUTAR_TODO.bat
```

Variantes:

```powershell
.\EJECUTAR_TODO.bat --ipc sa
.\EJECUTAR_TODO.bat --actualizar-datos
.\EJECUTAR_TODO.bat --fecha 20260928_23_45
```

## Jupyter

```powershell
.\ABRIR_JUPYTER.bat
```

El cuaderno queda en `cuadernos_jupyter/` y ya fue ejecutado por el orquestador.

## Actualización de la rama

```powershell
git fetch origin
git switch estructura_ordenada
git pull origin estructura_ordenada
.\INSTALAR.bat
```

## Si el cuaderno muestra `ModuleNotFoundError: curva_phillips`

Regenera el cuaderno con `EJECUTAR_TODO.bat` o `python scripts/03_generar_cuaderno.py`. La primera celda localiza automáticamente la raíz del repositorio y agrega `src/` a `sys.path`, por lo que funciona tanto si Jupyter se abrió desde la raíz como desde `cuadernos_jupyter/`.
