param(
    [ValidateSet("ruff", "coverage", "docstring", "dependency-audit", "bandit", "duplicate", "hygiene")]
    [string]$Mode,
    [switch]$Strict,
    [switch]$Fix,
    [switch]$NoPreview,
    [ValidateRange(0, 100)]
    [int]$FailUnder = 65,
    [ValidateRange(3, 200)]
    [int]$MinSimilarityLines = 8,
    [ValidateRange(1, 100)]
    [int]$MinConfidence = 70,
    [ValidateSet("A", "B", "C", "D", "E", "F")]
    [string]$ComplexityThreshold = "C",
    [string]$OutputFile = "",
    [string[]]$IgnoredVulnerabilityIds = @("PYSEC-2022-42969")
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$implRoot = Resolve-Path (Join-Path $scriptDir "..")
$workspaceRoot = Split-Path $implRoot -Parent
$reportsDir = Join-Path $workspaceRoot "reports"

if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
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

function Resolve-PythonCandidates {
    return @(
        (Join-Path $workspaceRoot ".venv\Scripts\python.exe"),
        (Join-Path $implRoot ".venv\Scripts\python.exe")
    )
}

function Resolve-PythonExe {
    return Resolve-FirstExistingPath -Candidates (Resolve-PythonCandidates)
}

function Resolve-RuffExe {
    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $workspaceRoot ".venv\Scripts\ruff.exe"),
        (Join-Path $implRoot ".venv\Scripts\ruff.exe")
    )
}

function Resolve-PylintExe {
    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $workspaceRoot ".venv\Scripts\pylint.exe"),
        (Join-Path $workspaceRoot ".venv-1\Scripts\pylint.exe"),
        (Join-Path $implRoot ".venv\Scripts\pylint.exe")
    )
}

function Resolve-VultureExe {
    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $workspaceRoot ".venv\Scripts\vulture.exe"),
        (Join-Path $workspaceRoot ".venv-1\Scripts\vulture.exe"),
        (Join-Path $implRoot ".venv\Scripts\vulture.exe")
    )
}

function Resolve-RadonExe {
    return Resolve-FirstExistingPath -Candidates @(
        (Join-Path $workspaceRoot ".venv\Scripts\radon.exe"),
        (Join-Path $workspaceRoot ".venv-1\Scripts\radon.exe"),
        (Join-Path $implRoot ".venv\Scripts\radon.exe")
    )
}

function Resolve-ReportOutputPath {
    param([string]$RequestedFile)

    $leaf = Split-Path -Leaf $RequestedFile
    if ([string]::IsNullOrWhiteSpace($leaf)) {
        throw "Output file name is empty after normalization: '$RequestedFile'"
    }

    return Join-Path $reportsDir $leaf
}

if ([string]::IsNullOrWhiteSpace($OutputFile)) {
    switch ($Mode) {
        "ruff" { $OutputFile = "ruff_src_report_latest.txt" }
        "coverage" { $OutputFile = "coverage_src_report_latest.txt" }
        "docstring" { $OutputFile = "interrogate_src_report_latest.txt" }
        "dependency-audit" { $OutputFile = "pip_audit_report_latest.txt" }
        "bandit" { $OutputFile = "bandit_src_report_latest.txt" }
        "duplicate" { $OutputFile = "duplicate_src_report_latest.txt" }
        "hygiene" { $OutputFile = "hygiene_src_report_latest.txt" }
    }
}

switch ($Mode) {
    "ruff" {
        $ruffExe = Resolve-RuffExe
        if (-not $ruffExe) {
            throw "Ruff executable not found in workspace or implementation virtual environment."
        }

        $previewArgs = @()
        if (-not $NoPreview) {
            $previewArgs += "--preview"
        }

        Push-Location $implRoot
        try {
            if ($Fix) {
                & $ruffExe check src --fix @previewArgs | Out-Null
            }

            $output = & $ruffExe check src --output-format concise --statistics @previewArgs 2>&1
            $exitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile
        if ($exitCode -eq 0 -and @($output).Count -eq 0) {
            "All checks passed!" | Set-Content -Path $outputPath -Encoding utf8
        }
        else {
            @($output) | Set-Content -Path $outputPath -Encoding utf8
        }

        Write-Host "Ruff report written to: $outputPath"
        exit $exitCode
    }

    "coverage" {
        $pythonExe = Resolve-PythonExe
        if (-not $pythonExe) {
            throw "Python executable not found in workspace or implementation virtual environment."
        }

        Push-Location $implRoot
        try {
            $coverageXmlPath = Join-Path $reportsDir "coverage_src_latest.xml"
            $coverageHtmlPath = Join-Path $reportsDir "coverage_src_html"
            $cmdOutput = & $pythonExe -m pytest tests -v --cov=src --cov-report=term-missing --cov-report=xml:$coverageXmlPath --cov-report=html:$coverageHtmlPath --cov-fail-under $FailUnder 2>&1
            $exitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile
        $reportLines = @()
        $reportLines += "Coverage workflow report"
        $reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        $reportLines += "scope: src"
        $reportLines += "coverage_fail_under: $FailUnder"
        $reportLines += "coverage_xml: $coverageXmlPath"
        $reportLines += "coverage_html: $coverageHtmlPath"
        $reportLines += ""
        $reportLines += @($cmdOutput)

        $reportLines | Set-Content -Path $outputPath -Encoding utf8
        Write-Host "Coverage report written to: $outputPath"
        exit $exitCode
    }

    "docstring" {
        $pythonExe = $null
        foreach ($candidate in (Resolve-PythonCandidates)) {
            if (Test-Path $candidate) {
                & $candidate -c "import interrogate" *> $null
                if ($LASTEXITCODE -eq 0) {
                    $pythonExe = $candidate
                    break
                }
                if (-not $pythonExe) {
                    $pythonExe = $candidate
                }
            }
        }

        if (-not $pythonExe) {
            throw "Python executable not found in workspace or implementation virtual environment."
        }

        $effectiveFailUnder = if ($Strict) { $FailUnder } else { 0 }
        $strictModeLabel = if ($Strict) { "strict" } else { "advisory" }

        Push-Location $implRoot
        try {
            $cmdOutput = & $pythonExe -m interrogate src --ignore-init-method --ignore-module --fail-under $effectiveFailUnder 2>&1
            $exitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $lines = @($cmdOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile

        $reportLines = @()
        $reportLines += "Docstring coverage report"
        $reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        $reportLines += "scope: src"
        $reportLines += "mode: $strictModeLabel"
        $reportLines += "fail_under: $effectiveFailUnder"
        $reportLines += ""

        if ($lines.Count -eq 0) {
            $reportLines += "No interrogate output captured."
        }
        else {
            $reportLines += $lines
        }

        $reportLines | Set-Content -Path $outputPath -Encoding utf8
        Write-Host "Docstring coverage report written to: $outputPath"

        exit $exitCode
    }

    "dependency-audit" {
        $pythonExe = Resolve-PythonExe
        if (-not $pythonExe) {
            throw "Python executable not found in workspace or implementation virtual environment."
        }

        Push-Location $implRoot
        try {
            $requirementsPath = Join-Path $implRoot "requirements.txt"
            if (-not (Test-Path $requirementsPath)) {
                throw "requirements.txt not found at $requirementsPath"
            }

            $auditArgs = @("-m", "pip_audit", "--progress-spinner", "off", "-r", $requirementsPath)
            foreach ($vulnId in $IgnoredVulnerabilityIds) {
                if ($vulnId -and $vulnId.Trim().Length -gt 0) {
                    $auditArgs += @("--ignore-vuln", $vulnId.Trim())
                }
            }

            $cmdOutput = & $pythonExe @auditArgs 2>&1
            $exitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $lines = @($cmdOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
        $joined = ($lines -join "`n")
        $hasFindings = $joined -match "Found\s+\d+\s+known\s+vulnerabilit"
        $runtimeError = ($exitCode -ne 0) -and (-not $hasFindings)

        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile
        $reportLines = @()
        $reportLines += "Dependency audit report"
        $reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        $reportLines += "scope: src runtime requirements (07_implementation/requirements.txt)"
        $reportLines += "mode: $(if ($Strict) { 'strict' } else { 'advisory' })"
        if ($IgnoredVulnerabilityIds -and $IgnoredVulnerabilityIds.Count -gt 0) {
            $reportLines += "ignored_vulnerability_ids: $($IgnoredVulnerabilityIds -join ', ')"
        }
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
    }

    "bandit" {
        $pythonExe = Resolve-PythonExe
        $ruffExe = Resolve-RuffExe

        if (-not $pythonExe) {
            throw "Python executable not found in workspace or implementation virtual environment."
        }

        if (-not $ruffExe) {
            throw "Ruff executable not found in workspace or implementation virtual environment."
        }

        $strictModeLabel = if ($Strict) { "strict" } else { "advisory" }
        $activeScanner = "bandit"
        $scanOutput = @()
        $scanExitCode = 0

        $banditArgs = @("-m", "bandit", "-r", "src", "-f", "txt")
        if (-not $Strict) {
            $banditArgs += "--exit-zero"
        }

        Push-Location $implRoot
        try {
            $banditOutput = & $pythonExe @banditArgs 2>&1
            $banditExitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $banditLines = @($banditOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
        $banditJoined = ($banditLines -join "`n")
        $banditAstCompatibilityError = $banditJoined -match "module 'ast' has no attribute 'Num'"

        if ($banditAstCompatibilityError) {
            $activeScanner = "ruff-security-fallback"

            Push-Location $implRoot
            try {
                $ruffOutput = & $ruffExe check src --select S 2>&1
                $ruffExitCode = $LASTEXITCODE
            }
            finally {
                Pop-Location
            }

            $scanOutput = @($ruffOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })

            if ($Strict) {
                $scanExitCode = $ruffExitCode
            }
            else {
                $scanExitCode = 0
            }
        }
        else {
            $scanOutput = $banditLines
            $scanExitCode = $banditExitCode
        }

        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile

        $reportLines = @()
        $reportLines += "Bandit security scan report"
        $reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        $reportLines += "scope: src"
        $reportLines += "mode: $strictModeLabel"
        $reportLines += "active_scanner: $activeScanner"
        $reportLines += ""

        if ($banditAstCompatibilityError) {
            $reportLines += "[note]"
            $reportLines += "Bandit reported Python 3.14 AST compatibility errors; security scan fell back to Ruff S-rules."
            $reportLines += ""
        }

        if ($scanOutput.Count -eq 0) {
            $reportLines += "No security findings output captured."
        }
        else {
            $reportLines += $scanOutput
        }

        $reportLines | Set-Content -Path $outputPath -Encoding utf8
        Write-Host "Bandit report written to: $outputPath"

        exit $scanExitCode
    }

    "duplicate" {
        $pylintExe = Resolve-PylintExe
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
        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile

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
    }

    "hygiene" {
        $vultureExe = Resolve-VultureExe
        $radonExe = Resolve-RadonExe

        if (-not $vultureExe) {
            throw "Vulture executable not found in workspace or implementation virtual environment."
        }

        if (-not $radonExe) {
            throw "Radon executable not found in workspace or implementation virtual environment."
        }

        Push-Location $implRoot
        try {
            $deadCodeOutput = & $vultureExe src --min-confidence $MinConfidence --sort-by-size 2>&1
            $deadCodeExit = $LASTEXITCODE

            $complexityOutput = & $radonExe cc src -s -n $ComplexityThreshold 2>&1
            $complexityExit = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        $deadCodeLines = @($deadCodeOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
        $complexityLines = @($complexityOutput | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })

        $hasDeadCodeFindings = $deadCodeLines.Count -gt 0
        $hasComplexityFindings = $complexityLines.Count -gt 0
        $hasRuntimeError = ($deadCodeExit -gt 1) -or ($complexityExit -ne 0)

        $reportLines = @()
        $reportLines += "Hygiene workflow report"
        $reportLines += "generated_at_utc: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        $reportLines += "scope: src"
        $reportLines += "dead_code_min_confidence: $MinConfidence"
        $reportLines += "complexity_threshold: $ComplexityThreshold"
        $reportLines += ""

        $reportLines += "[dead_code_vulture]"
        if ($hasDeadCodeFindings) {
            $reportLines += $deadCodeLines
        }
        else {
            $reportLines += "No dead-code findings."
        }
        $reportLines += ""

        $reportLines += "[complexity_radon]"
        if ($hasComplexityFindings) {
            $reportLines += $complexityLines
        }
        else {
            $reportLines += "No complexity findings at or above threshold."
        }

        if ($hasRuntimeError) {
            $reportLines += ""
            $reportLines += "[runtime_errors]"
            $reportLines += "vulture_exit_code=$deadCodeExit"
            $reportLines += "radon_exit_code=$complexityExit"
        }

        $outputPath = Resolve-ReportOutputPath -RequestedFile $OutputFile
        $reportLines | Set-Content -Path $outputPath -Encoding utf8

        Write-Host "Hygiene report written to: $outputPath"

        if ($hasRuntimeError) {
            exit 2
        }

        if ($Strict -and ($hasDeadCodeFindings -or $hasComplexityFindings)) {
            exit 1
        }

        exit 0
    }
}
