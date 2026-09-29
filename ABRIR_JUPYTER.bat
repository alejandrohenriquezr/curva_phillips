@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno .venv. Ejecute primero INSTALAR.bat
  exit /b 1
)

".venv\Scripts\python.exe" -m jupyter lab "%CD%\cuadernos_jupyter"
