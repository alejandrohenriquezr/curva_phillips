@echo off
cd /d "%~dp0"
set "PHILLIPS_ENV=%LOCALAPPDATA%\curva_phillips\venv"
if not exist "%PHILLIPS_ENV%\Scripts\python.exe" py -3 -m venv "%PHILLIPS_ENV%"
if not exist "%PHILLIPS_ENV%\Scripts\python.exe" (
  echo No se pudo crear el entorno. Instala Python 3.11 o superior.
  pause
  exit /b 1
)
"%PHILLIPS_ENV%\Scripts\python.exe" -m pip install -r requirements-notebook.txt
if errorlevel 1 (
  pause
  exit /b 1
)
echo Instalacion completa. Abre ABRIR_JUPYTER.bat
pause
