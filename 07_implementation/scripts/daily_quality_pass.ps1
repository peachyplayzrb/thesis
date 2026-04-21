param(
    [switch]$IncludeSetup,
    [switch]$SkipPackaging,
    [switch]$SkipVale,
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent
$reportsDir = Join-Path $workspaceRoot "reports"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    Write-Host "STEP: $Name" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkGray

    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

function Get-JsonFieldOrDefault {
    param(
        [string]$Path,
        [string]$Field,
        [string]$DefaultValue = "n/a"
    )

    if (-not (Test-Path $Path)) {
        return $DefaultValue
    }

    $obj = Get-Content -Path $Path -Raw | ConvertFrom-Json
    $value = $obj.$Field
    if ($null -eq $value -or [string]::IsNullOrWhiteSpace([string]$value)) {
        return $DefaultValue
    }

    return [string]$value
}

if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
}

Push-Location $workspaceRoot
try {
    if (-not $SkipPackaging) {
        Invoke-Step -Name "Package chapters and refresh bundle report" -Action {
            & pwsh -NoProfile -ExecutionPolicy Bypass -File "07_implementation/scripts/pandoc_package_chapters.ps1"
        }
    }
    else {
        Write-Host "Skipping packaging (--SkipPackaging provided)." -ForegroundColor Yellow
    }

    if (-not $SkipVale) {
        Invoke-Step -Name "Run Vale chapter bundle and refresh report" -Action {
            & pwsh -NoProfile -ExecutionPolicy Bypass -File "07_implementation/scripts/vale_package_chapters.ps1" -Mode "full"
        }
    }
    else {
        Write-Host "Skipping Vale bundle (--SkipVale provided)." -ForegroundColor Yellow
    }

    if (-not $SkipValidation) {
        $checkArgs = @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "07_implementation/scripts/check_all.ps1"
        )

        if (-not $IncludeSetup) {
            $checkArgs += "-SkipSetup"
        }

        Invoke-Step -Name "Run implementation validation" -Action {
            & pwsh @checkArgs
        }
    }
    else {
        Write-Host "Skipping validation (--SkipValidation provided)." -ForegroundColor Yellow
    }

    $bl013Path = Join-Path $workspaceRoot "07_implementation/src/orchestration/outputs/bl013_orchestration_run_latest.json"
    $bl014Path = Join-Path $workspaceRoot "07_implementation/src/quality/outputs/bl014_sanity_report.json"
    $packagingReportPath = Join-Path $workspaceRoot "reports/chapter_packaging_bundle_latest.md"
    $valeReportPath = Join-Path $workspaceRoot "reports/vale_chapter_bundle_latest.md"
    $snapshotPath = Join-Path $workspaceRoot "reports/daily_quality_pass_latest.md"

    $bl013RunId = Get-JsonFieldOrDefault -Path $bl013Path -Field "run_id"
    $bl013Status = Get-JsonFieldOrDefault -Path $bl013Path -Field "overall_status"
    $bl014RunId = Get-JsonFieldOrDefault -Path $bl014Path -Field "run_id"
    $bl014Status = Get-JsonFieldOrDefault -Path $bl014Path -Field "overall_status"
    $bl014ChecksPassed = Get-JsonFieldOrDefault -Path $bl014Path -Field "checks_passed"
    $bl014ChecksTotal = Get-JsonFieldOrDefault -Path $bl014Path -Field "checks_total"

    $packagingReportMtime = if (Test-Path $packagingReportPath) { (Get-Item $packagingReportPath).LastWriteTimeUtc.ToString("yyyy-MM-dd HH:mm:ss 'UTC'") } else { "n/a" }
    $valeReportMtime = if (Test-Path $valeReportPath) { (Get-Item $valeReportPath).LastWriteTimeUtc.ToString("yyyy-MM-dd HH:mm:ss 'UTC'") } else { "n/a" }

    $lines = @(
        "# Daily Quality Pass Snapshot",
        "",
        "- Generated UTC: $([DateTime]::UtcNow.ToString('yyyy-MM-dd HH:mm:ss'))",
        "- Include setup during validation: $IncludeSetup",
        "- Packaging run skipped: $SkipPackaging",
        "- Vale run skipped: $SkipVale",
        "- Validation run skipped: $SkipValidation",
        "",
        "## Latest Runtime Status",
        "",
        "- BL-013 run_id: $bl013RunId",
        "- BL-013 overall_status: $bl013Status",
        "- BL-014 run_id: $bl014RunId",
        "- BL-014 overall_status: $bl014Status",
        "- BL-014 checks: $bl014ChecksPassed / $bl014ChecksTotal",
        "",
        "## Bundle Report Freshness",
        "",
        "- reports/chapter_packaging_bundle_latest.md: $packagingReportMtime",
        "- reports/vale_chapter_bundle_latest.md: $valeReportMtime"
    )

    Set-Content -Path $snapshotPath -Value $lines -Encoding UTF8
    Write-Host ""
    Write-Host "PASS: Daily quality pass completed." -ForegroundColor Green
    Write-Host "Snapshot written: reports/daily_quality_pass_latest.md" -ForegroundColor Green
}
finally {
    Pop-Location
}
