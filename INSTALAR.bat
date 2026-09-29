@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ================================================
echo Instalacion - Curva de Phillips Chile
echo ================================================

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: no se encontro Python 3.
    echo Instale Python 3.10 o superior y vuelva a ejecutar.
    exit /b 1
  )
  set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual .venv...
  %PY% -m venv .venv
  if errorlevel 1 exit /b 1
)
set "VPY=%CD%\.venv\Scripts\python.exe"

"%VPY%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
"%VPY%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
"%VPY%" -m pip install -e .
if errorlevel 1 exit /b 1

"%VPY%" -m jupyter --version >nul 2>nul
if errorlevel 1 (
  echo Jupyter no esta disponible. Instalando Notebook, JupyterLab y nbconvert...
  "%VPY%" -m pip install notebook jupyterlab nbconvert
  if errorlevel 1 exit /b 1
)

"%VPY%" -m ipykernel install --user --name curva-phillips --display-name "Python (curva_phillips)" >nul 2>nul

if not exist "herramientas\x13\x13as_ascii.exe" (
  echo Instalando X-13ARIMA-SEATS...
  "%VPY%" scripts\02_instalar_x13.py
  if errorlevel 1 echo ADVERTENCIA: X-13 no pudo instalarse. El modo IPC original sigue disponible.
)

echo.
echo Ejecutando pruebas...
"%VPY%" -m unittest discover -s tests -v
if errorlevel 1 (
  echo ERROR: la instalacion termino, pero las pruebas fallaron.
  exit /b 1
)

echo.
echo Instalacion completada.
echo Para ejecutar todo: EJECUTAR_TODO.bat
echo Para abrir Jupyter: ABRIR_JUPYTER.bat
exit /b 0
