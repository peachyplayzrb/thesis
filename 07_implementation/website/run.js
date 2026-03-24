const startBtn = document.getElementById("pipeline-start-btn");
const cancelBtn = document.getElementById("pipeline-cancel-btn");
const bundleBtn = document.getElementById("pipeline-bundle-btn");
const refreshBtn = document.getElementById("pipeline-refresh-btn");

const messageNode = document.getElementById("pipeline-message");
const runIdNode = document.getElementById("pipeline-run-id");
const statusNode = document.getElementById("pipeline-status");
const currentStageNode = document.getElementById("pipeline-current-stage");
const startedAtNode = document.getElementById("pipeline-started-at");
const completedAtNode = document.getElementById("pipeline-completed-at");
const logCountNode = document.getElementById("pipeline-log-count");
const healthNode = document.getElementById("pipeline-health");
const uptimeNode = document.getElementById("pipeline-uptime");
const stageBody = document.getElementById("pipeline-stage-body");
const artifactsNode = document.getElementById("pipeline-artifacts");
const logNode = document.getElementById("pipeline-log");

const API_PIPELINE_START = "/api/pipeline/run/start";
const API_PIPELINE_STATUS = "/api/pipeline/run/status";
const API_PIPELINE_CANCEL = "/api/pipeline/run/cancel";
const API_PIPELINE_BUNDLE = "/api/pipeline/run/evidence_bundle";
const API_HEALTH = "/api/health";

let lastLogIndex = 0;
let allLogs = [];
let pollHandle = null;

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) return "-";
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return isoValue;
  return date.toISOString().replace(".000", "");
}

function formatStageLabel(stageId) {
  if (!stageId || stageId === "idle") return "-";
  if (stageId === "completed" || stageId === "cancelled" || stageId === "starting") {
    return stageId;
  }
  return stageId.toUpperCase();
}

function formatDuration(secondsRaw) {
  if (!Number.isFinite(secondsRaw) || secondsRaw < 0) return "-";
  const total = Math.floor(secondsRaw);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
}

async function fetchJson(path, options = undefined) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("Local API is unreachable. Start via setup/start_website.cmd and refresh this page.");
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}): ${path}`;
    const raw = await response.text();
    if (raw) {
      try {
        const payload = JSON.parse(raw);
        if (payload && payload.error) {
          message = payload.error;
        } else {
          message = raw;
        }
      } catch {
        message = raw;
      }
    }

    if (response.status === 404 && path.startsWith("/api/pipeline/")) {
      message = "Pipeline API endpoints are unavailable. Restart the website server so the latest API routes are loaded.";
    }

    throw new Error(message);
  }

  return response.json();
}

function updateButtons(runStatus) {
  const isRunning = runStatus === "running";
  startBtn.disabled = isRunning;
  cancelBtn.disabled = !isRunning;
  bundleBtn.disabled = isRunning;
}

function renderStages(stages) {
  if (!Array.isArray(stages) || !stages.length) {
    stageBody.innerHTML = '<tr><td colspan="6" class="hint">No stage data yet.</td></tr>';
    return;
  }

  stageBody.innerHTML = stages.map((stage) => {
    return `<tr>
      <td>${stage.label}</td>
      <td>${stage.status || "-"}</td>
      <td>${formatDateTimeDisplay(stage.started_at_utc)}</td>
      <td>${formatDateTimeDisplay(stage.completed_at_utc)}</td>
      <td>${stage.exit_code === null || stage.exit_code === undefined ? "-" : stage.exit_code}</td>
      <td>${stage.current_message || "-"}</td>
    </tr>`;
  }).join("");
}

function renderArtifacts(artifactSummary) {
  if (!artifactSummary || !Object.keys(artifactSummary).length) {
    artifactsNode.innerHTML = '<p class="hint">Run pipeline to generate artifact summary.</p>';
    return;
  }

  const html = Object.entries(artifactSummary).map(([key, info]) => {
    const status = info && !info.missing ? "ready" : "missing";
    const mtime = info && info.mtime_utc ? formatDateTimeDisplay(info.mtime_utc) : "-";
    const size = info && Number.isFinite(info.size_bytes) ? `${info.size_bytes} bytes` : "-";
    const path = info && info.path ? info.path : "-";

    return `<div class="artifact-item">
      <p><strong>${key}</strong> (${status})</p>
      <p class="track-meta">Path: ${path}</p>
      <p class="track-meta">Updated: ${mtime}</p>
      <p class="track-meta">Size: ${size}</p>
    </div>`;
  }).join("");

  artifactsNode.innerHTML = html;
}

function appendLogs(logs) {
  if (!Array.isArray(logs) || !logs.length) {
    return;
  }

  logs.forEach((entry) => {
    const prefix = entry.stage_id ? `[${entry.stage_id}] ` : "";
    allLogs.push(`${entry.index.toString().padStart(4, "0")} ${entry.timestamp_utc} ${prefix}${entry.line}`);
  });

  if (allLogs.length > 1200) {
    allLogs = allLogs.slice(-1200);
  }

  logNode.textContent = allLogs.length ? allLogs.join("\n") : "No logs yet.";
  logNode.scrollTop = logNode.scrollHeight;
}

function renderSnapshot(snapshot) {
  const run = snapshot && snapshot.run ? snapshot.run : null;
  if (!run) {
    messageNode.textContent = "No run data available.";
    updateButtons("idle");
    return;
  }

  messageNode.textContent = run.current_message || "-";
  runIdNode.textContent = run.run_id || "-";
  statusNode.textContent = run.status || "idle";
  currentStageNode.textContent = formatStageLabel(run.current_stage);
  startedAtNode.textContent = formatDateTimeDisplay(run.started_at_utc);
  completedAtNode.textContent = formatDateTimeDisplay(run.completed_at_utc);
  logCountNode.textContent = String(run.line_count || 0);

  updateButtons(run.status || "idle");
  renderStages(run.stages || []);
  renderArtifacts(run.artifact_summary || {});

  const incomingLogs = run.logs || [];
  appendLogs(incomingLogs);

  if (incomingLogs.length) {
    const maxIndex = incomingLogs[incomingLogs.length - 1].index;
    if (Number.isFinite(maxIndex)) {
      lastLogIndex = maxIndex;
    }
  }

  if (run.status === "running") {
    startPolling();
  } else {
    stopPolling();
  }
}

function renderHealth(snapshot) {
  const status = snapshot && snapshot.status ? String(snapshot.status).toLowerCase() : "unknown";
  if (healthNode) {
    healthNode.textContent = status;
    healthNode.classList.remove("health-ok", "health-fail", "health-unknown");
    if (status === "ok") {
      healthNode.classList.add("health-ok");
    } else if (status === "fail") {
      healthNode.classList.add("health-fail");
    } else {
      healthNode.classList.add("health-unknown");
    }
  }

  if (uptimeNode) {
    const uptime = snapshot && Number.isFinite(snapshot.uptime_seconds) ? snapshot.uptime_seconds : null;
    uptimeNode.textContent = uptime === null ? "-" : formatDuration(uptime);
  }
}

async function refreshHealth() {
  try {
    const health = await fetchJson(API_HEALTH);
    renderHealth(health);
  } catch {
    renderHealth({ status: "fail", uptime_seconds: null });
  }
}

async function refreshStatus() {
  try {
    const snapshot = await fetchJson(`${API_PIPELINE_STATUS}?after=${lastLogIndex}`);
    renderSnapshot(snapshot);
    await refreshHealth();
  } catch (error) {
    messageNode.textContent = String(error.message || error);
    renderHealth({ status: "fail", uptime_seconds: null });
  }
}

function stopPolling() {
  if (pollHandle) {
    clearInterval(pollHandle);
    pollHandle = null;
  }
}

function startPolling() {
  if (pollHandle) return;
  pollHandle = setInterval(() => {
    refreshStatus();
  }, 1500);
}

async function startRun() {
  messageNode.textContent = "Starting pipeline run...";
  try {
    lastLogIndex = 0;
    allLogs = [];
    logNode.textContent = "No logs yet.";
    const snapshot = await fetchJson(API_PIPELINE_START, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trigger: "website_run_page" })
    });
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

async function cancelRun() {
  messageNode.textContent = "Cancelling pipeline run...";
  try {
    const snapshot = await fetchJson(API_PIPELINE_CANCEL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}"
    });
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

function downloadJsonFile(fileName, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function exportEvidenceBundle() {
  messageNode.textContent = "Creating evidence bundle...";
  try {
    const runId = runIdNode.textContent && runIdNode.textContent !== "-" ? runIdNode.textContent : null;
    const response = await fetchJson(API_PIPELINE_BUNDLE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id: runId })
    });

    const bundle = response.bundle || {};
    const safeRun = (response.run_id || "latest").replace(/[^a-zA-Z0-9._-]/g, "_");
    downloadJsonFile(`website_evidence_bundle_${safeRun}.json`, bundle);
    messageNode.textContent = `Evidence bundle exported (${response.bundle_path || "manifest downloaded"}).`;
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

function wireEvents() {
  startBtn.addEventListener("click", startRun);
  cancelBtn.addEventListener("click", cancelRun);
  bundleBtn.addEventListener("click", exportEvidenceBundle);
  refreshBtn.addEventListener("click", refreshStatus);
}

(async function init() {
  wireEvents();
  await refreshStatus();
})();
