param(
    [switch]$Strict,
    [string]$OutputFile = "pip_audit_report_latest.txt"
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

$pythonExe = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $implRoot ".venv\Scripts\python.exe"),
    (Join-Path $workspaceRoot ".venv\Scripts\python.exe")
)

if (-not $pythonExe) {
    throw "Python executable not found in workspace or implementation virtual environment."
}

Push-Location $implRoot
try {
    $requirementsPath = Join-Path $implRoot "requirements.txt"
    if (-not (Test-Path $requirementsPath)) {
        throw "requirements.txt not found at $requirementsPath"
    }

    $cmdOutput = & $pythonExe -m pip_audit --progress-spinner off -r $requirementsPath 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$lines = @($cmdOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
$joined = ($lines -join "`n")
$hasFindings = $joined -match "Found\s+\d+\s+known\s+vulnerabilit"
$runtimeError = ($exitCode -ne 0) -and (-not $hasFindings)

$outputPath = Join-Path $workspaceRoot $OutputFile
$reportLines = @()
$reportLines += "Dependency audit report"
$reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$reportLines += "scope: src runtime requirements (07_implementation/requirements.txt)"
$reportLines += "mode: $(if ($Strict) { 'strict' } else { 'advisory' })"
$reportLines += ""

if ($lines.Count -eq 0) {
    $reportLines += "No pip-audit output captured."
}
else {
    $reportLines += $lines
}

if ($runtimeError) {
    $reportLines += ""
    $reportLines += "[runtime_error]"
    $reportLines += "pip_audit_exit_code=$exitCode"
}

$reportLines | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Dependency audit report written to: $outputPath"

if ($runtimeError) {
    exit $exitCode
}

if ($Strict -and $hasFindings) {
    exit 1
}

exit 0
