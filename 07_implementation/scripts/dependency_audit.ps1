param(
    [switch]$Strict,
    [string]$OutputFile = "reports/pip_audit_report_latest.txt",
    [string[]]$IgnoredVulnerabilityIds = @("PYSEC-2022-42969")
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaSuitePath = Join-Path $scriptDir "qa_suite.ps1"
if (-not (Test-Path $qaSuitePath)) {
    throw "QA suite script not found: $qaSuitePath"
}

$invokeParams = @{
    Mode                    = "dependency-audit"
    OutputFile              = $OutputFile
    IgnoredVulnerabilityIds = $IgnoredVulnerabilityIds
}
if ($Strict) { $invokeParams.Strict = $true }

& $qaSuitePath @invokeParams
exit $LASTEXITCODE
