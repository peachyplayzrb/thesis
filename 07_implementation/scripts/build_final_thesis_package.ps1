# Build Final Thesis Package (Merged Markdown -> Final DOCX with Cover)
#
# Steps:
# 1. Concatenate chapters 1-6 into thesis_master_draft_merged.md
# 2. Convert merged markdown to DOCX with Pandoc (bibliography + citeproc)
# 3. Combine cover page + body into final output DOCX

param(
    [string]$RepoRoot = ($PSScriptRoot -replace '\\07_implementation\\scripts$', ''),
    [string]$OutputName = 'final_project_report_with_cover.docx',
    [string]$CitationStylePath = '',
    [switch]$DisableWordComMerge,
    [int]$DefaultImageDpi = 300
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
$tempRenderedMd = Join-Path $reportsDir '_thesis_body_rendered_temp.md'
$finalOutput = Join-Path $reportsDir $OutputName

function Merge-DocxWithWordCom {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CoverPath,
        [Parameter(Mandatory = $true)]
        [string]$BodyPath,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $word = $null
    $coverDocument = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.DisplayAlerts = 0

        $coverDocument = $word.Documents.Open($CoverPath, $false, $true, $false)

        $wdCollapseEnd = 0
        $wdSectionBreakNextPage = 2

        $range = $coverDocument.Content
        $range.Collapse($wdCollapseEnd)
        $range.InsertBreak($wdSectionBreakNextPage)
        $range.Collapse($wdCollapseEnd)
        $range.InsertFile($BodyPath)

        $coverDocument.SaveAs2($OutputPath)
    }
    finally {
        if ($coverDocument -ne $null) {
            try {
                $coverDocument.Close($false)
            }
            catch {
                # Ignore shutdown cleanup errors.
            }
        }
        if ($word -ne $null) {
            try {
                $word.Quit()
            }
            catch {
                # Ignore shutdown cleanup errors.
            }
        }
    }
}

function Set-DocxImageQualityFlags {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DocxPath,
        [Parameter(Mandatory = $true)]
        [int]$ImageDpi
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $tempExtractDir = Join-Path $reportsDir ('_docx_quality_' + [guid]::NewGuid().ToString('N'))
    $tempDocx = Join-Path $reportsDir ('_docx_quality_' + [guid]::NewGuid().ToString('N') + '.docx')

    try {
        [System.IO.Compression.ZipFile]::ExtractToDirectory($DocxPath, $tempExtractDir)
        $settingsPath = Join-Path $tempExtractDir 'word/settings.xml'
        if (-not (Test-Path $settingsPath)) {
            throw "DOCX settings.xml not found while applying image quality flags: $settingsPath"
        }

        $xml = New-Object System.Xml.XmlDocument
        $xml.PreserveWhitespace = $true
        $xml.Load($settingsPath)

        $wNamespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace('w', $wNamespace)

        $settingsNode = $xml.SelectSingleNode('/w:settings', $ns)
        if ($null -eq $settingsNode) {
            throw 'DOCX settings root node was not found while applying image quality flags.'
        }

        $doNotCompressNode = $xml.SelectSingleNode('/w:settings/w:doNotCompressPictures', $ns)
        if ($null -eq $doNotCompressNode) {
            $doNotCompressNode = $xml.CreateElement('w', 'doNotCompressPictures', $wNamespace)
            $null = $settingsNode.AppendChild($doNotCompressNode)
        }

        $defaultDpiNode = $xml.SelectSingleNode('/w:settings/w:defaultImageDpi', $ns)
        if ($null -eq $defaultDpiNode) {
            $defaultDpiNode = $xml.CreateElement('w', 'defaultImageDpi', $wNamespace)
            $null = $settingsNode.AppendChild($defaultDpiNode)
        }
        $defaultDpiAttr = $xml.CreateAttribute('w', 'val', $wNamespace)
        $defaultDpiAttr.Value = [string]$ImageDpi
        if ($defaultDpiNode.Attributes.GetNamedItem('w:val') -ne $null) {
            $null = $defaultDpiNode.Attributes.RemoveNamedItem('w:val')
        }
        $null = $defaultDpiNode.Attributes.Append($defaultDpiAttr)

        $xml.Save($settingsPath)

        if (Test-Path $tempDocx) {
            Remove-Item $tempDocx -Force
        }
        [System.IO.Compression.ZipFile]::CreateFromDirectory($tempExtractDir, $tempDocx)
        Move-Item -Path $tempDocx -Destination $DocxPath -Force
    }
    finally {
        if (Test-Path $tempExtractDir) {
            Remove-Item $tempExtractDir -Recurse -Force
        }
        if (Test-Path $tempDocx) {
            Remove-Item $tempDocx -Force
        }
    }
}

# Verify input files exist
@($coverPage, $bibliography) | ForEach-Object {
    if (!(Test-Path $_)) {
        throw "Required file not found: $_"
    }
}

# Resolve an optional CSL file for explicit citation style control.
$resolvedCitationStyle = $null
if (-not [string]::IsNullOrWhiteSpace($CitationStylePath)) {
    $candidate = Join-Path $repo $CitationStylePath
    if (Test-Path $candidate) {
        $resolvedCitationStyle = (Resolve-Path $candidate).Path
    }
    elseif (Test-Path $CitationStylePath) {
        $resolvedCitationStyle = (Resolve-Path $CitationStylePath).Path
    }
    else {
        throw "Citation style file not found: $CitationStylePath"
    }
}
else {
    $defaultCslCandidates = @(
        (Join-Path $writingDir 'harvard-cite-them-right.csl'),
        (Join-Path $writingDir 'citation_style.csl'),
        (Join-Path $writingDir 'references.csl')
    )
    foreach ($candidate in $defaultCslCandidates) {
        if (Test-Path $candidate) {
            $resolvedCitationStyle = (Resolve-Path $candidate).Path
            break
        }
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
$pandocInputFormat = 'markdown+yaml_metadata_block+citations'
$pandocCmd = @(
    $mergedFile,
    '--from', $pandocInputFormat,
    '--resource-path', $writingDir,
    '--bibliography', $bibliography,
    '--citeproc',
    '-o', $tempBody
)

if ($resolvedCitationStyle) {
    Write-Host "  ✓ Citation style: $resolvedCitationStyle" -ForegroundColor Green
    $pandocCmd += @('--csl', $resolvedCitationStyle)
}
else {
    Write-Host "  ! No CSL style file found, using Pandoc default citation style" -ForegroundColor Yellow
}

& pandoc @pandocCmd 2>&1 | ForEach-Object {
    Write-Host "  $($_.ToString())" -ForegroundColor Gray
}

if (!(Test-Path $tempBody)) {
    throw "Pandoc conversion failed: $tempBody not created"
}

$bodySize = (Get-Item $tempBody).Length
Write-Host "  ✓ Body DOCX created: $('{0:N0}' -f $bodySize) bytes" -ForegroundColor Green

# Verify citations were rendered and no raw [@key] tokens remain.
Write-Host "`n[2b/4] Verifying citation rendering..." -ForegroundColor Yellow
$citationCheckCmd = @(
    $mergedFile,
    '--from', $pandocInputFormat,
    '--to', 'markdown',
    '--resource-path', $writingDir,
    '--bibliography', $bibliography,
    '--citeproc',
    '-o', $tempRenderedMd
)
if ($resolvedCitationStyle) {
    $citationCheckCmd += @('--csl', $resolvedCitationStyle)
}

& pandoc @citationCheckCmd
if (!(Test-Path $tempRenderedMd)) {
    throw "Citation check failed: rendered markdown was not created"
}

$renderedMd = Get-Content $tempRenderedMd -Raw
$unresolvedMatches = [regex]::Matches($renderedMd, '\[@[^\]]+\]')
if ($unresolvedMatches.Count -gt 0) {
    $sample = $unresolvedMatches | Select-Object -First 5 | ForEach-Object { $_.Value }
    throw "Unresolved citation keys detected after citeproc: $($sample -join ', ')"
}
Write-Host "  ✓ Citation rendering verified (no unresolved citation keys)" -ForegroundColor Green

# Step 3: Combine cover + body into final DOCX
Write-Host "`n[3/4] Combining cover page with body..." -ForegroundColor Yellow

# Clean up any temp lock files
$lockFile = Join-Path $reportsDir "~`$nal_project_report_with_cover.docx"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}

if (-not $DisableWordComMerge) {
    try {
        Merge-DocxWithWordCom -CoverPath $coverPage -BodyPath $tempBody -OutputPath $finalOutput
        Write-Host "  ✓ Combined with Word COM merge (cover assets preserved)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ! Word COM merge failed, falling back to Pandoc combine: $($_.Exception.Message)" -ForegroundColor Yellow
        $combineCmd = @(
            $coverPage,
            $tempBody,
            '-o', $finalOutput
        )

        & pandoc @combineCmd 2>&1 | ForEach-Object {
            Write-Host "  $($_.ToString())" -ForegroundColor Gray
        }
    }
}
else {
    $combineCmd = @(
        $coverPage,
        $tempBody,
        '-o', $finalOutput
    )

    & pandoc @combineCmd 2>&1 | ForEach-Object {
        Write-Host "  $($_.ToString())" -ForegroundColor Gray
    }
}

if (!(Test-Path $finalOutput)) {
    throw "Pandoc combine failed: $finalOutput not created"
}

Set-DocxImageQualityFlags -DocxPath $finalOutput -ImageDpi $DefaultImageDpi
Write-Host "  ✓ Applied DOCX image-quality flags (no compression, default DPI=$DefaultImageDpi)" -ForegroundColor Green

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
if (Test-Path $tempRenderedMd) {
    Remove-Item $tempRenderedMd -Force
    Write-Host "  ✓ Temporary citation-check file removed" -ForegroundColor Green
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
