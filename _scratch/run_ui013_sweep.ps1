Set-Location "c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main"
$py = "c:/Users/peach/Desktop/thesis-main (3)/thesis-main/thesis-main/.venv/Scripts/python.exe"
$configs = @(
  "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1.json",
  "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1a.json",
  "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1b.json",
  "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1c.json"
)

$rows = @()
foreach ($cfg in $configs) {
  Write-Host "=== RUNNING $cfg ==="
  & $py "07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py" --run-config $cfg --refresh-seed | Out-Null
  $bl013Exit = $LASTEXITCODE

  & $py "07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py" | Out-Null
  $bl014Exit = $LASTEXITCODE

  $bl003 = Get-Content "07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json" -Raw | ConvertFrom-Json
  $bl005 = Get-Content "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json" -Raw | ConvertFrom-Json
  $bl006 = Get-Content "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json" -Raw | ConvertFrom-Json
  $bl008 = Get-Content "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json" -Raw | ConvertFrom-Json
  $bl013 = Get-Content "07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json" -Raw | ConvertFrom-Json
  $bl014 = Get-Content "07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json" -Raw | ConvertFrom-Json

  $maxCount = 0
  foreach ($p in $bl008.top_contributor_distribution.PSObject.Properties) {
    if ([int]$p.Value -gt $maxCount) { $maxCount = [int]$p.Value }
  }
  $dominanceShare = if ([int]$bl008.playlist_track_count -gt 0) {
    [math]::Round($maxCount / [double]$bl008.playlist_track_count, 4)
  } else {
    0.0
  }

  $numMean = [double]$bl006.component_balance.all_candidates.numeric_contribution_mean
  $semMean = [double]$bl006.component_balance.all_candidates.semantic_contribution_mean

  $rows += [pscustomobject]@{
    config = [System.IO.Path]::GetFileName($cfg)
    bl013_exit = $bl013Exit
    bl014_exit = $bl014Exit
    bl013_run_id = [string]$bl013.run_id
    bl014_run_id = [string]$bl014.run_id
    bl003_threshold_enforced = [bool]$bl003.counts.match_rate_validation.threshold_enforced
    bl003_match_rate = [double]$bl003.counts.match_rate_validation.actual_match_rate
    bl005_kept_candidates = [int]$bl005.counts.kept_candidates
    bl006_numeric_mean = $numMean
    bl006_semantic_mean = $semMean
    bl006_gap_numeric_minus_semantic = [math]::Round($numMean - $semMean, 6)
    bl008_top_label_dominance_share = $dominanceShare
    bl014_overall_status = [string]$bl014.overall_status
  }
}

$rows | ConvertTo-Json -Depth 4 | Set-Content "_scratch/ui013_tuning_sweep_results.json" -Encoding UTF8
$rows | Format-Table -AutoSize
