param(
    [ValidateRange(0, 100)]
    [int]$FailUnder = 65,
    [string]$OutputFile = "coverage_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent

function Resolve-FirstExistingPath {
    param([string[]]$Candidates)

    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

$pythonExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $implRoot ".venv\Scripts\python.exe"),
    (Join-Path $workspaceRoot ".venv\Scripts\python.exe")
)

if (-not $pythonExe) {
    throw "Python executable not found in workspace or implementation virtual environment."
}

Push-Location $implRoot
try {
    $cmdOutput = & $pythonExe -m pytest tests -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=html:coverage_html --cov-fail-under $FailUnder 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$outputPath = Join-Path $workspaceRoot $OutputFile
$reportLines = @()
$reportLines += "Coverage workflow report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src"
$reportLines += "coverage_fail_under: $FailUnder"
$reportLines += ""
$reportLines += @($cmdOutput)

$reportLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Coverage report written to: $outputPath"

exit $exitCode
