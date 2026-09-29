@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno .venv. Ejecute primero INSTALAR.bat
  exit /b 1
)

".venv\Scripts\python.exe" scripts\08_ejecutar_todo.py %*
if errorlevel 1 exit /b 1

if exist "site\index.html" start "" "site\index.html"
exit /b 0
