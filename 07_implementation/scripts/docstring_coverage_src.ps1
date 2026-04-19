param(
    [switch]$Strict,
    [ValidateRange(0, 100)]
    [int]$FailUnder = 60,
    [string]$OutputFile = "interrogate_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent

function Resolve-PythonCandidates {
    $candidates = @(
        (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
        (Join-Path $implRoot ".venv\Scripts\python.exe")
    )

    $existing = @()
    foreach ($candidate in $candidates) {
        if ((Test-Path $candidate) -and -not ($existing -contains $candidate)) {
            $existing += $candidate
        }
    }

    return $existing
}

function Resolve-PythonWithInterrogate {
    $candidates = Resolve-PythonCandidates
    foreach ($candidate in $candidates) {
        & $candidate -c "import interrogate" *> $null
        if ($LASTEXITCODE -eq 0) {
            return $candidate
        }
    }

    if ($candidates.Count -gt 0) {
        return $candidates[0]
    }

    return $null
}

$pythonExe = Resolve-PythonWithInterrogate

if (-not $pythonExe) {
    throw "Python executable not found in workspace or implementation virtual environment."
}

$effectiveFailUnder = if ($Strict) { $FailUnder } else { 0 }
$mode = if ($Strict) { "strict" } else { "advisory" }

Push-Location $implRoot
try {
    $cmdOutput = & $pythonExe -m interrogate src --ignore-init-method --ignore-module --fail-under $effectiveFailUnder 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$lines = @($cmdOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
$outputPath = Join-Path $workspaceRoot $OutputFile

$reportLines = @()
$reportLines += "Docstring coverage report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src"
$reportLines += "mode: $mode"
$reportLines += "fail_under: $effectiveFailUnder"
$reportLines += ""

if ($lines.Count -eq 0) {
    $reportLines += "No interrogate output captured."
}
else {
    $reportLines += $lines
}

$reportLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Docstring coverage report written to: $outputPath"

exit $exitCode
