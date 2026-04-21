param(
    [string[]]$Target = @(
        "08_writing/chapter1.md",
        "08_writing/chapter2.md",
        "08_writing/chapter3.md",
        "08_writing/chapter4.md",
        "08_writing/chapter5.md",
        "08_writing/chapter6.md"
    ),
    [string]$ReportPath = "reports/chapter_packaging_bundle_latest.md"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$repoRoot = Split-Path $implRoot -Parent
$wrapper = Join-Path $scriptDir "run_tool_with_venv_fallback.ps1"

if (-not (Test-Path $wrapper)) {
    throw "Wrapper script not found: $wrapper"
}

Set-Location $repoRoot

$results = @()
$hadFailure = $false

foreach ($target in $Target) {
    [string]$targetPath = $target
    $sourceExists = Test-Path $targetPath
    $chapterBase = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
    $outputPath = "reports/{0}_diagram_packaging_check.docx" -f $chapterBase

    if (-not $sourceExists) {
        $hadFailure = $true
        $results += [pscustomobject]@{
            Chapter      = $chapterBase
            Source       = $targetPath
            Output       = $outputPath
            Status       = "missing_source"
            SizeBytes    = "n/a"
            LastWriteUtc = "n/a"
        }
        continue
    }

    & $wrapper pandoc $targetPath "--resource-path=08_writing" "-o" $outputPath
    if ($LASTEXITCODE -ne 0) {
        $hadFailure = $true
        $results += [pscustomobject]@{
            Chapter      = $chapterBase
            Source       = $targetPath
            Output       = $outputPath
            Status       = "pandoc_failed"
            SizeBytes    = "n/a"
            LastWriteUtc = "n/a"
        }
        continue
    }

    $artifact = Get-Item $outputPath
    $results += [pscustomobject]@{
        Chapter      = $chapterBase
        Source       = $targetPath
        Output       = $outputPath
        Status       = "ok"
        SizeBytes    = [string]$artifact.Length
        LastWriteUtc = $artifact.LastWriteTimeUtc.ToString("yyyy-MM-dd HH:mm:ss")
    }
}

$timestampUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")

$reportLines = @()
$reportLines += "# Chapter Packaging Bundle Report"
$reportLines += ""
$reportLines += "Date (UTC): $timestampUtc"
$reportLines += ""
$reportLines += "## Scope"
$reportLines += "DOCX packaging checks generated via Pandoc for chapter files using:"
$reportLines += '- resource path: `08_writing`'
$reportLines += '- output location: `reports/`'
$reportLines += ""
$reportLines += "## Artifacts"
$reportLines += ""
$reportLines += "| Chapter | Source | Output | Status | Size (bytes) | LastWriteTime (UTC) |"
$reportLines += "|---|---|---|---|---:|---|"

foreach ($row in $results) {
    $reportLines += "| {0} | `{1}` | `{2}` | {3} | {4} | {5} |" -f $row.Chapter, $row.Source, $row.Output, $row.Status, $row.SizeBytes, $row.LastWriteUtc
}

$okCount = ($results | Where-Object { $_.Status -eq "ok" }).Count
$reportLines += ""
$reportLines += "## Result"
$reportLines += "Successful chapter outputs: $okCount / $($results.Count)"

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

Set-Content -Path $ReportPath -Value $reportLines -Encoding UTF8
Write-Host "Updated report: $ReportPath"

if ($hadFailure) {
    exit 1
}

exit 0
