param(
    [ValidateSet("python", "pyright", "ruff", "duckdb", "mlr", "sqlite3", "vd", "wargs", "pandoc", "dot", "mmdc", "vale")]
    [string]$Tool = "python",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArgs
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

    # Keep any caller-provided PATH entries, but prepend machine/user PATH so
    # no-profile shells retain installed tool visibility.
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

function Resolve-ExecutableFromPath {
    param([string]$Name)

    $cmd = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }

    throw "Tool '$Name' was not found on PATH after PATH sync."
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
        return Resolve-ExecutableFromPath -Name "python"
    }

    if ($Name -eq "pyright") {
        $candidate = Resolve-FirstExistingPath -Candidates @(
            (Join-Path $workspaceRoot ".venv\Scripts\pyright.exe"),
            (Join-Path $implRoot ".venv\Scripts\pyright.exe")
        )
        if ($candidate) {
            return $candidate
        }
        return Resolve-ExecutableFromPath -Name "pyright"
    }

    if ($Name -eq "ruff") {
        $candidate = Resolve-FirstExistingPath -Candidates @(
            (Join-Path $workspaceRoot ".venv\Scripts\ruff.exe"),
            (Join-Path $implRoot ".venv\Scripts\ruff.exe")
        )
        if ($candidate) {
            return $candidate
        }
        return Resolve-ExecutableFromPath -Name "ruff"
    }

    if ($Name -in @("duckdb", "mlr", "sqlite3", "vd")) {
        return Resolve-ExecutableFromPath -Name $Name
    }

    if ($Name -eq "dot") {
        # Graphviz winget install does not add to Machine PATH on this machine.
        # Fall back to the known install location before trying PATH resolution.
        $dotCandidate = "C:\Program Files\Graphviz\bin\dot.exe"
        if (Test-Path $dotCandidate) {
            return $dotCandidate
        }
        return Resolve-ExecutableFromPath -Name "dot"
    }

    if ($Name -in @("wargs", "pandoc", "mmdc", "vale")) {
        return Resolve-ExecutableFromPath -Name $Name
    }

    throw "Unsupported tool: $Name"
}

$exe = Resolve-ToolExecutable -Name $Tool

& $exe @ToolArgs
exit $LASTEXITCODE
