param(
    [string]$CodexRoot = "C:\Users\24136\AppData\Local\JetBrains\PyCharm2026.1\aia\codex"
)

$ErrorActionPreference = "Stop"

$binDir = Join-Path $CodexRoot "bin"
$targets = @(
    "codex-acp-x64-windows.exe",
    "codex-x86_64-pc-windows-msvc.exe"
)

foreach ($name in $targets) {
    $targetPath = Join-Path $binDir $name
    $backupPath = [IO.Path]::ChangeExtension($targetPath, ".real.exe")

    if (Test-Path $backupPath) {
        Copy-Item $backupPath $targetPath -Force
        Remove-Item $backupPath -Force
    }
}

foreach ($name in "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY") {
    [Environment]::SetEnvironmentVariable($name, $null, "User")
}
