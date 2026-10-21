$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Install Node.js LTS first.' }
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ is required.' }
    }
    & '.\.venv\Scripts\python.exe' -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) { throw 'Could not install pip into the virtual environment.' }
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
} finally { Pop-Location }
