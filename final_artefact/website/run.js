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
const compositionMessageNode = document.getElementById("pipeline-composition-message");
const payloadPreviewNode = document.getElementById("pipeline-payload-preview");
const inlineStageControlsNode = document.getElementById("pipeline-inline-stage-controls");
const stageCheckboxes = Array.from(document.querySelectorAll(".pipeline-stage-checkbox"));

const API_PIPELINE_START = "/api/pipeline/run/start";
const API_PIPELINE_STATUS = "/api/pipeline/run/status";
const API_PIPELINE_CANCEL = "/api/pipeline/run/cancel";
const API_PIPELINE_BUNDLE = "/api/pipeline/run/evidence_bundle";
const API_HEALTH = "/api/health";

let lastLogIndex = 0;
let allLogs = [];
let pollHandle = null;
let inlineControlsRendered = false;

const STAGE_ORDER = ["bl003", "bl004", "bl005", "bl006", "bl007", "bl008", "bl009"];

const STAGE_PARAM_DEFS = {
  bl003: [
    {
      key: "input_scope",
      label: "Input scope (JSON object)",
      type: "json",
      defaultValue: "{\n  \"source_family\": \"spotify_api_export\",\n  \"include_top_tracks\": true,\n  \"top_time_ranges\": [\"short_term\", \"medium_term\", \"long_term\"],\n  \"include_saved_tracks\": true,\n  \"saved_tracks_limit\": null,\n  \"include_playlists\": true,\n  \"playlists_limit\": null,\n  \"playlist_items_per_playlist_limit\": null,\n  \"include_recently_played\": true,\n  \"recently_played_limit\": 50\n}"
    },
    { key: "allow_missing_selected_sources", label: "Allow missing selected sources", type: "bool", defaultValue: false }
  ],
  bl004: [
    { key: "top_tag_limit", label: "Top tags limit", type: "int", defaultValue: 10 },
    { key: "top_genre_limit", label: "Top genres limit", type: "int", defaultValue: 8 },
    { key: "top_lead_genre_limit", label: "Top lead-genres limit", type: "int", defaultValue: 6 },
    { key: "user_id", label: "User ID", type: "string", defaultValue: "21zsn42xecjhogne4kghyw5hq" },
    {
      key: "include_interaction_types",
      label: "Included interaction types (JSON array)",
      type: "json_array",
      defaultValue: "[\n  \"history\",\n  \"influence\"\n]"
    }
  ],
  bl005: [
    { key: "semantic_strong_keep_score", label: "Semantic strong-keep score", type: "int", defaultValue: 2 },
    { key: "semantic_min_keep_score", label: "Semantic minimum keep score", type: "int", defaultValue: 1 },
    { key: "numeric_support_min_pass", label: "Numeric support minimum pass", type: "int", defaultValue: 1 },
    { key: "profile_top_lead_genre_limit", label: "Top lead genres", type: "int", defaultValue: 6 },
    { key: "profile_top_tag_limit", label: "Top tags", type: "int", defaultValue: 10 },
    { key: "profile_top_genre_limit", label: "Top genres", type: "int", defaultValue: 8 },
    {
      key: "numeric_thresholds",
      label: "Numeric thresholds (JSON object)",
      type: "json",
      defaultValue: "{\n  \"danceability\": 0.2,\n  \"energy\": 0.2,\n  \"valence\": 0.2,\n  \"tempo\": 20.0,\n  \"duration_ms\": 45000.0,\n  \"key\": 2.0,\n  \"mode\": 0.5\n}"
    }
  ],
  bl006: [
    {
      key: "component_weights",
      label: "Component weights (JSON object)",
      type: "json",
      defaultValue: "{\n  \"tempo\": 0.1,\n  \"duration_ms\": 0.07,\n  \"key\": 0.06,\n  \"mode\": 0.04,\n  \"lead_genre\": 0.17,\n  \"genre_overlap\": 0.12,\n  \"tag_overlap\": 0.16,\n  \"danceability\": 0.1,\n  \"energy\": 0.1,\n  \"valence\": 0.08\n}"
    },
    {
      key: "numeric_thresholds",
      label: "Numeric thresholds (JSON object)",
      type: "json",
      defaultValue: "{\n  \"tempo\": 20.0,\n  \"duration_ms\": 60000.0,\n  \"key\": 3.0,\n  \"mode\": 1.0\n}"
    }
  ],
  bl007: [
    { key: "target_size", label: "Target playlist size", type: "int", defaultValue: 10 },
    { key: "min_score_threshold", label: "Minimum score threshold", type: "float", defaultValue: 0.35 },
    { key: "max_per_genre", label: "Max tracks per genre", type: "int", defaultValue: 4 },
    { key: "max_consecutive", label: "Max consecutive same-genre tracks", type: "int", defaultValue: 2 }
  ],
  bl008: [
    { key: "top_contributor_limit", label: "Top contributors per track", type: "int", defaultValue: 3 },
    { key: "blend_primary_contributor_on_near_tie", label: "Blend primary contributor on near tie", type: "bool", defaultValue: false },
    { key: "primary_contributor_tie_delta", label: "Primary contributor tie delta", type: "float", defaultValue: 0.02 }
  ],
  bl009: [
    { key: "diagnostic_sample_limit", label: "Diagnostic sample limit", type: "int", defaultValue: 5 },
    { key: "bootstrap_mode", label: "Bootstrap mode", type: "bool", defaultValue: true }
  ]
};

const apiFetchJson =
  window.WebsiteApi && typeof window.WebsiteApi.fetchJson === "function"
    ? window.WebsiteApi.fetchJson
    : null;

const escapeHtml =
  window.WebsiteApi && typeof window.WebsiteApi.escapeHtml === "function"
    ? window.WebsiteApi.escapeHtml
    : (value) => String(value ?? "-")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isFiniteNumberObject(value) {
  return isPlainObject(value) && Object.values(value).every((item) => Number.isFinite(item));
}

function validateJsonParam(stageId, key, payload) {
  if (stageId === "bl003" && key === "input_scope") {
    if (!isPlainObject(payload)) {
      return "Expected JSON object for BL003.input_scope.";
    }
    if (payload.top_time_ranges !== undefined) {
      if (!Array.isArray(payload.top_time_ranges) || payload.top_time_ranges.some((item) => typeof item !== "string")) {
        return "BL003.input_scope.top_time_ranges must be an array of strings.";
      }
    }
    return "";
  }

  if (stageId === "bl004" && key === "include_interaction_types") {
    if (!Array.isArray(payload) || payload.some((item) => typeof item !== "string" || !String(item).trim())) {
      return "BL004.include_interaction_types must be a non-empty string array.";
    }
    return "";
  }

  if (stageId === "bl005" && key === "numeric_thresholds") {
    return isFiniteNumberObject(payload)
      ? ""
      : "BL005.numeric_thresholds must be a JSON object with numeric values.";
  }

  if (stageId === "bl006" && (key === "component_weights" || key === "numeric_thresholds")) {
    return isFiniteNumberObject(payload)
      ? ""
      : `BL006.${key} must be a JSON object with numeric values.`;
  }

  return "";
}

function stageLabel(stageId) {
  return stageId.toUpperCase();
}

function makeDefaultString(def) {
  if (def.type === "bool") {
    return def.defaultValue ? "true" : "false";
  }
  if (def.defaultValue === null || def.defaultValue === undefined) {
    return "";
  }
  return String(def.defaultValue);
}

function setInputValue(input, type, value) {
  if (type === "bool") {
    const lowered = String(value ?? "").trim().toLowerCase();
    input.checked = lowered === "true" || lowered === "1" || lowered === "yes" || lowered === "on";
    return;
  }
  input.value = String(value ?? "");
}

function getInputRaw(input, type) {
  if (type === "bool") {
    return input.checked ? "true" : "false";
  }
  return String(input.value || "").trim();
}

function renderInlineStageControls(availableStageIds = STAGE_ORDER) {
  if (!inlineStageControlsNode || inlineControlsRendered) {
    return;
  }

  inlineStageControlsNode.innerHTML = "";
  const availableSet = new Set(Array.isArray(availableStageIds) && availableStageIds.length ? availableStageIds : STAGE_ORDER);

  STAGE_ORDER.forEach((stageId) => {
    if (!availableSet.has(stageId)) {
      return;
    }
    const defs = Array.isArray(STAGE_PARAM_DEFS[stageId]) ? STAGE_PARAM_DEFS[stageId] : [];
    if (!defs.length) {
      return;
    }

    const preset = loadStageParamsFromPreset(stageId) || {};

    const block = document.createElement("details");
    block.className = "inline-stage-block";
    block.dataset.stageId = stageId;

    const summary = document.createElement("summary");
    summary.textContent = `${stageLabel(stageId)} parameters`;
    block.appendChild(summary);

    const grid = document.createElement("div");
    grid.className = "inline-stage-grid";

    defs.forEach((def, index) => {
      const row = document.createElement("div");
      row.className = "inline-stage-field";

      const label = document.createElement("label");
      const inputId = `${stageId}-${def.key}-${index}`;
      label.setAttribute("for", inputId);
      label.textContent = def.label;

      let input;
      if (def.type === "json" || def.type === "json_array") {
        input = document.createElement("textarea");
        input.rows = 5;
        input.className = "form-control run-config-textarea";
      } else if (def.type === "bool") {
        input = document.createElement("input");
        input.type = "checkbox";
        input.className = "form-check-input";
      } else {
        input = document.createElement("input");
        input.type = def.type === "string" ? "text" : "number";
        input.className = "form-control";
      }

      const defaultText = makeDefaultString(def);
      const presetValue = Object.prototype.hasOwnProperty.call(preset, def.key) ? preset[def.key] : defaultText;
      setInputValue(input, def.type, presetValue);
      input.dataset.initialValue = getInputRaw(input, def.type);
      input.dataset.paramKey = def.key;
      input.dataset.paramType = def.type;
      input.id = inputId;

      row.appendChild(label);
      row.appendChild(input);
      grid.appendChild(row);
    });

    block.appendChild(grid);
    inlineStageControlsNode.appendChild(block);
  });

  inlineControlsRendered = true;
}

function collectInlineStageParams() {
  if (!inlineStageControlsNode) {
    return {};
  }

  const out = {};
  const blocks = Array.from(inlineStageControlsNode.querySelectorAll(".inline-stage-block"));

  blocks.forEach((block) => {
    const stageId = block.dataset.stageId;
    const params = {};
    const inputs = Array.from(block.querySelectorAll("[data-param-key]"));

    inputs.forEach((input) => {
      const key = String(input.dataset.paramKey || "");
      const type = String(input.dataset.paramType || "");
      const currentRaw = getInputRaw(input, type);
      const initialRaw = String(input.dataset.initialValue || "");
      if (!key || currentRaw === initialRaw) {
        return;
      }

      if (type === "bool") {
        params[key] = currentRaw === "true";
        return;
      }

      if (type === "int") {
        const parsed = Number.parseInt(currentRaw, 10);
        if (!Number.isFinite(parsed)) {
          throw new Error(`Invalid integer for ${stageLabel(stageId)}.${key}`);
        }
        params[key] = parsed;
        return;
      }

      if (type === "float") {
        const parsed = Number.parseFloat(currentRaw);
        if (!Number.isFinite(parsed)) {
          throw new Error(`Invalid float for ${stageLabel(stageId)}.${key}`);
        }
        params[key] = parsed;
        return;
      }

      if (type === "json" || type === "json_array") {
        let parsed;
        try {
          parsed = JSON.parse(currentRaw);
        } catch {
          throw new Error(`Invalid JSON for ${stageLabel(stageId)}.${key}`);
        }
        if (type === "json_array" && !Array.isArray(parsed)) {
          throw new Error(`Expected JSON array for ${stageLabel(stageId)}.${key}`);
        }
        const validationError = validateJsonParam(stageId, key, parsed);
        if (validationError) {
          throw new Error(validationError);
        }
        params[key] = parsed;
        return;
      }

      params[key] = currentRaw;
    });

    if (Object.keys(params).length) {
      out[stageId] = params;
    }
  });

  return out;
}

function getSelectedStageIds() {
  return STAGE_ORDER.filter((stageId) => {
    const checkbox = stageCheckboxes.find((node) => node.value === stageId);
    return checkbox && checkbox.checked;
  });
}

function stagePresetStorageKey(stageId) {
  return `v2-stage-params-preset-${stageId}`;
}

function priorStagePresetStorageKey(stageId) {
  return `stage-params-preset-${stageId}`;
}

function legacyStagePresetStorageKey(stageId) {
  return `playlist_stage_params_preset_${stageId}_v1`;
}

function loadStageParamsFromPreset(stageId) {
  const raw =
    localStorage.getItem(stagePresetStorageKey(stageId)) ||
    localStorage.getItem(priorStagePresetStorageKey(stageId)) ||
    localStorage.getItem(legacyStagePresetStorageKey(stageId));
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return null;
    }
    const cleaned = Object.fromEntries(Object.entries(parsed).filter(([key]) => Boolean(key)));
    return Object.keys(cleaned).length ? cleaned : null;
  } catch {
    return null;
  }
}

function buildRunPayload() {
  const selectedStageIds = getSelectedStageIds();
  const inlineParams = collectInlineStageParams();
  const stageParams = {};

  selectedStageIds.forEach((stageId) => {
    const preset = loadStageParamsFromPreset(stageId) || {};
    const overrides = inlineParams[stageId] || {};
    const merged = { ...preset, ...overrides };
    if (Object.keys(merged).length) {
      stageParams[stageId] = merged;
    }
  });

  const payload = {
    trigger: "website_run_page",
    stage_ids: selectedStageIds
  };
  if (Object.keys(stageParams).length) {
    payload.stage_params = stageParams;
  }
  return payload;
}

function renderCompositionSummary() {
  let payload;
  try {
    payload = buildRunPayload();
  } catch (error) {
    compositionMessageNode.textContent = `Payload error: ${error.message}`;
    payloadPreviewNode.textContent = "Fix inline stage controls to continue.";
    return;
  }
  const selected = payload.stage_ids || [];
  if (!selected.length) {
    compositionMessageNode.textContent = "Select at least one stage to run.";
    payloadPreviewNode.textContent = JSON.stringify(payload, null, 2);
    return;
  }

  compositionMessageNode.textContent = `This run will execute: ${selected.map((s) => s.toUpperCase()).join(" -> ")}.`;
  payloadPreviewNode.textContent = JSON.stringify(payload, null, 2);
}

function applyAvailableStages(availableStageIds) {
  if (!Array.isArray(availableStageIds) || !availableStageIds.length) {
    renderInlineStageControls(STAGE_ORDER);
    renderCompositionSummary();
    return;
  }

  stageCheckboxes.forEach((checkbox) => {
    const enabled = availableStageIds.includes(checkbox.value);
    checkbox.disabled = !enabled;
    if (!enabled) {
      checkbox.checked = false;
    }
  });

  renderInlineStageControls(availableStageIds);
  renderCompositionSummary();
}

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
  if (apiFetchJson) {
    return apiFetchJson(path, options, {
      networkMessage: "Local API is unreachable. Start via setup/start_website.cmd and refresh this page."
    });
  }

  const response = await fetch(path, options);
  if (!response.ok) {
    const raw = await response.text();
    throw new Error(raw || `Request failed for ${path}`);
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
      <td>${escapeHtml(stage.label || "-")}</td>
      <td>${escapeHtml(stage.status || "-")}</td>
      <td>${escapeHtml(formatDateTimeDisplay(stage.started_at_utc))}</td>
      <td>${escapeHtml(formatDateTimeDisplay(stage.completed_at_utc))}</td>
      <td>${stage.exit_code === null || stage.exit_code === undefined ? "-" : escapeHtml(stage.exit_code)}</td>
      <td>${escapeHtml(stage.current_message || "-")}</td>
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
      <p><strong>${escapeHtml(key)}</strong> (${escapeHtml(status)})</p>
      <p class="track-meta">Path: ${escapeHtml(path)}</p>
      <p class="track-meta">Updated: ${escapeHtml(mtime)}</p>
      <p class="track-meta">Size: ${escapeHtml(size)}</p>
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
    renderCompositionSummary();
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
  applyAvailableStages(run.available_stage_ids || []);

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
    stopPolling();
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
    const payload = buildRunPayload();
    if (!Array.isArray(payload.stage_ids) || !payload.stage_ids.length) {
      messageNode.textContent = "Select at least one stage before starting a run.";
      return;
    }

    lastLogIndex = 0;
    allLogs = [];
    logNode.textContent = "No logs yet.";
    const snapshot = await fetchJson(API_PIPELINE_START, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
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
  stageCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", renderCompositionSummary);
  });
}

(async function init() {
  wireEvents();
  renderInlineStageControls(STAGE_ORDER);
  renderCompositionSummary();
  await refreshStatus();
})();
