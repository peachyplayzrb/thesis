param(
    [switch]$Strict,
    [ValidateRange(3, 200)]
    [int]$MinSimilarityLines = 8,
    [string]$OutputFile = "reports/duplicate_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

$invokeParams = @{
    Mode = "duplicate"
    MinSimilarityLines = $MinSimilarityLines
    OutputFile = $OutputFile
}
if ($Strict) { $invokeParams.Strict = $true }

& $qaSuitePath @invokeParams
exit $LASTEXITCODE
