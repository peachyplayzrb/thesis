<#
.SYNOPSIS
    Multi-profile tuning sweep orchestration for comparison runs.

.DESCRIPTION
    Runs the full pipeline (BL-004 through BL-014) across multiple run_config profiles
    and generates a comparison matrix of key metrics.

    Historical use case: UI-013 tuning campaign to compare profile variants (v1, v1a, v1b, v1c).
    Current use case: Any multi-profile comparative analysis workflow.

.PARAMETER ProfileGlob
    Glob pattern for profile names to run. Default: all ui013 tuning profiles.
    Example: "run_config_ui013_tuning_*.json"

.PARAMETER OutputPath
    Where to write the results JSON. Default: reports/tuning_sweep_results.json

.PARAMETER NoValidate
    Skip BL-014 sanity checks (faster, less thorough).

.EXAMPLE
    # Run default tuning profiles
    .\tuning_sweep_orchestration.ps1

.EXAMPLE
    # Run custom profiles matching pattern
    .\tuning_sweep_orchestration.ps1 -ProfileGlob "run_config_bl021_probe_*.json" -OutputPath "reports/bl021_comparison.json"

.NOTES
    - Requires working Python environment in parent directory
    - Reads from 07_implementation/config/profiles/
    - Outputs comparison matrix to specified path
    - Each row includes: config name, exit codes, run IDs, key metrics, and BL-014 status
#>

param(
    [string]$ProfileGlob = "run_config_ui013_tuning_*.json",
    [string]$OutputPath = "reports/tuning_sweep_results.json",
    [switch]$NoValidate
)

Set-Location (Split-Path $PSScriptRoot -Parent)
$impl_root = (Get-Location).Path
$py = ".\scripts\run_tool_with_venv_fallback.ps1"

Write-Host "=== Tuning Sweep Orchestration ===" -ForegroundColor Cyan
Write-Host "Profile pattern: $ProfileGlob"
Write-Host "Implementation root: $impl_root"
Write-Host ""

# Find matching profiles
$profile_dir = "config/profiles"
$profiles = @(Get-ChildItem $profile_dir -Filter $ProfileGlob -File | Sort-Object Name | ForEach-Object { $_.FullName })

if ($profiles.Count -eq 0) {
    Write-Host "No profiles found matching: $ProfileGlob" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($profiles.Count) profile(s) to run:" -ForegroundColor Green
$profiles | ForEach-Object { Write-Host "  - $(Split-Path $_ -Leaf)" }
Write-Host ""

$rows = @()
$profileIndex = 0

foreach ($profile_path in $profiles) {
    $profileIndex++
    $profile_name = Split-Path $profile_path -Leaf

    Write-Host "[$profileIndex/$($profiles.Count)] Running: $profile_name" -ForegroundColor Cyan
    Write-Host "  > BL-013 pipeline..."

    # Run full pipeline
    & $py python main.py --run-config $profile_path 2>&1 | Out-Null
    $bl013_exit = $LASTEXITCODE

    if (-not $NoValidate) {
        Write-Host "  > BL-014 sanity checks..."
        & $py python -m pytest tests/test_quality.py -v 2>&1 | Out-Null
        $bl014_exit = $LASTEXITCODE
    }
    else {
        $bl014_exit = 0
    }

    # Try to read output artifacts (with fallbacks if structure differs)
    try {
        $try_paths = @(
            "src/bl003_alignment/outputs/bl003_ds001_spotify_summary.json",
            "src/bl005_retrieval/outputs/bl005_candidate_diagnostics.json",
            "src/bl006_scoring/outputs/bl006_score_summary.json",
            "src/bl008_transparency/outputs/bl008_explanation_summary.json",
            "src/bl013_orchestration/outputs/bl013_orchestration_run_latest.json"
        )

        $artifacts = @{}
        foreach ($path in $try_paths) {
            if (Test-Path $path) {
                $key = [System.IO.Path]::GetFileNameWithoutExtension($path).Substring(0, 5)
                $artifacts[$key] = Get-Content $path -Raw | ConvertFrom-Json
            }
        }

        # Extract metrics with safe fallbacks
        $bl003 = $artifacts["bl003"]
        $bl005 = $artifacts["bl005"]
        $bl006 = $artifacts["bl006"]
        $bl008 = $artifacts["bl008"]
        $bl013 = $artifacts["bl013"]

        $bl003_threshold = if ($bl003.counts.match_rate_validation) { [bool]$bl003.counts.match_rate_validation.threshold_enforced } else { "N/A" }
        $bl003_match_rate = if ($bl003.counts.match_rate_validation) { [double]$bl003.counts.match_rate_validation.actual_match_rate } else { 0.0 }
        $bl005_kept = if ($bl005.counts.kept_candidates) { [int]$bl005.counts.kept_candidates } else { 0 }

        $num_mean = if ($bl006.component_balance.all_candidates.numeric_contribution_mean) { [double]$bl006.component_balance.all_candidates.numeric_contribution_mean } else { 0.0 }
        $sem_mean = if ($bl006.component_balance.all_candidates.semantic_contribution_mean) { [double]$bl006.component_balance.all_candidates.semantic_contribution_mean } else { 0.0 }
        $gap = [math]::Round($num_mean - $sem_mean, 6)

        $max_dominance = 0.0
        if ($bl008.top_contributor_distribution) {
            foreach ($prop in $bl008.top_contributor_distribution.PSObject.Properties) {
                if ([int]$prop.Value -gt $max_dominance) { $max_dominance = [int]$prop.Value }
            }
        }
        $dominance_share = if ($bl008.playlist_track_count -gt 0) { [math]::Round($max_dominance / [double]$bl008.playlist_track_count, 4) } else { 0.0 }

        $rows += [pscustomobject]@{
            profile                  = $profile_name
            bl013_exit               = $bl013_exit
            bl014_exit               = $bl014_exit
            bl013_run_id             = if ($bl013.run_id) { [string]$bl013.run_id } else { "?" }
            bl003_threshold_enforced = $bl003_threshold
            bl003_match_rate         = $bl003_match_rate
            bl005_kept_candidates    = $bl005_kept
            bl006_numeric_mean       = $num_mean
            bl006_semantic_mean      = $sem_mean
            bl006_gap                = $gap
            bl008_dominance_share    = $dominance_share
        }

        Write-Host "  ✓ Metrics extracted" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Error reading artifacts: $_" -ForegroundColor Yellow
        $rows += [pscustomobject]@{
            profile = $profile_name
            error   = $_.Exception.Message
        }
    }

    Write-Host ""
}

# Write results
$output_dir = Split-Path $OutputPath -Parent
if ($output_dir -and -not (Test-Path $output_dir)) {
    mkdir $output_dir | Out-Null
}

$rows | ConvertTo-Json -Depth 4 | Set-Content $OutputPath -Encoding UTF8
Write-Host "Results written to: $OutputPath" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
$rows | Format-Table -AutoSize

Write-Host "Done!" -ForegroundColor Green
