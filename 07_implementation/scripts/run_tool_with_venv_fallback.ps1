param(
    [ValidateSet("python", "pyright", "ruff", "duckdb", "mlr", "sqlite3", "vd", "wargs", "pandoc", "dot", "mmdc", "vale")]
    [string]$Tool = "python",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArgs
)

$ErrorActionPreference = "Stop"

function Sync-SessionPathFromRegistry {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")

    $pathParts = @()
    if ($machinePath) { $pathParts += $machinePath }
    if ($userPath) { $pathParts += $userPath }

    if ($pathParts.Count -gt 0) {
        # Ensure no-profile task shells inherit full installed CLI visibility.
        $env:Path = ($pathParts -join ";")
    }
}

Sync-SessionPathFromRegistry

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

function Resolve-ToolExecutable {
    param([string]$Name)

    if ($Name -eq "python") {
        $candidate = Resolve-FirstExistingPath -Candidates @(
            (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
            (Join-Path $implRoot ".venv\Scripts\python.exe")
        )
        if ($candidate) {
            return $candidate
        }
        return "python"
    }

    if ($Name -eq "pyright") {
        $candidate = Resolve-FirstExistingPath -Candidates @(
            (Join-Path $workspaceRoot ".venv\Scripts\pyright.exe"),
            (Join-Path $implRoot ".venv\Scripts\pyright.exe")
        )
        if ($candidate) {
            return $candidate
        }
        return "pyright"
    }

    if ($Name -eq "ruff") {
        $candidate = Resolve-FirstExistingPath -Candidates @(
            (Join-Path $workspaceRoot ".venv\Scripts\ruff.exe"),
            (Join-Path $implRoot ".venv\Scripts\ruff.exe")
        )
        if ($candidate) {
            return $candidate
        }
        return "ruff"
    }

    if ($Name -in @("duckdb", "mlr", "sqlite3", "vd")) {
        return $Name
    }

    if ($Name -eq "dot") {
        # Graphviz winget install does not add to Machine PATH on this machine.
        # Fall back to the known install location before trying PATH resolution.
        $dotCandidate = "C:\Program Files\Graphviz\bin\dot.exe"
        if (Test-Path $dotCandidate) {
            return $dotCandidate
        }
        return "dot"
    }

    if ($Name -in @("wargs", "pandoc", "mmdc", "vale")) {
        return $Name
    }

    throw "Unsupported tool: $Name"
}

$exe = Resolve-ToolExecutable -Name $Tool

& $exe @ToolArgs
exit $LASTEXITCODE
