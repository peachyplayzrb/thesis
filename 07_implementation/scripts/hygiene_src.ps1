param(
    [switch]$Strict,
    [string]$OutputFile = "reports/hygiene_src_report_latest.txt",
    [ValidateRange(1, 100)]
    [int]$MinConfidence = 70,
    [ValidateSet("A", "B", "C", "D", "E", "F")]
    [string]$ComplexityThreshold = "C"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

$invokeParams = @{
    Mode = "hygiene"
    MinConfidence = $MinConfidence
    ComplexityThreshold = $ComplexityThreshold
    OutputFile = $OutputFile
}
if ($Strict) { $invokeParams.Strict = $true }

& $qaSuitePath @invokeParams
exit $LASTEXITCODE
