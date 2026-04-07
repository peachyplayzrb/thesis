param(
    [switch]$SkipSetup,
    [switch]$SkipTypecheck
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
    (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
    (Join-Path $implRoot ".venv\Scripts\python.exe")
)

if ($null -eq $pythonExe) {
    throw "Python executable not found in workspace/local .venv paths."
}

$activateScript = Resolve-FirstExistingPath -Candidates @(
    (Join-Path $workspaceRoot ".venv\Scripts\Activate.ps1"),
    (Join-Path $implRoot ".venv\Scripts\Activate.ps1")
)

if ($null -eq $activateScript) {
    throw "Virtual environment activation script not found in workspace/local .venv paths."
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host "";
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    Write-Host "STEP: $Name" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkGray

    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

Push-Location $implRoot
try {
    Invoke-Step -Name "Preflight" -Action {
        & ".\scripts\preflight_windows.ps1"
    }

    if (-not $SkipSetup) {
        Invoke-Step -Name "Bootstrap environment" -Action {
            & ".\setup.ps1"
        }
    } else {
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
                & $pyrightPath .\src
            }
        } else {
            Write-Host "WARN: pyright executable not found at $pyrightPath. Skipping typecheck." -ForegroundColor Yellow
        }
    } else {
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

    Write-Host "";
    Write-Host "PASS: End-to-end checks completed." -ForegroundColor Green
    Write-Host "Artifacts:" -ForegroundColor Green
    Write-Host "  - src/orchestration/outputs/bl013_orchestration_run_latest.json"
    Write-Host "  - src/quality/outputs/bl014_sanity_report.json"
} finally {
    Pop-Location
}
