param([int]$Port = 8000)

$ErrorActionPreference = 'Stop'
$raizProyecto = Split-Path $PSScriptRoot -Parent
$pythonLocal = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314\python.exe'
if (-not (Test-Path -LiteralPath $pythonLocal)) {
    throw 'No se encontro Python 3.14. Revise la instalacion local antes de iniciar.'
}

Push-Location $raizProyecto
try {
    $env:PYTHONPATH = "$raizProyecto\.deps-rag;$raizProyecto\.venv\Lib\site-packages"
    $env:PYTHONIOENCODING = 'utf-8'
    $env:HF_HOME = "$raizProyecto\.cache\huggingface"
    $env:HF_HUB_OFFLINE = '1'
    $env:TRANSFORMERS_OFFLINE = '1'
    $env:ANONYMIZED_TELEMETRY = 'False'
    & $pythonLocal -B -m uvicorn app.main:app --host 127.0.0.1 --port $Port
} finally {
    Pop-Location
}
