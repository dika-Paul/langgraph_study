param(
    [string]$CodexRoot = "C:\Users\24136\AppData\Local\JetBrains\PyCharm2026.1\aia\codex"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$installScript = Join-Path $scriptRoot "install-codex-only-proxy.ps1"

while (Get-Process -Name pycharm64 -ErrorAction SilentlyContinue) {
    Start-Sleep -Seconds 3
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $installScript -CodexRoot $CodexRoot
