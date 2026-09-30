@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno .venv. Ejecute primero INSTALAR.bat
  exit /b 1
)

REM Expone src/ al kernel de Jupyter. Esto permite importar curva_phillips
REM incluso al abrir un cuaderno antiguo desde cuadernos_jupyter.
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

".venv\Scripts\python.exe" -m jupyter lab "%CD%\cuadernos_jupyter"
