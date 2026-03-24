const stageRoot = document.querySelector("[data-stage-id]");
const stageId = stageRoot ? String(stageRoot.getAttribute("data-stage-id") || "").toLowerCase() : "";

const stageTitleNode = document.getElementById("stage-title");
const stageDescriptionNode = document.getElementById("stage-description");
const stageScriptNode = document.getElementById("stage-script-path");

const startBtn = document.getElementById("stage-start-btn");
const cancelBtn = document.getElementById("stage-cancel-btn");
const refreshBtn = document.getElementById("stage-refresh-btn");

const messageNode = document.getElementById("stage-message");
const runIdNode = document.getElementById("stage-run-id");
const runStatusNode = document.getElementById("stage-run-status");
const runCurrentNode = document.getElementById("stage-run-current");
const stageStatusNode = document.getElementById("stage-status");
const stageStartedNode = document.getElementById("stage-started");
const stageFinishedNode = document.getElementById("stage-finished");
const stageExitNode = document.getElementById("stage-exit");
const stageLogNode = document.getElementById("stage-log");
const artifactNode = document.getElementById("stage-artifacts");

const API_STAGE_CATALOG = "/api/pipeline/stages";
const API_RUN_START = "/api/pipeline/run/start";
const API_RUN_STATUS = "/api/pipeline/run/status";
const API_RUN_CANCEL = "/api/pipeline/run/cancel";

const STAGE_PARAMETER_DEFS = {
  bl004: [
    { key: "top_tag_limit", label: "Top tags limit", type: "int", min: 1, max: 100, step: 1, defaultValue: 10 },
    { key: "top_genre_limit", label: "Top genres limit", type: "int", min: 1, max: 100, step: 1, defaultValue: 10 },
    { key: "top_lead_genre_limit", label: "Top lead-genres limit", type: "int", min: 1, max: 100, step: 1, defaultValue: 10 },
    { key: "user_id", label: "User ID", type: "string", defaultValue: "21zsn42xecjhogne4kghyw5hq" }
  ],
  bl005: [
    { key: "semantic_strong_keep_score", label: "Semantic strong-keep score", type: "int", min: 0, max: 10, step: 1, defaultValue: 2 },
    { key: "semantic_min_keep_score", label: "Semantic minimum keep score", type: "int", min: 0, max: 10, step: 1, defaultValue: 1 },
    { key: "numeric_support_min_pass", label: "Numeric support minimum pass", type: "int", min: 0, max: 10, step: 1, defaultValue: 1 },
    { key: "profile_top_lead_genre_limit", label: "Top lead genres", type: "int", min: 1, max: 30, step: 1, defaultValue: 6 },
    { key: "profile_top_tag_limit", label: "Top tags", type: "int", min: 1, max: 50, step: 1, defaultValue: 10 },
    { key: "profile_top_genre_limit", label: "Top genres", type: "int", min: 1, max: 50, step: 1, defaultValue: 8 }
  ],
  bl006: [
    {
      key: "component_weights",
      label: "Component weights (JSON object)",
      type: "json",
      defaultValue: "{\n  \"genre\": 0.24,\n  \"tag\": 0.16,\n  \"artist_affinity\": 0.16,\n  \"tempo\": 0.08,\n  \"duration_ms\": 0.08,\n  \"key\": 0.04,\n  \"mode\": 0.04,\n  \"artist_popularity\": 0.08,\n  \"track_popularity\": 0.08,\n  \"spotify_popularity\": 0.04\n}"
    },
    {
      key: "numeric_thresholds",
      label: "Numeric thresholds (JSON object)",
      type: "json",
      defaultValue: "{\n  \"tempo\": 20.0,\n  \"duration_ms\": 60000.0,\n  \"key\": 3.0,\n  \"mode\": 1.0\n}"
    }
  ],
  bl007: [
    { key: "target_size", label: "Target playlist size", type: "int", min: 1, max: 100, step: 1, defaultValue: 10 },
    { key: "min_score_threshold", label: "Minimum score threshold", type: "float", min: 0, max: 1, step: 0.01, defaultValue: 0.35 },
    { key: "max_per_genre", label: "Max tracks per genre", type: "int", min: 1, max: 20, step: 1, defaultValue: 4 },
    { key: "max_consecutive", label: "Max consecutive same-genre tracks", type: "int", min: 1, max: 10, step: 1, defaultValue: 2 }
  ],
  bl008: [
    { key: "top_contributor_limit", label: "Top contributors per track", type: "int", min: 1, max: 20, step: 1, defaultValue: 3 }
  ],
  bl009: [
    { key: "diagnostic_sample_limit", label: "Diagnostic sample limit", type: "int", min: 1, max: 50, step: 1, defaultValue: 5 }
  ]
};

let pollHandle = null;
let logCursor = 0;
let stageLogs = [];
let stageParamInputs = [];
let stageParamMessageNode = null;

function getStageParameterDefs() {
  return Array.isArray(STAGE_PARAMETER_DEFS[stageId]) ? STAGE_PARAMETER_DEFS[stageId] : [];
}

function stagePresetStorageKey() {
  return `playlist_stage_params_preset_${stageId}_v1`;
}

function setStageParamMessage(text) {
  if (stageParamMessageNode) {
    stageParamMessageNode.textContent = text;
  }
}

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) return "-";
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return isoValue;
  return date.toISOString().replace(".000", "");
}

async function fetchJson(path, options = undefined) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    const raw = await response.text();
    if (raw) {
      try {
        const payload = JSON.parse(raw);
        if (payload && payload.error) {
          message = payload.error;
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

function stageHasParameterControls() {
  return getStageParameterDefs().length > 0;
}

function buildStageParameterControls() {
  if (!stageRoot) return;
  if (!stageHasParameterControls()) return;

  const controlCard = stageRoot.querySelector("section.export-status-card[aria-live='polite']");
  if (!controlCard || !controlCard.parentElement) return;

  const defs = getStageParameterDefs();
  const card = document.createElement("section");
  card.className = "export-status-card";

  const title = document.createElement("div");
  title.className = "export-status-head";
  title.innerHTML = "<h3>Stage Parameters</h3>";
  card.appendChild(title);

  const hint = document.createElement("p");
  hint.className = "hint";
  hint.textContent = "These parameters apply to this stage run only.";
  card.appendChild(hint);

  const grid = document.createElement("div");
  grid.className = "row g-2";

  defs.forEach((def) => {
    const col = document.createElement("div");
    col.className = def.type === "json" ? "col-12" : "col-md-6";

    const label = document.createElement("label");
    label.className = "form-label";
    label.textContent = def.label;

    const inputId = `stage-param-${def.key}`;
    label.setAttribute("for", inputId);

    let input;
    if (def.type === "json") {
      input = document.createElement("textarea");
      input.rows = 7;
      input.className = "form-control run-config-textarea";
    } else if (def.type === "string") {
      input = document.createElement("input");
      input.type = "text";
      input.className = "form-control";
    } else {
      input = document.createElement("input");
      input.type = "number";
      input.className = "form-control";
      if (Number.isFinite(def.min)) input.min = String(def.min);
      if (Number.isFinite(def.max)) input.max = String(def.max);
      if (Number.isFinite(def.step)) input.step = String(def.step);
    }

    input.id = inputId;
    input.value = String(def.defaultValue ?? "");
    input.dataset.paramKey = def.key;
    input.dataset.paramType = def.type;
    input.dataset.defaultValue = String(def.defaultValue ?? "");
    col.appendChild(label);
    col.appendChild(input);

    grid.appendChild(col);
    stageParamInputs.push(input);
  });

  card.appendChild(grid);

  const actions = document.createElement("div");
  actions.className = "profile-action-row";

  const resetBtn = document.createElement("button");
  resetBtn.type = "button";
  resetBtn.className = "secondary-btn";
  resetBtn.textContent = "Reset Defaults";
  resetBtn.addEventListener("click", () => {
    stageParamInputs.forEach((input) => {
      input.value = String(input.dataset.defaultValue || "");
    });
    setStageParamMessage("Stage parameter values reset to defaults.");
  });

  const savePresetBtn = document.createElement("button");
  savePresetBtn.type = "button";
  savePresetBtn.className = "secondary-btn";
  savePresetBtn.textContent = "Save Preset";
  savePresetBtn.addEventListener("click", () => {
    try {
      const preset = {};
      stageParamInputs.forEach((input) => {
        const key = String(input.dataset.paramKey || "");
        if (key) {
          preset[key] = String(input.value || "");
        }
      });
      localStorage.setItem(stagePresetStorageKey(), JSON.stringify(preset));
      setStageParamMessage("Preset saved for this stage in your browser.");
    } catch {
      setStageParamMessage("Unable to save preset in this browser session.");
    }
  });

  const loadPresetBtn = document.createElement("button");
  loadPresetBtn.type = "button";
  loadPresetBtn.className = "secondary-btn";
  loadPresetBtn.textContent = "Load Preset";
  loadPresetBtn.addEventListener("click", () => {
    try {
      const raw = localStorage.getItem(stagePresetStorageKey());
      if (!raw) {
        setStageParamMessage("No saved preset found for this stage.");
        return;
      }
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        setStageParamMessage("Saved preset is invalid. Save a new preset.");
        return;
      }
      let loadedCount = 0;
      stageParamInputs.forEach((input) => {
        const key = String(input.dataset.paramKey || "");
        if (Object.prototype.hasOwnProperty.call(parsed, key)) {
          input.value = String(parsed[key] ?? "");
          loadedCount += 1;
        }
      });
      setStageParamMessage(loadedCount ? `Loaded preset values for ${loadedCount} parameter(s).` : "Preset did not match current parameter fields.");
    } catch {
      setStageParamMessage("Unable to load preset. Save a new preset.");
    }
  });

  actions.appendChild(resetBtn);
  actions.appendChild(savePresetBtn);
  actions.appendChild(loadPresetBtn);
  card.appendChild(actions);

  stageParamMessageNode = document.createElement("p");
  stageParamMessageNode.className = "hint";
  stageParamMessageNode.textContent = "Parameter values will be sent with the next run.";
  card.appendChild(stageParamMessageNode);

  controlCard.insertAdjacentElement("afterend", card);

  try {
    const raw = localStorage.getItem(stagePresetStorageKey());
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        let loaded = 0;
        stageParamInputs.forEach((input) => {
          const key = String(input.dataset.paramKey || "");
          if (Object.prototype.hasOwnProperty.call(parsed, key)) {
            input.value = String(parsed[key] ?? "");
            loaded += 1;
          }
        });
        if (loaded) {
          setStageParamMessage(`Loaded saved preset values for ${loaded} parameter(s).`);
        }
      }
    }
  } catch {
    setStageParamMessage("Parameter values will be sent with the next run.");
  }
}

function collectStageParams() {
  const params = {};
  if (!stageHasParameterControls()) {
    return params;
  }

  for (const input of stageParamInputs) {
    const key = String(input.dataset.paramKey || "");
    const type = String(input.dataset.paramType || "");
    const raw = String(input.value || "").trim();

    if (!key || !raw) {
      continue;
    }

    if (type === "int") {
      const value = Number.parseInt(raw, 10);
      if (!Number.isFinite(value)) {
        throw new Error(`Invalid integer for ${key}.`);
      }
      params[key] = value;
      continue;
    }

    if (type === "float") {
      const value = Number.parseFloat(raw);
      if (!Number.isFinite(value)) {
        throw new Error(`Invalid number for ${key}.`);
      }
      params[key] = value;
      continue;
    }

    if (type === "json") {
      let payload;
      try {
        payload = JSON.parse(raw);
      } catch {
        throw new Error(`Invalid JSON for ${key}.`);
      }
      if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
        throw new Error(`Expected a JSON object for ${key}.`);
      }
      params[key] = payload;
      continue;
    }

    if (type === "string") {
      params[key] = raw;
      continue;
    }
  }

  return params;
}

function renderArtifacts(artifactSummary) {
  if (!artifactSummary || !Object.keys(artifactSummary).length) {
    artifactNode.innerHTML = '<p class="hint">No artifact summary available yet.</p>';
    return;
  }

  artifactNode.innerHTML = Object.entries(artifactSummary).map(([key, info]) => {
    const ready = info && !info.missing;
    return `<div class="artifact-item">
      <p><strong>${key}</strong> (${ready ? "ready" : "missing"})</p>
      <p class="track-meta">Path: ${info.path || "-"}</p>
      <p class="track-meta">Updated: ${formatDateTimeDisplay(info.mtime_utc)}</p>
      <p class="track-meta">Hash: ${info.sha256 || "-"}</p>
    </div>`;
  }).join("");
}

function renderSnapshot(snapshot) {
  const run = snapshot && snapshot.run ? snapshot.run : null;
  if (!run) {
    messageNode.textContent = "No run data available.";
    return;
  }

  runIdNode.textContent = run.run_id || "-";
  runStatusNode.textContent = run.status || "idle";
  runCurrentNode.textContent = run.current_stage || "-";

  const stage = Array.isArray(run.stages) ? run.stages.find((item) => item.stage_id === stageId) : null;
  stageStatusNode.textContent = stage ? (stage.status || "-") : "not-selected";
  stageStartedNode.textContent = stage ? formatDateTimeDisplay(stage.started_at_utc) : "-";
  stageFinishedNode.textContent = stage ? formatDateTimeDisplay(stage.completed_at_utc) : "-";
  stageExitNode.textContent = stage && stage.exit_code !== null && stage.exit_code !== undefined ? String(stage.exit_code) : "-";

  const selectedIds = Array.isArray(run.selected_stage_ids) && run.selected_stage_ids.length
    ? run.selected_stage_ids
    : (Array.isArray(run.stages) ? run.stages.map((item) => item.stage_id).filter(Boolean) : []);
  const selectedLabel = selectedIds.length ? selectedIds.join(", ") : "full default chain";
  messageNode.textContent = `${run.current_message || "-"} Selected stages: ${selectedLabel}`;

  const incoming = Array.isArray(run.logs) ? run.logs : [];
  incoming.forEach((entry) => {
    if (entry.stage_id === stageId) {
      stageLogs.push(`${entry.index.toString().padStart(4, "0")} ${entry.timestamp_utc} ${entry.line}`);
    }
  });
  if (stageLogs.length > 800) {
    stageLogs = stageLogs.slice(-800);
  }
  stageLogNode.textContent = stageLogs.length ? stageLogs.join("\n") : "No stage logs yet.";

  if (incoming.length) {
    const maxIndex = incoming[incoming.length - 1].index;
    if (Number.isFinite(maxIndex)) {
      logCursor = maxIndex;
    }
  }

  renderArtifacts(run.artifact_summary || {});

  const isRunning = run.status === "running";
  startBtn.disabled = isRunning;
  cancelBtn.disabled = !isRunning;

  if (isRunning) {
    startPolling();
  } else {
    stopPolling();
  }
}

async function refreshStatus() {
  try {
    const snapshot = await fetchJson(`${API_RUN_STATUS}?after=${logCursor}`);
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

async function startStageRun() {
  messageNode.textContent = `Starting ${stageId.toUpperCase()}...`;
  try {
    const stageParams = collectStageParams();
    const keys = Object.keys(stageParams);
    setStageParamMessage(keys.length
      ? `Using ${keys.length} parameter override(s): ${keys.join(", ")}`
      : "Using default stage parameters.");

    logCursor = 0;
    stageLogs = [];
    stageLogNode.textContent = "No stage logs yet.";
    const body = {
      trigger: "stage_page",
      stage_ids: [stageId]
    };
    if (Object.keys(stageParams).length) {
      body.stage_params = { [stageId]: stageParams };
    }
    const snapshot = await fetchJson(API_RUN_START, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

async function cancelRun() {
  messageNode.textContent = "Cancelling active run...";
  try {
    const snapshot = await fetchJson(API_RUN_CANCEL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}"
    });
    renderSnapshot(snapshot);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
  }
}

async function loadStageMeta() {
  try {
    const catalog = await fetchJson(API_STAGE_CATALOG);
    const stage = Array.isArray(catalog.stages) ? catalog.stages.find((item) => item.stage_id === stageId) : null;
    if (stage) {
      stageTitleNode.textContent = stage.label;
      stageDescriptionNode.textContent = stage.description || "-";
      stageScriptNode.textContent = stage.script_path || "-";
    } else {
      stageTitleNode.textContent = stageId.toUpperCase();
      stageDescriptionNode.textContent = "Stage metadata unavailable.";
      stageScriptNode.textContent = "-";
    }
  } catch (error) {
    stageTitleNode.textContent = stageId.toUpperCase();
    stageDescriptionNode.textContent = String(error.message || error);
    stageScriptNode.textContent = "-";
  }
}

startBtn.addEventListener("click", startStageRun);
cancelBtn.addEventListener("click", cancelRun);
refreshBtn.addEventListener("click", refreshStatus);

(async function init() {
  buildStageParameterControls();
  await loadStageMeta();
  await refreshStatus();
})();
