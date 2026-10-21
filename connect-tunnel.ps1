param(
    [Parameter(Mandatory=$true)][string]$ClientPath,
    [Parameter(Mandatory=$true)][string]$ProfilePath
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $ClientPath -PathType Leaf)) { throw 'Tunnel client not found.' }
if (-not (Test-Path -LiteralPath $ProfilePath -PathType Leaf)) { throw 'Tunnel profile not found.' }
$previousKey = [Environment]::GetEnvironmentVariable('CONTROL_PLANE_API_KEY', 'Process')
$secureKey = Read-Host 'Paste your OpenAI tunnel runtime key (hidden)' -AsSecureString
$keyPointer = [IntPtr]::Zero
try {
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $env:CONTROL_PLANE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    & $ClientPath doctor --profile-file $ProfilePath --explain
    if ($LASTEXITCODE -ne 0) { throw 'Tunnel doctor failed. Review the output above.' }
    Write-Host 'Keep this window open while using ChatGPT. Ctrl+C stops the tunnel.'
    & $ClientPath run --profile-file $ProfilePath
    if ($LASTEXITCODE -ne 0) { throw 'Tunnel client stopped with an error.' }
} finally {
    [Environment]::SetEnvironmentVariable('CONTROL_PLANE_API_KEY', $previousKey, 'Process')
    if ($keyPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
    $secureKey.Dispose()
}
