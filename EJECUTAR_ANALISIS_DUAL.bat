@echo off
setlocal
cd /d "%~dp0"

REM Verifica que el entorno se haya instalado antes de ejecutar.
if not exist ".venv\Scripts\python.exe" (
  echo Falta .venv. Ejecute primero INSTALAR_ANALISIS_DUAL.bat
  exit /b 1
)

REM Genera los informes anual, mensual y el HTML combinado con dos pestanas.
".venv\Scripts\python.exe" analisis_dual.py
if errorlevel 1 exit /b 1

REM Abre el informe combinado en el navegador predeterminado de Windows.
start "" "resultados\informe_phillips_dual.html"
exit /b 0