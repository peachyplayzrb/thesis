# Build Final Thesis Package (Merged Markdown -> Final DOCX with Cover)
#
# Steps:
# 1. Concatenate chapters 1-6 into thesis_master_draft_merged.md
# 2. Convert merged markdown to DOCX with Pandoc (bibliography + citeproc)
# 3. Combine cover page + body into final output DOCX

param(
    [string]$RepoRoot = ($PSScriptRoot -replace '\\07_implementation\\scripts$', ''),
    [string]$OutputName = 'final_project_report_with_cover.docx'
)

$ErrorActionPreference = 'Stop'

# Resolve paths
$repo = (Resolve-Path $RepoRoot).Path
$writingDir = Join-Path $repo '08_writing'
$reportsDir = Join-Path $repo 'reports'
$mergedFile = Join-Path $writingDir 'thesis_master_draft_merged.md'
$coverPage = Join-Path $writingDir 'Project Cover Page.docx'
$bibliography = Join-Path $writingDir 'references.bib'
$tempBody = Join-Path $reportsDir '_thesis_body_temp.docx'
$finalOutput = Join-Path $reportsDir $OutputName

# Verify input files exist
@($coverPage, $bibliography) | ForEach-Object {
    if (!(Test-Path $_)) {
        throw "Required file not found: $_"
    }
}

Write-Host "Repository root: $repo" -ForegroundColor Cyan
Write-Host "Output directory: $reportsDir" -ForegroundColor Cyan

# Step 1: Merge chapters into thesis_master_draft_merged.md
Write-Host "`n[1/4] Concatenating chapters 1-6 into merged file..." -ForegroundColor Yellow
$chapters = @(
    '08_writing/chapter1.md',
    '08_writing/chapter2.md',
    '08_writing/chapter3.md',
    '08_writing/chapter4.md',
    '08_writing/chapter5.md',
    '08_writing/chapter6.md'
) | ForEach-Object { Join-Path $repo $_ }

# Verify all chapter files exist
$chapters | ForEach-Object {
    if (!(Test-Path $_)) {
        throw "Missing chapter file: $_"
    }
}

# Concatenate with proper encoding and line endings
$parts = @()
foreach ($chapterPath in $chapters) {
    $content = Get-Content $chapterPath -Raw
    $parts += $content.TrimEnd()
}
$merged = $parts -join "`r`n`r`n"

# Write with UTF8 no BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path $mergedFile), $merged, $utf8NoBom)

# Verify merge
$written = Get-Content $mergedFile -Raw
$normMerged = ($merged -replace "`r`n", "`n").TrimEnd()
$normWritten = ($written -replace "`r`n", "`n").TrimEnd()
if ($normWritten -ne $normMerged) {
    throw "Merged file verification failed"
}

Write-Host "  ✓ Merged file updated: $mergedFile" -ForegroundColor Green
$chapterCount = Select-String -Path $mergedFile -Pattern '^\s*# Chapter ' | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "  ✓ Contains $chapterCount chapters" -ForegroundColor Green

# Step 2: Convert merged markdown to DOCX with Pandoc
Write-Host "`n[2/4] Converting merged markdown to DOCX..." -ForegroundColor Yellow
$pandocCmd = @(
    $mergedFile,
    '--from', 'gfm',
    '--resource-path', $writingDir,
    '--bibliography', $bibliography,
    '--citeproc',
    '-o', $tempBody
)

& pandoc @pandocCmd 2>&1 | ForEach-Object {
    Write-Host "  $($_.ToString())" -ForegroundColor Gray
}

if (!(Test-Path $tempBody)) {
    throw "Pandoc conversion failed: $tempBody not created"
}

$bodySize = (Get-Item $tempBody).Length
Write-Host "  ✓ Body DOCX created: $('{0:N0}' -f $bodySize) bytes" -ForegroundColor Green

# Step 3: Combine cover + body into final DOCX
Write-Host "`n[3/4] Combining cover page with body..." -ForegroundColor Yellow

# Clean up any temp lock files
$lockFile = Join-Path $reportsDir "~`$nal_project_report_with_cover.docx"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}

$combineCmd = @(
    $coverPage,
    $tempBody,
    '-o', $finalOutput
)

& pandoc @combineCmd 2>&1 | ForEach-Object {
    Write-Host "  $($_.ToString())" -ForegroundColor Gray
}

if (!(Test-Path $finalOutput)) {
    throw "Pandoc combine failed: $finalOutput not created"
}

$finalSize = (Get-Item $finalOutput).Length
$timestamp = (Get-Item $finalOutput).LastWriteTimeUtc.ToString('yyyy-MM-dd HH:mm:ss UTC')
Write-Host "  ✓ Final DOCX created: $('{0:N0}' -f $finalSize) bytes" -ForegroundColor Green
Write-Host "  ✓ Timestamp: $timestamp" -ForegroundColor Green

# Step 4: Cleanup and report
Write-Host "`n[4/4] Cleanup and final report..." -ForegroundColor Yellow
if (Test-Path $tempBody) {
    Remove-Item $tempBody -Force
    Write-Host "  ✓ Temporary body file removed" -ForegroundColor Green
}

Write-Host "`n" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FINAL THESIS PACKAGE BUILD COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Merged chapters:     $mergedFile" -ForegroundColor White
Write-Host "Final DOCX output:   $finalOutput" -ForegroundColor Yellow
Write-Host "File size:           $('{0:N0}' -f $finalSize) bytes" -ForegroundColor White
Write-Host "Generated:           $timestamp" -ForegroundColor White
Write-Host "`nReady for submission workflows." -ForegroundColor Green
