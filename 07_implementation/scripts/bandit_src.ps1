param(
    [switch]$Strict,
    [string]$OutputFile = "bandit_src_report_latest.txt"
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

$ruffExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $implRoot ".venv\Scripts\ruff.exe"),
    (Join-Path $workspaceRoot ".venv\Scripts\ruff.exe")
)

if (-not $pythonExe) {
    throw "Python executable not found in workspace or implementation virtual environment."
}

if (-not $ruffExe) {
    throw "Ruff executable not found in workspace or implementation virtual environment."
}

$mode = if ($Strict) { "strict" } else { "advisory" }
$activeScanner = "bandit"
$scanOutput = @()
$scanExitCode = 0

$banditArgs = @("-m", "bandit", "-r", "src", "-f", "txt")
if (-not $Strict) {
    $banditArgs += "--exit-zero"
}

Push-Location $implRoot
try {
    $banditOutput = & $pythonExe @banditArgs 2>&1
    $banditExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$banditLines = @($banditOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
$banditJoined = ($banditLines -join "`n")
$banditAstCompatibilityError = $banditJoined -match "module 'ast' has no attribute 'Num'"

if ($banditAstCompatibilityError) {
    $activeScanner = "ruff-security-fallback"

    Push-Location $implRoot
    try {
        $ruffOutput = & $ruffExe check src --select S 2>&1
        $ruffExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $scanOutput = @($ruffOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })

    if ($Strict) {
        $scanExitCode = $ruffExitCode
    }
    else {
        $scanExitCode = 0
    }
}
else {
    $scanOutput = $banditLines
    $scanExitCode = $banditExitCode
}

$outputPath = Join-Path $workspaceRoot $OutputFile

$reportLines = @()
$reportLines += "Bandit security scan report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src"
$reportLines += "mode: $mode"
$reportLines += "active_scanner: $activeScanner"
$reportLines += ""

if ($banditAstCompatibilityError) {
    $reportLines += "[note]"
    $reportLines += "Bandit reported Python 3.14 AST compatibility errors; security scan fell back to Ruff S-rules."
    $reportLines += ""
}

if ($scanOutput.Count -eq 0) {
    $reportLines += "No security findings output captured."
}
else {
    $reportLines += $scanOutput
}

$reportLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Bandit report written to: $outputPath"

exit $scanExitCode
