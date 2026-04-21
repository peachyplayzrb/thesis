param(
    [ValidateSet("preflight", "ci-guard", "typecheck", "tests", "validate-only", "full-contract")]
    [string]$Mode = "full-contract",
    [switch]$SkipSetup,
    [switch]$SkipTypecheck,
    [string]$RunConfig,
    [switch]$EmitAutopilotReport
)

$ErrorActionPreference = "Stop"

function Get-PathEntries {
    param([string]$PathValue)

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return @()
    }

    return @($PathValue -split ";" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Sync-SessionPathFromRegistry {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $existingPath = $env:Path

    $candidateEntries = @()
    $candidateEntries += Get-PathEntries -PathValue $machinePath
    $candidateEntries += Get-PathEntries -PathValue $userPath
    $candidateEntries += Get-PathEntries -PathValue $existingPath

    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
    $mergedEntries = @()
    foreach ($entry in $candidateEntries) {
        if ($seen.Add($entry)) {
            $mergedEntries += $entry
        }
    }

    if ($mergedEntries.Count -gt 0) {
        $env:Path = ($mergedEntries -join ";")
    }
}

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
    param([string]$WorkspaceRoot, [string]$ImplementationRoot)

    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"),
        (Join-Path $ImplementationRoot ".venv\Scripts\python.exe")
    )
}

function Resolve-ActivateScript {
    param([string]$WorkspaceRoot, [string]$ImplementationRoot)

    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $WorkspaceRoot ".venv\Scripts\Activate.ps1"),
        (Join-Path $ImplementationRoot ".venv\Scripts\Activate.ps1")
    )
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    Write-Host "STEP: $Name" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkGray

    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

Sync-SessionPathFromRegistry

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent
$pythonExe = Resolve-PythonExe -WorkspaceRoot $workspaceRoot -ImplementationRoot $implRoot

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
            Invoke-Step -Name "Type check (pyright)" -Action {
                & ".\scripts\run_tool_with_venv_fallback.ps1" pyright --project .\pyrightconfig.json
            }
        }
        "tests" {
            Invoke-Step -Name "Test suite" -Action {
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
            $activateScript = Resolve-ActivateScript -WorkspaceRoot $workspaceRoot -ImplementationRoot $implRoot
            if ($null -eq $activateScript) {
                throw "Virtual environment activation script not found in workspace/local .venv paths."
            }

            if ($RunConfig) {
                Write-Host "WARN: -RunConfig is ignored in full-contract mode." -ForegroundColor Yellow
            }

            Invoke-Step -Name "Preflight" -Action {
                & ".\scripts\preflight_windows.ps1"
            }

            if (-not $SkipSetup) {
                Invoke-Step -Name "Bootstrap environment" -Action {
                    & ".\setup.ps1"
                }
            }
            else {
                Write-Host "Skipping setup (--SkipSetup provided)." -ForegroundColor Yellow
            }

            Invoke-Step -Name "Activate virtual environment" -Action {
                & $activateScript
            }

            Invoke-Step -Name "Architecture guard (Phase 6)" -Action {
                & $pythonExe .\ci_guard_phase_6_check.py
            }

            Invoke-Step -Name "Test suite" -Action {
                & $pythonExe -m pytest .\tests -v
            }

            if (-not $SkipTypecheck) {
                $pyrightPath = Resolve-FirstExistingPath -Candidates @(
                    (Join-Path $workspaceRoot ".venv\Scripts\pyright.exe"),
                    (Join-Path $implRoot ".venv\Scripts\pyright.exe")
                )
                if (Test-Path $pyrightPath) {
                    Invoke-Step -Name "Type check (pyright)" -Action {
                        & $pyrightPath --project .\pyrightconfig.json
                    }
                }
                else {
                    Write-Host "WARN: pyright executable not found at $pyrightPath. Skipping typecheck." -ForegroundColor Yellow
                }
            }
            else {
                Write-Host "Skipping typecheck (--SkipTypecheck provided)." -ForegroundColor Yellow
            }

            Invoke-Step -Name "Wrapper validate-only run (BL-013 + BL-014)" -Action {
                & $pythonExe .\main.py --validate-only
            }

            Invoke-Step -Name "BL-014 quality gate" -Action {
                $sanityReport = Join-Path $implRoot "src/quality/outputs/bl014_sanity_report.json"
                if (-not (Test-Path $sanityReport)) {
                    throw "BL-014 sanity report not found: $sanityReport"
                }

                $status = & $pythonExe -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,'r',encoding='utf-8')); print(str(d.get('overall_status','')).lower())" $sanityReport
                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to read BL-014 sanity report status"
                }

                if ($status.Trim() -ne "pass") {
                    throw "BL-014 sanity gate failed with overall_status='$($status.Trim())'"
                }
            }

            Write-Host ""
            Write-Host "PASS: End-to-end checks completed." -ForegroundColor Green
            Write-Host "Artifacts:" -ForegroundColor Green
            Write-Host "  - src/orchestration/outputs/bl013_orchestration_run_latest.json"
            Write-Host "  - src/quality/outputs/bl014_sanity_report.json"
        }
        default {
            throw "Unsupported mode: $Mode"
        }
    }
}
catch {
    $exitCode = 1
    Write-Host ""
    Write-Host "WORKFLOW FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    if ($EmitAutopilotReport) {
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
