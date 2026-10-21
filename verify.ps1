param([switch]$Live)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if ($Live) {
        & '.\.venv\Scripts\python.exe' -m pytest -q tests
    } else {
        & '.\.venv\Scripts\python.exe' -m pytest -q -m 'not live' tests
    }
    if ($LASTEXITCODE -ne 0) { throw 'Verification failed.' }
} finally { Pop-Location }
