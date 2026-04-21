param(
    [switch]$SkipSetup,
    [switch]$SkipTypecheck
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$orchestratorPath = Join-Path $scriptDir "workflow_orchestrator.ps1"
if (-not (Test-Path $orchestratorPath)) {
    throw "Shared workflow orchestrator not found: $orchestratorPath"
}

$invokeParams = @{ Mode = "full-contract" }
if ($SkipSetup) { $invokeParams.SkipSetup = $true }
if ($SkipTypecheck) { $invokeParams.SkipTypecheck = $true }

& $orchestratorPath @invokeParams
exit $LASTEXITCODE
