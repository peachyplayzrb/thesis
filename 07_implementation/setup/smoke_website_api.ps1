param(
  [string]$BaseUrl = "http://127.0.0.1:5501"
)

$ErrorActionPreference = "Stop"

function Assert-True {
  param(
    [bool]$Condition,
    [string]$Message
  )
  if (-not $Condition) {
    throw $Message
  }
}

function Get-StatusCode {
  param([string]$Path)
  $response = Invoke-WebRequest -Uri ("$BaseUrl$Path") -UseBasicParsing
  return [int]$response.StatusCode
}

function Get-Json {
  param([string]$Path)
  return Invoke-RestMethod -Uri ("$BaseUrl$Path") -Method Get
}

Write-Output "Running website smoke checks against $BaseUrl"

$importStatus = Get-StatusCode "/website/import.html"
$runStatus = Get-StatusCode "/website/run.html"
Assert-True ($importStatus -eq 200) "Import page is not reachable."
Assert-True ($runStatus -eq 200) "Run page is not reachable."

$health = Get-Json "/api/health"
Assert-True ($health.status -eq "ok") "Health endpoint did not return status=ok."
Assert-True ([int]$health.server.port -gt 0) "Health endpoint did not report server port."

$config = Get-Json "/api/runtime/config"
Assert-True ($null -ne $config.pipeline) "Runtime config missing pipeline block."
Assert-True ($config.pipeline.stages.Count -ge 6) "Runtime config missing stage catalog entries."
Assert-True ($null -ne $config.pipeline.stage_parameter_schema.bl004) "Runtime config missing BL-004 parameter schema."

$validatePayload = @{
  stage_params = @{
    bl004 = @{
      top_tag_limit = 12
      user_id = "smoke_user"
    }
    bl006 = @{
      numeric_thresholds = @{
        tempo = 15.0
      }
    }
  }
} | ConvertTo-Json -Depth 8

$validate = Invoke-RestMethod -Uri ("$BaseUrl/api/runtime/config/validate") -Method Post -ContentType "application/json" -Body $validatePayload
Assert-True ([bool]$validate.valid) "Runtime config validation returned invalid payload for a known-good request."

$stageCatalog = Get-Json "/api/pipeline/stages"
Assert-True ($stageCatalog.stages.Count -eq 6) "Stage catalog should contain 6 stages."

$pipeline = Get-Json "/api/pipeline/run/status"
Assert-True ($null -ne $pipeline.run.status) "Pipeline status response missing run.status."

Write-Output "SMOKE_OK import=$importStatus run=$runStatus health=$($health.status) stages=$($stageCatalog.stages.Count) pipeline_status=$($pipeline.run.status)"
