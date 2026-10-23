param([switch]$SoloPreparar)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$environmentPath = Join-Path $root 'venv'

function Test-CompatiblePython([string]$Executable, [string[]]$Prefix = @()) {
    if (-not $Executable) { return $false }
    try {
        & $Executable @Prefix -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in [(3,11),(3,12),(3,13)] and sys.maxsize > 2**32 else 1)' 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

$python = Join-Path $environmentPath 'Scripts\python.exe'
if (-not (Test-CompatiblePython $python)) {
    $selected = $null
    $prefix = @()
    # Reutilizar un Python compatible instalado para el proyecto.
    $candidates = @(
        $env:PHILLIPS_PYTHON,
        (Join-Path $root '.venv\Scripts\python.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-CompatiblePython $candidate) { $selected = $candidate; break }
    }
    if (-not $selected) {
        foreach ($version in @('-3.13','-3.12','-3.11')) {
            if (Test-CompatiblePython 'py' @($version)) {
                $selected = 'py'; $prefix = @($version); break
            }
        }
    }
    if (-not $selected -and (Test-CompatiblePython 'python')) { $selected = 'python' }
    if (-not $selected) {
        throw 'Instala Python 3.13 de 64 bits o define PHILLIPS_PYTHON con la ruta de un Python 3.11, 3.12 o 3.13 de 64 bits.'
    }
    if (Test-Path -LiteralPath $environmentPath) {
        # Solo mover el entorno exacto de este proyecto, nunca una ruta externa.
        $expected = [IO.Path]::GetFullPath((Join-Path $root 'venv'))
        $actual = (Resolve-Path -LiteralPath $environmentPath).Path
        if ($actual -ne $expected -or ((Get-Item -LiteralPath $actual).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'El entorno es un enlace o apunta fuera del proyecto. Revisa la carpeta venv.'
        }
        $backup = Join-Path $root ('venv_incompatible_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0,6))
        Move-Item -LiteralPath $actual -Destination $backup
        Write-Host "Entorno anterior conservado en: $backup"
    }
    & $selected @prefix -m venv $environmentPath
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno compatible.' }
}
if (-not (Test-CompatiblePython $python)) { throw 'El entorno creado no tiene un Python compatible.' }
& $python -c 'import sys; print(sys.version); print(sys.executable)'
$pipReady = $false
try { & $python -m pip --version 2>$null | Out-Null; $pipReady = $LASTEXITCODE -eq 0 } catch { $pipReady = $false }
if (-not $pipReady) {
    & $python -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar pip en el entorno.' }
}
if ($SoloPreparar) { exit 0 }
& $python -m pip install --only-binary=:all: -r (Join-Path $root 'dependencias\requirements-completo.txt')
if ($LASTEXITCODE -ne 0) { throw 'Fallo la instalacion de dependencias. No se marca la instalacion como completa.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Hay dependencias incompatibles en el entorno.' }
Write-Host 'Instalacion completa. Ejecuta EJECUTAR_TODO.bat o ABRIR_JUPYTER.bat.'
