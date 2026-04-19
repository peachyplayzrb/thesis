param(
    [ValidateSet("python", "pyright", "ruff")]
    [string]$Tool = "python",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArgs
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

    throw "Unsupported tool: $Name"
}

$exe = Resolve-ToolExecutable -Name $Tool

& $exe @ToolArgs
exit $LASTEXITCODE
