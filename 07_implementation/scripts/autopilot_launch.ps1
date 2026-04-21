param(
    [ValidateSet("preflight", "ci-guard", "typecheck", "tests", "validate-only", "full-contract")]
    [string]$Mode = "full-contract",
    [switch]$SkipSetup,
    [switch]$SkipTypecheck,
    [string]$RunConfig,
    [switch]$NoReport
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$orchestratorPath = Join-Path $scriptDir "workflow_orchestrator.ps1"
if (-not (Test-Path $orchestratorPath)) {
    throw "Shared workflow orchestrator not found: $orchestratorPath"
}

$invokeParams = @{ Mode = $Mode }
if ($SkipSetup) { $invokeParams.SkipSetup = $true }
if ($SkipTypecheck) { $invokeParams.SkipTypecheck = $true }
if ($RunConfig) { $invokeParams.RunConfig = $RunConfig }
if (-not $NoReport) { $invokeParams.EmitAutopilotReport = $true }

& $orchestratorPath @invokeParams
exit $LASTEXITCODE
