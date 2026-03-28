$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$requirementsPath = Join-Path $repoRoot "requirements.txt"

function Get-BasePythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }

    throw "Python was not found. Install Python 3.11+ and rerun this script."
}

if (-not (Test-Path $requirementsPath)) {
    throw "requirements.txt not found at $requirementsPath"
}

if (-not (Test-Path $venvPython)) {
    $basePython = Get-BasePythonCommand
    Write-Host "Creating .venv using $($basePython -join ' ')"
    if ($basePython.Length -gt 1) {
        & $basePython[0] $basePython[1] -m venv (Join-Path $repoRoot ".venv")
    }
    else {
        & $basePython[0] -m venv (Join-Path $repoRoot ".venv")
    }
}

Write-Host "Upgrading pip in .venv"
& $venvPython -m pip install --upgrade pip

Write-Host "Installing pinned requirements"
& $venvPython -m pip install -r $requirementsPath

Write-Host "Verifying required imports"
& $venvPython -c "import h5py, pypdf, rapidfuzz; print('Python environment ready')"

Write-Host ""
Write-Host "Interpreter:" $venvPython
Write-Host "Activation command: .\\.venv\\Scripts\\Activate.ps1"