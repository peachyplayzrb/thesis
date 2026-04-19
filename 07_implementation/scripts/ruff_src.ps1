param(
    [switch]$Fix,
    [switch]$NoPreview,
    [string]$OutputFile = "ruff_src_report_latest.txt"
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

$ruffExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $workspaceRoot ".venv\Scripts\ruff.exe"),
    (Join-Path $implRoot ".venv\Scripts\ruff.exe")
)

if (-not $ruffExe) {
    throw "Ruff executable not found in workspace or implementation virtual environment."
}

$previewArgs = @()
if (-not $NoPreview) {
    $previewArgs += "--preview"
}

Push-Location $implRoot
try {
    if ($Fix) {
        & $ruffExe check src --fix @previewArgs | Out-Null
    }

    $output = & $ruffExe check src --output-format concise --statistics @previewArgs 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$outputPath = Join-Path $workspaceRoot $OutputFile

if ($exitCode -eq 0 -and @($output).Count -eq 0) {
    "All checks passed!" | Set-Content -Path $outputPath -Encoding utf8
}
else {
    @($output) | Set-Content -Path $outputPath -Encoding utf8
}

Write-Host "Ruff report written to: $outputPath"
exit $exitCode
