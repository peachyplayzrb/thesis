param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("BASE", "ALT")]
    [string]$Profile,

    [switch]$RunIngestion,
    [switch]$ForceAuth,

    [string]$RunConfigPath = "07_implementation/implementation_notes/run_config/run_config_template_v1.json"
)

$ErrorActionPreference = "Stop"

# Load local profile credentials (must exist: spotify_env_profiles.local.ps1)
$localProfileFile = Join-Path $PSScriptRoot "spotify_env_profiles.local.ps1"
if (Test-Path $localProfileFile) {
    . $localProfileFile
} else {
    throw "Missing local profiles file: $localProfileFile`nCreate it by copying spotify_env_profiles_template.ps1 and filling in your credentials."
}

function Get-ScopedEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not $value) {
        $value = [Environment]::GetEnvironmentVariable($Name, "User")
    }
    if (-not $value) {
        $value = [Environment]::GetEnvironmentVariable($Name, "Machine")
    }
    return $value
}

function Require-ProfileVar {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Suffix
    )
    $name = "SPOTIFY_${Profile}_${Suffix}"
    $value = Get-ScopedEnvValue -Name $name
    if (-not $value) {
        throw "Missing required environment variable: $name"
    }
    return $value
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$env:SPOTIFY_CLIENT_ID = Require-ProfileVar -Suffix "CLIENT_ID"
$env:SPOTIFY_CLIENT_SECRET = Require-ProfileVar -Suffix "CLIENT_SECRET"
$env:SPOTIFY_REDIRECT_URI = Require-ProfileVar -Suffix "REDIRECT_URI"

Write-Host "[profile-test] active profile = $Profile"
Write-Host "[profile-test] redirect uri   = $($env:SPOTIFY_REDIRECT_URI)"

Set-Location $repoRoot

if ($RunIngestion) {
    Write-Host "[profile-test] running BL-002 ingestion"
    # Run as module from repo root to resolve relative imports
    $ingestArgs = @("-m", "07_implementation.implementation_notes.ingestion.export_spotify_max_dataset")
    if ($ForceAuth) {
        $ingestArgs += "--force-auth"
    }
    & $pythonExe @ingestArgs
    if ($LASTEXITCODE -ne 0) {
        throw "BL-002 ingestion failed with exit code $LASTEXITCODE"
    }
}

Write-Host "[profile-test] running BL-013 with refresh-seed"
& $pythonExe "07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py" --refresh-seed --run-config $RunConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "BL-013 failed with exit code $LASTEXITCODE"
}

Write-Host "[profile-test] running BL-014 sanity checks"
& $pythonExe "07_implementation/implementation_notes/quality/run_bl014_sanity_checks.py"
if ($LASTEXITCODE -ne 0) {
    throw "BL-014 failed with exit code $LASTEXITCODE"
}

Write-Host "[profile-test] running active freshness suite"
& $pythonExe "07_implementation/implementation_notes/quality/run_active_freshness_suite.py"
if ($LASTEXITCODE -ne 0) {
    throw "Active freshness suite failed with exit code $LASTEXITCODE"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$profileOutDir = Join-Path $repoRoot "07_implementation/implementation_notes/quality/outputs/profile_tests/${stamp}_${Profile.ToLower()}"
New-Item -ItemType Directory -Path $profileOutDir -Force | Out-Null

$copyTargets = @(
    "07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_export_run_summary.json",
    "07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json",
    "07_implementation/implementation_notes/alignment/outputs/bl003_ds001_spotify_summary.json",
    "07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json",
    "07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json",
    "07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json",
    "07_implementation/implementation_notes/quality/outputs/bl014_sanity_report.json",
    "07_implementation/implementation_notes/quality/outputs/bl010_bl011_freshness_report.json",
    "07_implementation/implementation_notes/quality/outputs/bl_active_freshness_suite_report.json"
)

foreach ($target in $copyTargets) {
    $sourcePath = Join-Path $repoRoot $target
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination (Join-Path $profileOutDir (Split-Path $target -Leaf)) -Force
    }
}

Write-Host "[profile-test] completed successfully"
Write-Host "[profile-test] evidence snapshot: $profileOutDir"