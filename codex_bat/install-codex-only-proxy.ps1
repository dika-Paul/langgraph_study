param(
    [string]$CodexRoot = "C:\Users\24136\AppData\Local\JetBrains\PyCharm2026.1\aia\codex"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$binDir = Join-Path $CodexRoot "bin"
$sourcePath = Join-Path $scriptRoot "CodexProxyWrapper.cs"
$templatePath = Join-Path $scriptRoot "CodexProxyWrapperTemplate.exe"
$targets = @(
    "codex-acp-x64-windows.exe",
    "codex-x86_64-pc-windows-msvc.exe"
)

Add-Type -Path $sourcePath -OutputAssembly $templatePath -OutputType ConsoleApplication

foreach ($name in $targets) {
    $targetPath = Join-Path $binDir $name
    $backupPath = [IO.Path]::ChangeExtension($targetPath, ".real.exe")

    if (-not (Test-Path $backupPath)) {
        Copy-Item $targetPath $backupPath -Force
    }

    Copy-Item $templatePath $targetPath -Force
}

foreach ($name in "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY") {
    [Environment]::SetEnvironmentVariable($name, $null, "User")
}
