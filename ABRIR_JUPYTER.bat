@echo off
cd /d "%~dp0"
set "PHILLIPS_PYTHON=%LOCALAPPDATA%\curva_phillips\venv\Scripts\python.exe"
if not exist "%PHILLIPS_PYTHON%" (
  echo Primero ejecuta INSTALAR.bat
  pause
  exit /b 1
)
"%PHILLIPS_PYTHON%" -m notebook "Curva_de_Phillips.ipynb"
if errorlevel 1 pause
