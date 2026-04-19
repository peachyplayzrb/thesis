$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")

Write-Host "=== Preflight Checks (Windows) ===" -ForegroundColor Cyan
Write-Host "Implementation root: $implRoot"

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Resolve-PythonExecutable {
    param([string]$ImplementationRoot)

    $workspaceRoot = Split-Path $ImplementationRoot -Parent
    $candidates = @(
        (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
        (Join-Path $ImplementationRoot ".venv\Scripts\python.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    if (Test-CommandAvailable -Name "python") {
        return "python"
    }

    return $null
}

$pythonExe = Resolve-PythonExecutable -ImplementationRoot $implRoot
if ($null -eq $pythonExe) {
    throw "Python executable not found in workspace/local .venv or PATH. Install Python 3.10+ and reopen terminal."
}

$versionLine = & $pythonExe --version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Unable to determine Python version using '$pythonExe'."
}

if ($versionLine -match "Python\s+(\d+)\.(\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
        throw "Python 3.12+ is required. Found: $versionLine"
    }
    if (-not ($major -eq 3 -and $minor -eq 14)) {
        Write-Warning "Validated environment is Python 3.14.x. Found: $versionLine — behaviour may differ."
    }
    Write-Host "PASS: Python version $versionLine" -ForegroundColor Green
}
else {
    throw "Could not parse Python version output: $versionLine"
}

if (Test-CommandAvailable -Name "git") {
    Write-Host "PASS: Git available" -ForegroundColor Green
}
else {
    Write-Warning "Git is not available on PATH."
}

if (Test-CommandAvailable -Name "rg") {
    Write-Host "PASS: ripgrep available" -ForegroundColor Green
}
else {
    Write-Warning "ripgrep is not available on PATH. VS Code search fallback is still supported."
}

$datasetPath = Join-Path $implRoot "src/data_layer/outputs/ds001_working_candidate_dataset.csv"
if (-not (Test-Path $datasetPath)) {
    throw "Missing embedded dataset: $datasetPath"
}
Write-Host "PASS: Embedded DS-001 dataset found" -ForegroundColor Green

$spotifyExportPath = Join-Path $implRoot "src/ingestion/outputs/spotify_api_export"
if (-not (Test-Path $spotifyExportPath -PathType Container)) {
    throw "Missing embedded Spotify export bundle directory: $spotifyExportPath"
}
Write-Host "PASS: Embedded Spotify export bundle found" -ForegroundColor Green

Write-Host "PASS: Preflight checks complete" -ForegroundColor Green
