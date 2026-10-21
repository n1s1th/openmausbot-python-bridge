param([switch]$AllowWrites)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Run setup.ps1 first.' }
$bridge = Join-Path $PSScriptRoot 'bridge.py'
if ($AllowWrites) { & $python $bridge --allow-writes } else { & $python $bridge }
exit $LASTEXITCODE
