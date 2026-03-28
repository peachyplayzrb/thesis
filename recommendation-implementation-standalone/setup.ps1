# Setup script for Windows (PowerShell)

Write-Host "=== Recommendation System Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating Python virtual environment..." -ForegroundColor Green
python -m venv .venv

Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..." -ForegroundColor Green
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the environment: .\.venv\Scripts\Activate.ps1"
Write-Host "2. Download the Music4All dataset and extract it"
Write-Host "3. Run: python main.py --dataset-root C:\path\to\music4all\ --validate-only"
Write-Host ""
