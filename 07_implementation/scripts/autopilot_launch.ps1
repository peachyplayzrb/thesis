param(
    [ValidateSet("preflight", "ci-guard", "typecheck", "tests", "validate-only", "full-contract")]
    [string]$Mode = "full-contract",
    [switch]$SkipSetup,
    [switch]$SkipTypecheck,
    [string]$RunConfig,
    [switch]$NoReport
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

function Resolve-PythonExe {
    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
        (Join-Path $implRoot ".venv\Scripts\python.exe")
    )
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    Write-Host "AUTOPILOT STEP: $Name" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkGray

    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

$pythonExe = Resolve-PythonExe
if ($null -eq $pythonExe) {
    throw "Python executable not found in workspace/local .venv paths."
}

$exitCode = 0

Push-Location $implRoot
try {
    switch ($Mode) {
        "preflight" {
            Invoke-Step -Name "Preflight" -Action {
                & ".\scripts\preflight_windows.ps1"
            }
        }
        "ci-guard" {
            Invoke-Step -Name "Architecture guard" -Action {
                & ".\scripts\run_tool_with_venv_fallback.ps1" python .\ci_guard_phase_6_check.py
            }
        }
        "typecheck" {
            Invoke-Step -Name "Typecheck" -Action {
                & ".\scripts\run_tool_with_venv_fallback.ps1" pyright .\src
            }
        }
        "tests" {
            Invoke-Step -Name "Tests" -Action {
                & ".\scripts\run_tool_with_venv_fallback.ps1" python -m pytest .\tests -v
            }
        }
        "validate-only" {
            $validateArgs = @(".\main.py", "--validate-only")
            if ($RunConfig) {
                $validateArgs += @("--run-config", $RunConfig)
            }

            Invoke-Step -Name "Validate-only orchestration run" -Action {
                & ".\scripts\run_tool_with_venv_fallback.ps1" python @validateArgs
            }
        }
        "full-contract" {
            if ($RunConfig) {
                Write-Host "WARN: -RunConfig is ignored in full-contract mode because check_all.ps1 does not accept a run-config override." -ForegroundColor Yellow
            }

            $checkAllArgs = @()
            if ($SkipSetup) {
                $checkAllArgs += "-SkipSetup"
            }
            if ($SkipTypecheck) {
                $checkAllArgs += "-SkipTypecheck"
            }

            Invoke-Step -Name "Full contract checks" -Action {
                & ".\scripts\check_all.ps1" @checkAllArgs
            }
        }
        default {
            throw "Unsupported mode: $Mode"
        }
    }
}
catch {
    $exitCode = 1
    Write-Host ""
    Write-Host "AUTOPILOT FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    if (-not $NoReport) {
        try {
            $reportScript = Join-Path $scriptDir "autopilot_report.py"
            & $pythonExe $reportScript --impl-root $implRoot --mode $Mode
            if ($LASTEXITCODE -ne 0) {
                Write-Host "WARN: Failed to generate autopilot report." -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "WARN: Report generation error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    Pop-Location
}

exit $exitCode
