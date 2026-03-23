param(
    [int]$Port = 5501,
    [string]$Bind = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "..\.venv\Scripts\python.exe"
$pythonExe = [System.IO.Path]::GetFullPath($pythonExe)

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe. Activate or create the project .venv first."
}

$serveDir = $repoRoot

function Test-PortAvailable {
    param(
        [string]$BindAddress,
        [int]$CandidatePort
    )

    $listener = $null
    try {
        $ipAddress = [System.Net.IPAddress]::Parse($BindAddress)
        $listener = [System.Net.Sockets.TcpListener]::new($ipAddress, $CandidatePort)
        $listener.Start()
        return $true
    }
    catch {
        return $false
    }
    finally {
        if ($listener -ne $null) {
            $listener.Stop()
        }
    }
}

$selectedPort = $Port
for ($i = 0; $i -lt 20; $i++) {
    if (Test-PortAvailable -BindAddress $Bind -CandidatePort $selectedPort) {
        break
    }
    $selectedPort += 1
}

if (-not (Test-PortAvailable -BindAddress $Bind -CandidatePort $selectedPort)) {
    throw "Unable to find a free port starting from $Port."
}

Write-Host "Starting website server..."
Write-Host "Directory: $serveDir"
Write-Host "URL: http://$Bind`:$selectedPort/"
Write-Host "Import page: http://$Bind`:$selectedPort/website/import.html"

& $pythonExe "$PSScriptRoot\website_api_server.py" $Bind $selectedPort