param(
    [switch]$Strict,
    [string]$OutputFile = "reports/bandit_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

$invokeParams = @{
    Mode       = "bandit"
    OutputFile = $OutputFile
}
if ($Strict) { $invokeParams.Strict = $true }

& $qaSuitePath @invokeParams
exit $LASTEXITCODE
