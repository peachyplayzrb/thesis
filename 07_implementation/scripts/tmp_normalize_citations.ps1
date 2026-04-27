$root = 'c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\08_writing'
$files = @('chapter1.md', 'chapter2.md', 'chapter3.md', 'chapter4.md') | ForEach-Object { Join-Path $root $_ }

$mapYear = @{
    'Adomavicius and Tuzhilin|2005' = 'adomavicius_toward_2005'
    'Lu et al.|2015'                = 'lu_recommender_2015'
    'Bonnin and Jannach|2015'       = 'bonnin_automated_2015'
    'Schedl et al.|2018'            = 'schedl_current_2018'
    'Pegoraro Santana et al.|2020'  = 'pegoraro_santana_music4all_2020'
    'Roy and Dutta|2022'            = 'roy_systematic_2022'
    'Herlocker et al.|2004'         = 'herlocker_evaluating_2004'
    'Ferrari Dacrema et al.|2021'   = 'ferrari_dacrema_troubling_2021'
    'Bauer et al.|2024'             = 'bauer_exploring_2024'
    'Deldjoo et al.|2024'           = 'deldjoo_content-driven_2024'
    'Flexer and Grill|2016'         = 'flexer_problem_2016'
    'Zhang and Chen|2020'           = 'zhang_explainable_2020'
    'Cano and Morisio|2017'         = 'cano_hybrid_2017'
    'Fkih|2022'                     = 'fkih_similarity_2022'
    'Tintarev and Masthoff|2007'    = 'tintarev_survey_2007'
    'Tintarev and Masthoff|2012'    = 'tintarev_evaluating_2012'
    'Jin et al.|2020'               = 'jin_effects_2020'
    'Knijnenburg et al.|2012'       = 'knijnenburg_explaining_2012'
    'Afroogh et al.|2024'           = 'afroogh_trust_2024'
    'Beel et al.|2016'              = 'beel_towards_2016'
    'Anelli et al.|2021'            = 'anelli_elliot_2021'
    'Cavenaghi et al.|2023'         = 'cavenaghi_systematic_2023'
    'Bogdanov et al.|2013'          = 'bogdanov_semantic_2013'
    'Andjelkovic et al.|2019'       = 'andjelkovic_moodplay_2019'
    'Zamani et al.|2019'            = 'zamani_analysis_2019'
    'Ferraro et al.|2018'           = 'ferraro_automatic_2018'
    'Vall et al.|2019'              = 'vall_feature-combination_2019'
    'Schweiger et al.|2025'         = 'schweiger_impact_2025'
    'Ru et al.|2023'                = 'ru_improving_2023'
    'Bellogin and Said|2021'        = 'bellogin_improving_2021'
    'Zhu et al.|2022'               = 'zhu_bars_2022'
    'Sotirou et al.|2025'           = 'sotirou_musiclime_2025'
    'Nauta et al.|2023'             = 'nauta_anecdotal_2023'
    'He et al.|2017'                = 'he_neural_2017'
    'Peffers et al.|2007'           = 'peffers_design_2007'
    'Liu et al.|2025'               = 'liu_multimodal_2025'
    'Papadakis et al.|2021'         = 'papadakis_blocking_2021'
    'Elmagarmid et al.|2007'        = 'elmagarmid_duplicate_2007'
}

function Convert-Segment([string]$seg) {
    $s = $seg.Trim()
    if ($s -match '^(?<a>[^,]+?),\s*(?<y>\d{4}(?:\s*,\s*\d{4})*)$') {
        $author = $Matches.a.Trim()
        $years = $Matches.y -split '\s*,\s*'
        $keys = @()
        foreach ($year in $years) {
            $key = $mapYear["$author|$year"]
            if (-not $key) { return $null }
            $keys += "@$key"
        }
        return ($keys -join '; ')
    }
    return $null
}

foreach ($file in $files) {
    $script:changes = 0
    $text = Get-Content $file -Raw
    $unmatched = New-Object System.Collections.Generic.HashSet[string]
    $text = [regex]::Replace($text, '\((?<c>[^()]*\d{4}[^()]*)\)', {
            param($m)
            $content = $m.Groups['c'].Value
            if (-not ($content -match '[A-Za-z].*,\s*\d{4}')) { return $m.Value }
            $parts = $content -split ';'
            $out = @()
            foreach ($part in $parts) {
                $converted = Convert-Segment $part
                if (-not $converted) {
                    [void]$unmatched.Add($part.Trim())
                    return $m.Value
                }
                $out += $converted
            }
            $script:changes += 1
            return '[' + ($out -join '; ') + ']'
        })
    Set-Content -Path $file -Value $text -NoNewline
    Write-Output "FILE: $([System.IO.Path]::GetFileName($file)) CHANGES: $script:changes"
    if ($unmatched.Count -gt 0) {
        Write-Output 'UNMATCHED:'
        $unmatched | Sort-Object | ForEach-Object { " - $_" }
    }
}
