param(
    [switch]$Strict,
    [string]$OutputFile = "hygiene_src_report_latest.txt",
    [ValidateRange(1, 100)]
    [int]$MinConfidence = 70,
    [ValidateSet("A", "B", "C", "D", "E", "F")]
    [string]$ComplexityThreshold = "C"
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

$vultureExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $workspaceRoot ".venv\Scripts\vulture.exe"),
    (Join-Path $workspaceRoot ".venv-1\Scripts\vulture.exe"),
    (Join-Path $implRoot ".venv\Scripts\vulture.exe")
)

$radonExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $workspaceRoot ".venv\Scripts\radon.exe"),
    (Join-Path $workspaceRoot ".venv-1\Scripts\radon.exe"),
    (Join-Path $implRoot ".venv\Scripts\radon.exe")
)

if (-not $vultureExe) {
    throw "Vulture executable not found in workspace or implementation virtual environment."
}

if (-not $radonExe) {
    throw "Radon executable not found in workspace or implementation virtual environment."
}

Push-Location $implRoot
try {
    $deadCodeOutput = & $vultureExe src --min-confidence $MinConfidence --sort-by-size 2>&1
    $deadCodeExit = $LASTEXITCODE

    $complexityOutput = & $radonExe cc src -s -n $ComplexityThreshold 2>&1
    $complexityExit = $LASTEXITCODE
}
finally {
    Pop-Location
}

$deadCodeLines = @($deadCodeOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
$complexityLines = @($complexityOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })

$hasDeadCodeFindings = $deadCodeLines.Count -gt 0
$hasComplexityFindings = $complexityLines.Count -gt 0
$hasRuntimeError = ($deadCodeExit -gt 1) -or ($complexityExit -ne 0)

$reportLines = @()
$reportLines += "Hygiene workflow report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src"
$reportLines += "dead_code_min_confidence: $MinConfidence"
$reportLines += "complexity_threshold: $ComplexityThreshold"
$reportLines += ""

$reportLines += "[dead_code_vulture]"
if ($hasDeadCodeFindings) {
    $reportLines += $deadCodeLines
}
else {
    $reportLines += "No dead-code findings."
}
$reportLines += ""

$reportLines += "[complexity_radon]"
if ($hasComplexityFindings) {
    $reportLines += $complexityLines
}
else {
    $reportLines += "No complexity findings at or above threshold."
}

if ($hasRuntimeError) {
    $reportLines += ""
    $reportLines += "[runtime_errors]"
    $reportLines += "vulture_exit_code=$deadCodeExit"
    $reportLines += "radon_exit_code=$complexityExit"
}

$outputPath = Join-Path $workspaceRoot $OutputFile
$reportLines | Set-Content -Path $outputPath -Encoding utf8

Write-Host "Hygiene report written to: $outputPath"

if ($hasRuntimeError) {
    exit 2
}

if ($Strict -and ($hasDeadCodeFindings -or $hasComplexityFindings)) {
    exit 1
}

exit 0
