# Starts the ValveGuard API and thin client from the notebooks folder.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
powershell -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "start-demo.ps1")
