# Setup script for Windows (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=== Recommendation System Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating Python virtual environment..." -ForegroundColor Green
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create virtual environment (.venv)."
}

Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

$venvPython = Join-Path ".\.venv\Scripts" "python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python executable not found at $venvPython"
}

Write-Host "Installing dependencies..." -ForegroundColor Green
& $venvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip/setuptools/wheel in virtual environment."
}

& $venvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install requirements.txt into virtual environment."
}

& $venvPython -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install project in editable mode."
}

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the environment: .\.venv\Scripts\Activate.ps1"
Write-Host "2. (Optional) Spotify credentials - only needed if regenerating live exports"
Write-Host "3. Run: python main.py --validate-only"
Write-Host ""
