param(
    [switch]$Fix,
    [switch]$NoPreview,
    [string]$OutputFile = "reports/ruff_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

$invokeParams = @{
    Mode       = "ruff"
    OutputFile = $OutputFile
}
if ($Fix) { $invokeParams.Fix = $true }
if ($NoPreview) { $invokeParams.NoPreview = $true }

& $qaSuitePath @invokeParams
exit $LASTEXITCODE
