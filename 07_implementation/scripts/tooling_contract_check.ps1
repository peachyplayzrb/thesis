param(
    [switch]$SkipRuntime,
    [string]$OutputFile = "reports/tooling_contract_check_latest.md"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent
$reportsDir = Join-Path $workspaceRoot "reports"

if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
}

function New-CheckResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    return [PSCustomObject]@{
        Name    = $Name
        Passed  = $Passed
        Details = $Details
    }
}

function Test-DelegationContract {
    param(
        [string]$FilePath,
        [string[]]$RequiredSnippets,
        [string]$Label
    )

    if (-not (Test-Path $FilePath)) {
        return New-CheckResult -Name $Label -Passed $false -Details "File missing: $FilePath"
    }

    $content = Get-Content -Path $FilePath -Raw
    $missing = @()
    foreach ($snippet in $RequiredSnippets) {
        if ($content -notlike "*$snippet*") {
            $missing += $snippet
        }
    }

    if ($missing.Count -gt 0) {
        return New-CheckResult -Name $Label -Passed $false -Details ("Missing snippet(s): " + ($missing -join ", "))
    }

    return New-CheckResult -Name $Label -Passed $true -Details "Delegation contract present."
}

$checks = @()

$checks += Test-DelegationContract -FilePath (Join-Path $scriptDir "check_all.ps1") -RequiredSnippets @('workflow_orchestrator.ps1', 'Mode = "full-contract"') -Label "check_all delegates to workflow_orchestrator"
$checks += Test-DelegationContract -FilePath (Join-Path $scriptDir "autopilot_launch.ps1") -RequiredSnippets @("workflow_orchestrator.ps1", "EmitAutopilotReport") -Label "autopilot_launch delegates to workflow_orchestrator"

$qaShimContracts = @(
    @{ File = "ruff_src.ps1"; Snippets = @('qa_suite.ps1', '"ruff"'); Label = "ruff shim delegates to qa_suite" },
    @{ File = "test_coverage.ps1"; Snippets = @('qa_suite.ps1', '"coverage"'); Label = "coverage shim delegates to qa_suite" },
    @{ File = "docstring_coverage_src.ps1"; Snippets = @('qa_suite.ps1', '"docstring"'); Label = "docstring shim delegates to qa_suite" },
    @{ File = "dependency_audit.ps1"; Snippets = @('qa_suite.ps1', '"dependency-audit"'); Label = "dependency-audit shim delegates to qa_suite" },
    @{ File = "bandit_src.ps1"; Snippets = @('qa_suite.ps1', '"bandit"'); Label = "bandit shim delegates to qa_suite" },
    @{ File = "duplicate_src.ps1"; Snippets = @('qa_suite.ps1', '"duplicate"'); Label = "duplicate shim delegates to qa_suite" },
    @{ File = "hygiene_src.ps1"; Snippets = @('qa_suite.ps1', '"hygiene"'); Label = "hygiene shim delegates to qa_suite" }
)

foreach ($contract in $qaShimContracts) {
    $checks += Test-DelegationContract -FilePath (Join-Path $scriptDir $contract.File) -RequiredSnippets $contract.Snippets -Label $contract.Label
}

if (-not $SkipRuntime) {
    $ruffScript = Join-Path $scriptDir "ruff_src.ps1"
    & $ruffScript -NoPreview
    $ruffExitCode = $LASTEXITCODE
    $ruffRuntimePassed = ($ruffExitCode -eq 0) -or ($ruffExitCode -eq 1)
    $checks += New-CheckResult -Name "ruff shim runtime smoke" -Passed $ruffRuntimePassed -Details ("Exit code: $ruffExitCode (0=clean, 1=findings)")
}
else {
    $checks += New-CheckResult -Name "ruff shim runtime smoke" -Passed $true -Details "Skipped by -SkipRuntime."
}

$reportsFile = Join-Path $reportsDir "ruff_src_report_latest.txt"
$checks += New-CheckResult -Name "ruff report present in reports" -Passed (Test-Path $reportsFile) -Details $reportsFile

$legacyRootOutputs = @(
    (Join-Path $workspaceRoot "ruff_src_report_latest.txt"),
    (Join-Path $workspaceRoot "coverage_src_report_latest.txt"),
    (Join-Path $workspaceRoot "interrogate_src_report_latest.txt"),
    (Join-Path $workspaceRoot "pip_audit_report_latest.txt"),
    (Join-Path $workspaceRoot "bandit_src_report_latest.txt"),
    (Join-Path $workspaceRoot "duplicate_src_report_latest.txt"),
    (Join-Path $workspaceRoot "hygiene_src_report_latest.txt"),
    (Join-Path $implRoot "coverage.xml"),
    (Join-Path $implRoot "coverage_html")
)

$legacyPresent = @($legacyRootOutputs | Where-Object { Test-Path $_ })
$legacyDetails = if ($legacyPresent.Count -eq 0) {
    "No legacy outputs found outside reports."
}
else {
    "Found legacy outputs: " + ($legacyPresent -join "; ")
}
$checks += New-CheckResult -Name "legacy output paths absent" -Passed ($legacyPresent.Count -eq 0) -Details $legacyDetails

$outputPath = if ([System.IO.Path]::IsPathRooted($OutputFile)) {
    $OutputFile
}
else {
    Join-Path $workspaceRoot $OutputFile
}

$generatedAt = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$summaryLines = @()
$summaryLines += "# Tooling Contract Check"
$summaryLines += ""
$summaryLines += "- generated_at_utc: $generatedAt"
$summaryLines += "- runtime_mode: $(if ($SkipRuntime) { 'static-only' } else { 'static-plus-runtime' })"
$summaryLines += ""
$summaryLines += "## Results"
foreach ($check in $checks) {
    $status = if ($check.Passed) { "PASS" } else { "FAIL" }
    $summaryLines += "- [$status] $($check.Name): $($check.Details)"
}

$failedChecks = @($checks | Where-Object { -not $_.Passed })
$summaryLines += ""
$summaryLines += "## Summary"
$summaryLines += "- passed: $(@($checks | Where-Object { $_.Passed }).Count)"
$summaryLines += "- failed: $($failedChecks.Count)"

$summaryLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Tooling contract report written to: $outputPath"

if ($failedChecks.Count -gt 0) {
    foreach ($failed in $failedChecks) {
        Write-Host "FAIL: $($failed.Name) -> $($failed.Details)" -ForegroundColor Red
    }
    exit 1
}

Write-Host "PASS: Tooling contract checks passed." -ForegroundColor Green
exit 0
