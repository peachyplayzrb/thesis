param(
    [ValidateRange(0, 100)]
    [int]$FailUnder = 65,
    [string]$OutputFile = "reports/coverage_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

& $qaSuitePath -Mode "coverage" -FailUnder $FailUnder -OutputFile $OutputFile
exit $LASTEXITCODE
