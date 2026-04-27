param(
    [string]$RepoRoot = ($PSScriptRoot -replace '\\07_implementation\\scripts$', ''),
    [string]$InputDocx = 'reports/final_project_report_with_cover.docx',
    [string]$OutputPdf = 'reports/final_project_report_with_cover_word_ui.pdf',
    [string]$OutputHtml = 'reports/final_project_report_with_cover_word_ui_filtered.html',
    [string]$ParagraphAuditCsv = 'reports/word_ui_render_paragraph_audit_latest.csv',
    [string]$ReportPath = 'reports/word_ui_render_check_latest.md'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RepoPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Base,
        [Parameter(Mandatory = $true)]
        [string]$PathValue
    )

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $Base $PathValue))
}

function Ensure-ParentDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )

    $parent = Split-Path -Parent $FilePath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
}

function Clean-ParagraphText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $clean = $Value -replace "`r", '' -replace "`a", ''
    return $clean.Trim()
}

$repo = (Resolve-Path $RepoRoot).Path
$docxPath = Resolve-RepoPath -Base $repo -PathValue $InputDocx
$pdfPath = Resolve-RepoPath -Base $repo -PathValue $OutputPdf
$htmlPath = Resolve-RepoPath -Base $repo -PathValue $OutputHtml
$auditCsvPath = Resolve-RepoPath -Base $repo -PathValue $ParagraphAuditCsv
$reportAbsPath = Resolve-RepoPath -Base $repo -PathValue $ReportPath

if (-not (Test-Path -LiteralPath $docxPath)) {
    throw "Input DOCX not found: $docxPath"
}

Ensure-ParentDirectory -FilePath $pdfPath
Ensure-ParentDirectory -FilePath $htmlPath
Ensure-ParentDirectory -FilePath $auditCsvPath
Ensure-ParentDirectory -FilePath $reportAbsPath

$word = $null
$document = $null
$timestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss')

$rows = @()
$literalMarkdownHeadingCount = 0
$blankO1ThresholdLineCount = 0
$blankO5ReplayLineCount = 0
$blankO5AcceptanceLineCount = 0
$figureCaptionCounts = @{}
$criticalIssues = @()
$notes = @()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $readOnly = $true
    $isVisible = $false
    $document = $word.Documents.Open($docxPath, $false, $readOnly, $false, '', '', $isVisible)

    $wdExportFormatPDF = 17
    $wdFormatFilteredHTML = 10

    $document.ExportAsFixedFormat($pdfPath, $wdExportFormatPDF)
    $document.SaveAs([ref]$htmlPath, [ref]$wdFormatFilteredHTML)

    $paragraphIndex = 0
    foreach ($paragraph in $document.Paragraphs) {
        $paragraphIndex += 1

        $rawText = [string]$paragraph.Range.Text
        $text = Clean-ParagraphText -Value $rawText
        if ([string]::IsNullOrWhiteSpace($text)) {
            continue
        }

        $styleName = ''
        try {
            $styleName = [string]$paragraph.Range.Style.NameLocal
        }
        catch {
            try {
                $styleName = [string]$paragraph.Range.Style
            }
            catch {
                $styleName = 'unknown'
            }
        }

        $listType = 0
        $listString = ''
        try {
            $listType = [int]$paragraph.Range.ListFormat.ListType
            $listString = [string]$paragraph.Range.ListFormat.ListString
        }
        catch {
            $listType = 0
            $listString = ''
        }

        $outlineLevel = 0
        try {
            $outlineLevel = [int]$paragraph.OutlineLevel
        }
        catch {
            $outlineLevel = 0
        }

        if ($text -match '^\s*#{1,6}\s+') {
            $literalMarkdownHeadingCount += 1
        }
        if ($text -match '^O1 missingness threshold\s*\.$') {
            $blankO1ThresholdLineCount += 1
        }
        if ($text -match '^O5 reproducibility replay count\s+fixed-config replays\.$') {
            $blankO5ReplayLineCount += 1
        }
        if ($text -match '^BL-010 reports deterministic replay consistency for\s+replays') {
            $blankO5AcceptanceLineCount += 1
        }

        if ($text -match '^Figure\s+\d+\.\d+\.') {
            if (-not $figureCaptionCounts.ContainsKey($text)) {
                $figureCaptionCounts[$text] = 0
            }
            $figureCaptionCounts[$text] += 1
        }

        $rows += [pscustomobject]@{
            ParagraphIndex = $paragraphIndex
            Style          = $styleName
            OutlineLevel   = $outlineLevel
            ListType       = $listType
            ListString     = $listString
            Text           = $text
        }
    }

    $duplicateCaptions = @($figureCaptionCounts.GetEnumerator() | Where-Object { $_.Value -gt 1 } | Sort-Object Name)

    if ($literalMarkdownHeadingCount -gt 0) {
        $criticalIssues += "Literal markdown heading markers detected in rendered DOCX paragraphs: $literalMarkdownHeadingCount"
    }
    if ($blankO1ThresholdLineCount -gt 0) {
        $criticalIssues += "Blank O1 threshold phrasing detected: $blankO1ThresholdLineCount"
    }
    if ($blankO5ReplayLineCount -gt 0) {
        $criticalIssues += "Blank O5 replay-count phrasing detected: $blankO5ReplayLineCount"
    }
    if ($blankO5AcceptanceLineCount -gt 0) {
        $criticalIssues += "Blank BL-010 replay-acceptance phrasing detected: $blankO5AcceptanceLineCount"
    }
    if ($duplicateCaptions.Count -gt 0) {
        $criticalIssues += "Duplicate figure captions detected: $($duplicateCaptions.Count)"
    }

    $rows | Export-Csv -LiteralPath $auditCsvPath -NoTypeInformation -Encoding UTF8

    if (-not (Test-Path -LiteralPath $pdfPath)) {
        $criticalIssues += 'PDF export was not created by Word rendering pass.'
    }
    if (-not (Test-Path -LiteralPath $htmlPath)) {
        $criticalIssues += 'Filtered HTML export was not created by Word rendering pass.'
    }

    $listSample = @($rows | Where-Object { $_.ListType -ne 0 } | Select-Object -First 12)

    $report = @()
    $report += '# Word UI Render Check Report'
    $report += ''
    $report += "Date (UTC): $timestampUtc"
    $report += ''
    $report += '## Inputs'
    $report += "- DOCX: $docxPath"
    $report += "- PDF export: $pdfPath"
    $report += "- Filtered HTML export: $htmlPath"
    $report += "- Paragraph audit CSV: $auditCsvPath"
    $report += ''
    $report += '## Critical Checks'
    if ($criticalIssues.Count -eq 0) {
        $report += '- PASS: No critical rendering defects detected in this audit pass.'
    }
    else {
        foreach ($issue in $criticalIssues) {
            $report += "- FAIL: $issue"
        }
    }

    $report += ''
    $report += '## Diagnostic Counts'
    $report += "- Literal markdown heading markers: $literalMarkdownHeadingCount"
    $report += "- Blank O1 threshold lines: $blankO1ThresholdLineCount"
    $report += "- Blank O5 replay lines: $blankO5ReplayLineCount"
    $report += "- Blank O5 acceptance lines: $blankO5AcceptanceLineCount"
    $report += "- Duplicate figure-caption entries: $(@($figureCaptionCounts.GetEnumerator() | Where-Object { $_.Value -gt 1 }).Count)"

    $report += ''
    $report += '## Numbered List Sample (Word Paragraph/List Metadata)'
    if ($listSample.Count -eq 0) {
        $report += '- No numbered-list paragraphs found in sample window.'
    }
    else {
        $report += ''
        $report += '| ParagraphIndex | Style | ListType | ListString | Text |'
        $report += '|---|---|---:|---|---|'
        foreach ($row in $listSample) {
            $safeText = ([string]$row.Text).Replace('|', '\|')
            $safeStyle = ([string]$row.Style).Replace('|', '\|')
            $safeListString = ([string]$row.ListString).Replace('|', '\|')
            $report += "| $($row.ParagraphIndex) | $safeStyle | $($row.ListType) | $safeListString | $safeText |"
        }
    }

    if ($figureCaptionCounts.Count -gt 0) {
        $report += ''
        $report += '## Figure Caption Frequency'
        foreach ($kv in ($figureCaptionCounts.GetEnumerator() | Sort-Object Name)) {
            $safeCaption = ([string]$kv.Key).Replace('|', '\|')
            $report += "- $safeCaption => $($kv.Value)"
        }
    }

    Set-Content -LiteralPath $reportAbsPath -Value $report -Encoding UTF8
    Write-Host "Updated report: $reportAbsPath"
    Write-Host "Updated paragraph audit: $auditCsvPath"

    if ($criticalIssues.Count -gt 0) {
        exit 2
    }

    exit 0
}
catch {
    $errorMessage = $_.Exception.Message
    $notes += "Render audit failed: $errorMessage"

    $report = @()
    $report += '# Word UI Render Check Report'
    $report += ''
    $report += "Date (UTC): $timestampUtc"
    $report += ''
    $report += '## Result'
    $report += '- FAIL: Word COM rendering audit could not complete.'
    $report += "- Error: $errorMessage"
    $report += ''
    $report += '## Suggested Actions'
    $report += '- Confirm Microsoft Word is installed and can be launched under this user account.'
    $report += '- Re-run the task `08: Word UI Render Check (COM)`.'

    Set-Content -LiteralPath $reportAbsPath -Value $report -Encoding UTF8
    Write-Host "Updated report: $reportAbsPath"
    exit 1
}
finally {
    if ($document -ne $null) {
        try {
            $document.Close($false)
        }
        catch {
        }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }

    if ($word -ne $null) {
        try {
            $word.Quit()
        }
        catch {
        }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }

    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
