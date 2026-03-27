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
const configTriggerNode = document.getElementById("results-config-trigger");
const configStagesNode = document.getElementById("results-config-stages");
const configKeysNode = document.getElementById("results-config-keys");
const requestConfigJsonNode = document.getElementById("results-request-config-json");
const stageTraceBody = document.getElementById("results-stage-trace-body");
const explainRunIdNode = document.getElementById("results-explain-run-id");
const explainGeneratedNode = document.getElementById("results-explain-generated");
const explainTrackCountNode = document.getElementById("results-explain-track-count");
const explainDistBody = document.getElementById("results-explain-dist-body");
const explainHashBody = document.getElementById("results-explain-hash-body");
const observeRunIdNode = document.getElementById("results-observe-run-id");
const observeDatasetNode = document.getElementById("results-observe-dataset");
const observePipelineNode = document.getElementById("results-observe-pipeline");
const observeBootstrapNode = document.getElementById("results-observe-bootstrap");
const observeConfigSourceNode = document.getElementById("results-observe-config-source");
const observePlaylistLengthNode = document.getElementById("results-observe-playlist-length");
const observeStageBody = document.getElementById("results-observe-stage-body");
const observeDiagBody = document.getElementById("results-observe-diag-body");
const playlistJsonNode = document.getElementById("results-playlist-json");

const API_RESULTS = "/api/pipeline/run/results";

function escapeHtml(value) {
  return String(value ?? "-")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

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

function formatElapsed(started, finished) {
  if (!started || !finished) {
    return "-";
  }
  const start = new Date(started);
  const end = new Date(finished);
  const seconds = (end.getTime() - start.getTime()) / 1000;
  if (!Number.isFinite(seconds) || seconds < 0) {
    return "-";
  }
  return `${seconds.toFixed(3)}s`;
}

function formatBytes(value) {
  if (!Number.isFinite(value) || value < 0) {
    return "-";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(2)} MB`;
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
      <td>${escapeHtml(row.track_id || "-")}</td>
      <td>${escapeHtml(row.title || "-")}</td>
      <td>${escapeHtml(row.artist || "-")}</td>
      <td>${row.score === null || row.score === undefined ? "-" : escapeHtml(row.score)}</td>
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
      <p><strong>Baseline Run:</strong> ${escapeHtml(compare.baseline_run_id || "none")}</p>
      <p class="track-meta"><strong>Changed (${changed.length}):</strong> ${changed.length ? escapeHtml(changed.join(", ")) : "none"}</p>
      <p class="track-meta"><strong>Unchanged (${unchanged.length}):</strong> ${unchanged.length ? escapeHtml(unchanged.join(", ")) : "none"}</p>
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
        <p class="track-meta">Path: ${escapeHtml(info.path || "-")}</p>
        <p class="track-meta">Size: ${formatBytes(info.size_bytes)}</p>
        <p class="track-meta">Updated: ${formatDateTimeDisplay(info.mtime_utc)}</p>
        <p class="track-meta">Hash: <span class="hash-cell">${escapeHtml(info.sha256 || "-")}</span></p>
      </div>
    `;
  }).join("");
}

function renderRunConfiguration(run) {
  if (!run || typeof run !== "object") {
    configTriggerNode.textContent = "-";
    configStagesNode.textContent = "-";
    configKeysNode.textContent = "-";
    requestConfigJsonNode.textContent = "No request config available.";
    return;
  }

  const requestConfig = run.request_config && typeof run.request_config === "object" ? run.request_config : null;
  const selectedStages = Array.isArray(run.selected_stage_ids) ? run.selected_stage_ids : [];

  configTriggerNode.textContent = requestConfig && requestConfig.trigger ? String(requestConfig.trigger) : "-";
  configStagesNode.textContent = selectedStages.length ? selectedStages.map((s) => String(s).toUpperCase()).join(" -> ") : "-";
  configKeysNode.textContent = requestConfig ? String(Object.keys(requestConfig).length) : "0";
  requestConfigJsonNode.textContent = requestConfig
    ? JSON.stringify(requestConfig, null, 2)
    : "No request config available.";
}

function renderStageTrace(run) {
  if (!run || !Array.isArray(run.stages) || !run.stages.length) {
    stageTraceBody.innerHTML = '<tr><td colspan="7" class="hint">No stage execution trace available yet.</td></tr>';
    return;
  }

  stageTraceBody.innerHTML = run.stages.map((stage) => {
    const status = stage && stage.status ? stage.status : "-";
    return `<tr>
      <td>${escapeHtml(stage.stage_id || "-")}</td>
      <td>${escapeHtml(status)}</td>
      <td>${formatDateTimeDisplay(stage.started_at_utc)}</td>
      <td>${formatDateTimeDisplay(stage.completed_at_utc)}</td>
      <td>${escapeHtml(formatElapsed(stage.started_at_utc, stage.completed_at_utc))}</td>
      <td>${stage.exit_code === null || stage.exit_code === undefined ? "-" : escapeHtml(stage.exit_code)}</td>
      <td>${escapeHtml(stage.current_message || "-")}</td>
    </tr>`;
  }).join("");
}

function renderExplanationSummary(summary) {
  if (!summary || typeof summary !== "object") {
    explainRunIdNode.textContent = "-";
    explainGeneratedNode.textContent = "-";
    explainTrackCountNode.textContent = "-";
    explainDistBody.innerHTML = '<tr><td colspan="2" class="hint">No explanation summary available yet.</td></tr>';
    explainHashBody.innerHTML = '<tr><td colspan="3" class="hint">No BL-008 artifact hashes available yet.</td></tr>';
    return;
  }

  explainRunIdNode.textContent = summary.run_id || "-";
  explainGeneratedNode.textContent = formatDateTimeDisplay(summary.generated_at_utc);
  explainTrackCountNode.textContent = Number.isFinite(summary.playlist_track_count) ? String(summary.playlist_track_count) : "-";

  const distribution = summary.top_contributor_distribution;
  if (!distribution || typeof distribution !== "object" || !Object.keys(distribution).length) {
    explainDistBody.innerHTML = '<tr><td colspan="2" class="hint">No contributor distribution available.</td></tr>';
    return;
  }

  explainDistBody.innerHTML = Object.entries(distribution)
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))
    .map(([name, count]) => `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(count)}</td></tr>`)
    .join("");

  const rows = [];
  const inputHashes = summary.input_artifact_hashes && typeof summary.input_artifact_hashes === "object"
    ? summary.input_artifact_hashes
    : {};
  const outputHashes = summary.output_artifact_hashes && typeof summary.output_artifact_hashes === "object"
    ? summary.output_artifact_hashes
    : {};

  Object.entries(inputHashes).forEach(([artifact, hash]) => {
    rows.push(`<tr><td>input_artifact_hashes</td><td>${escapeHtml(artifact)}</td><td><span class="hash-cell">${escapeHtml(hash || "-")}</span></td></tr>`);
  });
  Object.entries(outputHashes).forEach(([artifact, hash]) => {
    rows.push(`<tr><td>output_artifact_hashes</td><td>${escapeHtml(artifact)}</td><td><span class="hash-cell">${escapeHtml(hash || "-")}</span></td></tr>`);
  });

  explainHashBody.innerHTML = rows.length
    ? rows.join("")
    : '<tr><td colspan="3" class="hint">No BL-008 artifact hashes available yet.</td></tr>';
}

function renderObservabilitySummary(summary) {
  if (!summary || typeof summary !== "object") {
    observeRunIdNode.textContent = "-";
    observeDatasetNode.textContent = "-";
    observePipelineNode.textContent = "-";
    observeBootstrapNode.textContent = "-";
    observeConfigSourceNode.textContent = "-";
    observePlaylistLengthNode.textContent = "-";
    observeStageBody.innerHTML = '<tr><td colspan="2" class="hint">No observability stage run IDs available yet.</td></tr>';
    observeDiagBody.innerHTML = '<tr><td colspan="3" class="hint">No BL-009 diagnostics available yet.</td></tr>';
    return;
  }

  const metadata = summary.run_metadata && typeof summary.run_metadata === "object" ? summary.run_metadata : {};
  const runConfig = summary.run_config && typeof summary.run_config === "object" ? summary.run_config : {};
  const controlMode = runConfig.control_mode && typeof runConfig.control_mode === "object" ? runConfig.control_mode : {};
  const stageOutputs = summary.stage_outputs && typeof summary.stage_outputs === "object" ? summary.stage_outputs : {};

  observeRunIdNode.textContent = metadata.run_id || "-";
  observeDatasetNode.textContent = metadata.dataset_version || "-";
  observePipelineNode.textContent = metadata.pipeline_version || "-";
  observeBootstrapNode.textContent = metadata.bootstrap_mode === undefined ? "-" : String(Boolean(metadata.bootstrap_mode));
  observeConfigSourceNode.textContent = metadata.config_source || controlMode.source || "-";
  observePlaylistLengthNode.textContent = stageOutputs.assembly && Number.isFinite(stageOutputs.assembly.playlist_length)
    ? String(stageOutputs.assembly.playlist_length)
    : "-";

  const upstreamRunIds = metadata.upstream_stage_run_ids && typeof metadata.upstream_stage_run_ids === "object"
    ? metadata.upstream_stage_run_ids
    : {};

  if (!Object.keys(upstreamRunIds).length) {
    observeStageBody.innerHTML = '<tr><td colspan="2" class="hint">No observability stage run IDs available yet.</td></tr>';
    return;
  }

  observeStageBody.innerHTML = Object.entries(upstreamRunIds)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([stage, runId]) => `<tr><td>${escapeHtml(stage)}</td><td>${escapeHtml(runId || "-")}</td></tr>`)
    .join("");

  const datasetHashes = metadata.dataset_component_hashes && typeof metadata.dataset_component_hashes === "object"
    ? metadata.dataset_component_hashes
    : {};
  const scriptHashes = metadata.pipeline_script_hashes && typeof metadata.pipeline_script_hashes === "object"
    ? metadata.pipeline_script_hashes
    : {};
  const optionalDeps = metadata.optional_dependency_availability && typeof metadata.optional_dependency_availability === "object"
    ? metadata.optional_dependency_availability
    : {};

  const diagRows = [];
  Object.entries(datasetHashes).forEach(([key, value]) => {
    diagRows.push(`<tr><td>dataset_component_hashes</td><td>${escapeHtml(key)}</td><td><span class="hash-cell">${escapeHtml(value || "-")}</span></td></tr>`);
  });
  Object.entries(scriptHashes).forEach(([key, value]) => {
    diagRows.push(`<tr><td>pipeline_script_hashes</td><td>${escapeHtml(key)}</td><td><span class="hash-cell">${escapeHtml(value || "-")}</span></td></tr>`);
  });
  Object.entries(optionalDeps).forEach(([key, value]) => {
    diagRows.push(`<tr><td>optional_dependency_availability</td><td>${escapeHtml(key)}</td><td>${escapeHtml(value)}</td></tr>`);
  });

  observeDiagBody.innerHTML = diagRows.length
    ? diagRows.join("")
    : '<tr><td colspan="3" class="hint">No BL-009 diagnostics available yet.</td></tr>';
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
    renderRunConfiguration(null);
    renderStageTrace(null);
    renderExplanationSummary(null);
    renderObservabilitySummary(null);
    playlistJsonNode.textContent = "No playlist payload loaded yet.";
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
  renderRunConfiguration(run);
  renderStageTrace(run);
  renderExplanationSummary(snapshot.explanation_summary || null);
  renderObservabilitySummary(snapshot.observability_summary || null);
  playlistJsonNode.textContent = snapshot.playlist_payload
    ? JSON.stringify(snapshot.playlist_payload, null, 2)
    : "No playlist payload loaded yet.";

  jsonNode.textContent = JSON.stringify(snapshot, null, 2);
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
