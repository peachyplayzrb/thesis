param(
    [ValidateSet('full', 'clarity', 'academic', 'strict', 'readability')]
    [string]$Mode = 'full',
    [string]$Target = '08_writing/chapter2.md',
    [string]$OutputPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$wrapperPath = Join-Path $PSScriptRoot 'run_tool_with_venv_fallback.ps1'

if (-not (Test-Path -LiteralPath $wrapperPath)) {
    throw "Wrapper not found: $wrapperPath"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $reportsDir = Join-Path $workspaceRoot 'reports'
    if (-not (Test-Path -LiteralPath $reportsDir)) {
        New-Item -ItemType Directory -Path $reportsDir | Out-Null
    }

    $targetLeaf = Split-Path -Leaf $Target
    if ([string]::IsNullOrWhiteSpace($targetLeaf) -or $targetLeaf -eq '08_writing' -or $targetLeaf -eq '.') {
        $targetStem = 'all_writing'
    }
    else {
        $targetStem = [System.IO.Path]::GetFileNameWithoutExtension($targetLeaf)
    }
    $OutputPath = Join-Path $reportsDir ("vale_{0}_{1}_latest.txt" -f $targetStem, $Mode)
}

$valeArgs = @()
switch ($Mode) {
    'clarity' {
        $valeArgs += '--config'
        $valeArgs += '.vale-clarity.ini'
    }
    'academic' {
        $valeArgs += '--config'
        $valeArgs += '.vale-academic.ini'
    }
    'strict' {
        $valeArgs += '--config'
        $valeArgs += '.vale-strict.ini'
    }
    'readability' {
        $valeArgs += '--config'
        $valeArgs += '.vale-readability.ini'
    }
    default {
        # Full mode uses .vale.ini implicitly.
    }
}
$valeArgs += $Target

Push-Location $workspaceRoot
try {
    & $wrapperPath vale @valeArgs 2>&1 | Tee-Object -FilePath $OutputPath
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "Vale run completed with no alerts."
        Write-Host "Report written to: $OutputPath"
        exit 0
    }

    if ($exitCode -eq 1) {
        Write-Host "Vale run completed with lint alerts (expected for prose review)."
        Write-Host "Report written to: $OutputPath"
        exit 0
    }

    Write-Error "Vale exited with code $exitCode"
    Write-Host "Partial/full output written to: $OutputPath"
    exit $exitCode
}
finally {
    Pop-Location
}
