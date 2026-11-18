# Manager AI PRO — Quick One-Line Installer & Launcher (PowerShell `irm | iex`)
# Usage: irm https://raw.githubusercontent.com/othmx/Manager-AI-PRO/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   ✦  M A N A G E R   A I   P R O  ✦                      ║" -ForegroundColor Cyan
Write-Host "║            Quick Installer & Launcher (PT-BR / EN / ZH-CN)               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$TargetDir = Join-Path $env:USERPROFILE "Desktop\Manager-AI-PRO"
$RepoZip = "https://github.com/othmx/Manager-AI-PRO/archive/refs/heads/main.zip"
$TmpZip = Join-Path $env:TEMP "Manager-AI-PRO-main.zip"
$TmpExtract = Join-Path $env:TEMP "Manager-AI-PRO-extract"

if (Get-Command git -ErrorAction SilentlyContinue) {
    if (Test-Path (Join-Path $TargetDir ".git")) {
        Write-Host "▶ Updating existing installation at $TargetDir..." -ForegroundColor Yellow
        git -C $TargetDir pull --ff-only
    } else {
        if (Test-Path $TargetDir) { Remove-Item -Recurse -Force $TargetDir }
        Write-Host "▶ Cloning Manager-AI-PRO into $TargetDir..." -ForegroundColor Cyan
        git clone https://github.com/othmx/Manager-AI-PRO.git $TargetDir
    }
} else {
    Write-Host "▶ Downloading Manager-AI-PRO package..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $RepoZip -OutFile $TmpZip
    if (Test-Path $TmpExtract) { Remove-Item -Recurse -Force $TmpExtract }
    Expand-Archive -Path $TmpZip -DestinationPath $TmpExtract -Force
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir | Out-Null }
    Copy-Item -Path (Join-Path $TmpExtract "Manager-AI-PRO-main\*") -Destination $TargetDir -Recurse -Force
    Remove-Item -Force $TmpZip -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $TmpExtract -ErrorAction SilentlyContinue
}

Write-Host "✅ Installed at: $TargetDir" -ForegroundColor Green
Write-Host "▶ Launching Manager AI PRO..." -ForegroundColor Cyan
Set-Location $TargetDir
$env:PYTHONIOENCODING = "utf-8"
python "$TargetDir\manager_ai_pro.py"
