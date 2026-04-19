param(
    [switch]$Strict,
    [ValidateRange(3, 200)]
    [int]$MinSimilarityLines = 8,
    [string]$OutputFile = "duplicate_src_report_latest.txt"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent

function Resolve-FirstExistingPath {
    param([string[]]$Candidates)

    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

$pylintExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $workspaceRoot ".venv\Scripts\pylint.exe"),
    (Join-Path $workspaceRoot ".venv-1\Scripts\pylint.exe"),
    (Join-Path $implRoot ".venv\Scripts\pylint.exe")
)

if (-not $pylintExe) {
    throw "Pylint executable not found in workspace or implementation virtual environment. Install with: pip install pylint"
}

$cmdOutput = @()
$exitCode = 0

Push-Location $implRoot
try {
    $cmdOutput = & $pylintExe src --disable=all --enable=duplicate-code --min-similarity-lines $MinSimilarityLines 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$lines = @($cmdOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
$outputPath = Join-Path $workspaceRoot $OutputFile

$reportLines = @()
$reportLines += "Duplicate-code workflow report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src"
$reportLines += "min_similarity_lines: $MinSimilarityLines"
$reportLines += ""

if ($lines.Count -eq 0) {
    $reportLines += "All checks passed!"
}
else {
    $reportLines += $lines
}

$reportLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Duplicate-code report written to: $outputPath"

if ($Strict -and $lines.Count -gt 0) {
    exit 1
}

exit 0
