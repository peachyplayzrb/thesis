const refreshBtn = document.getElementById("results-refresh-btn");
const messageNode = document.getElementById("results-message");
const runIdNode = document.getElementById("results-run-id");
const statusNode = document.getElementById("results-status");
const stageNode = document.getElementById("results-stage");
const startedNode = document.getElementById("results-started");
const finishedNode = document.getElementById("results-finished");
const changeCountNode = document.getElementById("results-change-count");
const playlistBody = document.getElementById("results-playlist-body");
const compareNode = document.getElementById("results-compare");
const jsonNode = document.getElementById("results-json");
const artifactsNode = document.getElementById("results-artifacts");

const API_RESULTS = "/api/pipeline/run/results";

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) return "-";
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return isoValue;
  return date.toISOString().replace(".000", "");
}

function getRunIdFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("run_id");
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    const raw = await response.text();
    if (raw) {
      try {
        const payload = JSON.parse(raw);
        if (payload && payload.error) message = payload.error;
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

function renderPlaylist(rows) {
  if (!Array.isArray(rows) || !rows.length) {
    playlistBody.innerHTML = '<tr><td colspan="4" class="hint">No playlist preview available yet.</td></tr>';
    return;
  }

  playlistBody.innerHTML = rows.map((row) => {
    return `<tr>
      <td>${row.track_id || "-"}</td>
      <td>${row.title || "-"}</td>
      <td>${row.artist || "-"}</td>
      <td>${row.score === null || row.score === undefined ? "-" : row.score}</td>
    </tr>`;
  }).join("");
}

function renderCompare(compare) {
  if (!compare) {
    compareNode.innerHTML = '<p class="hint">No compare data yet.</p>';
    return;
  }

  const changed = Array.isArray(compare.changed_artifacts) ? compare.changed_artifacts : [];
  const unchanged = Array.isArray(compare.unchanged_artifacts) ? compare.unchanged_artifacts : [];

  compareNode.innerHTML = `
    <div class="artifact-item">
      <p><strong>Baseline Run:</strong> ${compare.baseline_run_id || "none"}</p>
      <p class="track-meta"><strong>Changed (${changed.length}):</strong> ${changed.length ? changed.join(", ") : "none"}</p>
      <p class="track-meta"><strong>Unchanged (${unchanged.length}):</strong> ${unchanged.length ? unchanged.join(", ") : "none"}</p>
    </div>
  `;
}

function renderArtifacts(artifactSummary) {
  if (!artifactSummary || !Object.keys(artifactSummary).length) {
    artifactsNode.innerHTML = '<p class="hint">No artifact summary available yet.</p>';
    return;
  }

  artifactsNode.innerHTML = Object.entries(artifactSummary).map(([key, info]) => {
    const ready = info && !info.missing;
    return `
      <div class="artifact-item">
        <p><strong>${key}</strong> (${ready ? "ready" : "missing"})</p>
        <p class="track-meta">Path: ${info.path || "-"}</p>
        <p class="track-meta">Updated: ${formatDateTimeDisplay(info.mtime_utc)}</p>
        <p class="track-meta">Hash: ${info.sha256 || "-"}</p>
      </div>
    `;
  }).join("");
}

function renderSnapshot(snapshot) {
  const run = snapshot.run || null;
  if (!run) {
    messageNode.textContent = "No completed run found yet.";
    runIdNode.textContent = "-";
    statusNode.textContent = "-";
    stageNode.textContent = "-";
    startedNode.textContent = "-";
    finishedNode.textContent = "-";
    changeCountNode.textContent = "-";
    renderPlaylist([]);
    renderCompare(null);
    renderArtifacts(null);
    jsonNode.textContent = "No result payload loaded yet.";
    return;
  }

  messageNode.textContent = run.current_message || "Results loaded.";
  runIdNode.textContent = run.run_id || "-";
  statusNode.textContent = run.status || "-";
  stageNode.textContent = run.current_stage || "-";
  startedNode.textContent = formatDateTimeDisplay(run.started_at_utc);
  finishedNode.textContent = formatDateTimeDisplay(run.completed_at_utc);

  const compare = snapshot.compare_to_previous || null;
  changeCountNode.textContent = compare && Number.isFinite(compare.changed_count) ? String(compare.changed_count) : "-";

  renderPlaylist(snapshot.playlist_preview || []);
  renderCompare(compare);
  renderArtifacts(run.artifact_summary || {});

  jsonNode.textContent = JSON.stringify({
    explanation_summary: snapshot.explanation_summary,
    observability_summary: snapshot.observability_summary
  }, null, 2);
}

async function refreshResults() {
  messageNode.textContent = "Loading results...";
  try {
    const runId = getRunIdFromQuery();
    const suffix = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
    const snapshot = await fetchJson(`${API_RESULTS}${suffix}`);
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

refreshBtn.addEventListener("click", refreshResults);
refreshResults();
