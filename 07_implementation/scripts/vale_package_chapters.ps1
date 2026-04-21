param(
    [ValidateSet('full', 'clarity', 'academic', 'strict', 'readability')]
    [string]$Mode = 'full',
    [string[]]$Target = @(
        '08_writing/chapter1.md',
        '08_writing/chapter2.md',
        '08_writing/chapter3.md',
        '08_writing/chapter4.md',
        '08_writing/chapter5.md',
        '08_writing/chapter6.md'
    ),
    [string]$ReportPath = 'reports/vale_chapter_bundle_latest.md'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir '..')
$repoRoot = Split-Path $implRoot -Parent
$valeReportScript = Join-Path $scriptDir 'vale_report.ps1'

if (-not (Test-Path -LiteralPath $valeReportScript)) {
    throw "Vale report script not found: $valeReportScript"
}

Set-Location $repoRoot

$results = @()
$hadFailure = $false

foreach ($target in $Target) {
    [string]$targetPath = $target
    $sourceExists = Test-Path -LiteralPath $targetPath
    $chapterBase = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
    $outputPath = "reports/vale_{0}_{1}_latest.txt" -f $chapterBase, $Mode

    if (-not $sourceExists) {
        $hadFailure = $true
        $results += [pscustomobject]@{
            Chapter      = $chapterBase
            Source       = $targetPath
            Output       = $outputPath
            Status       = 'missing_source'
            LastSummary  = 'n/a'
            LastWriteUtc = 'n/a'
        }
        continue
    }

    & $valeReportScript -Mode $Mode -Target $targetPath -OutputPath $outputPath
    if ($LASTEXITCODE -ne 0) {
        $hadFailure = $true
        $results += [pscustomobject]@{
            Chapter      = $chapterBase
            Source       = $targetPath
            Output       = $outputPath
            Status       = 'vale_failed'
            LastSummary  = 'n/a'
            LastWriteUtc = 'n/a'
        }
        continue
    }

    $artifact = Get-Item -LiteralPath $outputPath
    $lastSummary = ''
    $nonEmptyLines = @(Get-Content -LiteralPath $outputPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($nonEmptyLines.Count -gt 0) {
        $rawTail = [string]$nonEmptyLines[-1]
        $sanitizedTail = [regex]::Replace($rawTail, "`e\[[0-9;]*m", '')
        $sanitizedTail = $sanitizedTail.Trim()
        $match = [regex]::Match($sanitizedTail, '(\d+)\s+errors?,\s+(\d+)\s+warnings?\s+and\s+(\d+)\s+suggestions?')
        if ($match.Success) {
            $lastSummary = '{0} errors, {1} warnings, {2} suggestions' -f $match.Groups[1].Value, $match.Groups[2].Value, $match.Groups[3].Value
        }
        else {
            $lastSummary = $sanitizedTail
        }
    }

    $results += [pscustomobject]@{
        Chapter      = $chapterBase
        Source       = $targetPath
        Output       = $outputPath
        Status       = 'ok'
        LastSummary  = $lastSummary
        LastWriteUtc = $artifact.LastWriteTimeUtc.ToString('yyyy-MM-dd HH:mm:ss')
    }
}

$timestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss')

$reportLines = @()
$reportLines += '# Vale Chapter Bundle Report'
$reportLines += ''
$reportLines += "Date (UTC): $timestampUtc"
$reportLines += ''
$reportLines += '## Scope'
$reportLines += 'Per-chapter Vale runs generated via `vale_report.ps1` using:'
$reportLines += ('- mode: `{0}`' -f $Mode)
$reportLines += '- source set: chapter1.md through chapter6.md'
$reportLines += '- output location: `reports/`'
$reportLines += ''
$reportLines += '## Artifacts'
$reportLines += ''
$reportLines += '| Chapter | Source | Output | Status | Last Summary Line | LastWriteTime (UTC) |'
$reportLines += '|---|---|---|---|---|---|'

foreach ($row in $results) {
    $summaryEscaped = $row.LastSummary -replace '\|', '\\|'
    $reportLines += ('| {0} | `{1}` | `{2}` | {3} | {4} | {5} |' -f $row.Chapter, $row.Source, $row.Output, $row.Status, $summaryEscaped, $row.LastWriteUtc)
}

$okCount = ($results | Where-Object { $_.Status -eq 'ok' }).Count
$reportLines += ''
$reportLines += '## Result'
$reportLines += "Successful chapter reports: $okCount / $($results.Count)"

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

Set-Content -LiteralPath $ReportPath -Value $reportLines -Encoding UTF8
Write-Host "Updated report: $ReportPath"

if ($hadFailure) {
    exit 1
}

exit 0
