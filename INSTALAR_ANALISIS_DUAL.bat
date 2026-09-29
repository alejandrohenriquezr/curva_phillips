@echo off
setlocal
cd /d "%~dp0"

REM Crea un entorno virtual aislado para el análisis anual/mensual.
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

REM Instala dependencias reproducibles del proyecto y statsmodels.
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r requirements-analisis.txt
if errorlevel 1 goto :error

echo.
echo Instalacion completada.
echo Ejecute EJECUTAR_ANALISIS_DUAL.bat para generar los informes.
exit /b 0

:error
echo.
echo ERROR: no fue posible completar la instalacion.
exit /b 1