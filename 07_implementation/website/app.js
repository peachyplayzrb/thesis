const sourceBtns = Array.from(document.querySelectorAll(".source-btn:not([disabled])"));
const sourcePanels = Array.from(document.querySelectorAll(".source-panel"));
const endpointItems = Array.from(document.querySelectorAll(".endpoint-item"));
const endpointCbs = Array.from(document.querySelectorAll(".endpoint-cb"));
const useMaxToggles = Array.from(document.querySelectorAll(".use-max-toggle"));

const ingestBtn = document.getElementById("start-ingest-btn");
const importSummary = document.getElementById("import-summary");
const statusNode = document.getElementById("status");
const progressNode = document.getElementById("progress");
const progressStep = document.getElementById("progress-step");
const progressBar = document.getElementById("progress-bar");
const clearSavedSelectionBtn = document.getElementById("clear-saved-selection-btn");

const manualJsonFile = document.getElementById("manual-json-file");
const manualJsonPaste = document.getElementById("manual-json-paste");

const epCbTopTracks = document.getElementById("ep-cb-top-tracks");
const epCbSavedTracks = document.getElementById("ep-cb-saved-tracks");
const epCbPlaylists = document.getElementById("ep-cb-playlists");
const epCbRecentlyPlayed = document.getElementById("ep-cb-recently-played");

const epTtsEnabled = document.getElementById("ep-tts-enabled");
const epTtmEnabled = document.getElementById("ep-ttm-enabled");
const epTtlEnabled = document.getElementById("ep-ttl-enabled");
const epTtsLimit = document.getElementById("ep-tts-limit");
const epTtmLimit = document.getElementById("ep-ttm-limit");
const epTtlLimit = document.getElementById("ep-ttl-limit");

const epSavMaxItems = document.getElementById("ep-sav-max-items");
const epSavUseMax = document.getElementById("ep-sav-use-max");
const epPlMaxPlaylists = document.getElementById("ep-pl-max-playlists");
const epPlUseMax = document.getElementById("ep-pl-use-max");
const epPlMaxItems = document.getElementById("ep-pl-max-items");
const epPlItemsUseMax = document.getElementById("ep-pl-items-use-max");
const epRecMaxItems = document.getElementById("ep-rec-max-items");
const epRecUseMax = document.getElementById("ep-rec-use-max");

const exportStatusMessage = document.getElementById("export-status-message");
const exportRunIdNode = document.getElementById("export-run-id");
const exportGeneratedAtNode = document.getElementById("export-generated-at");
const exportCountTopNode = document.getElementById("export-count-top");
const exportCountSavedNode = document.getElementById("export-count-saved");
const exportCountPlaylistItemsNode = document.getElementById("export-count-playlist-items");
const exportCountCallsNode = document.getElementById("export-count-calls");
const refreshExportBtn = document.getElementById("refresh-export-btn");

const runStatusMessage = document.getElementById("run-status-message");
const runStateNode = document.getElementById("run-state");
const runStepNode = document.getElementById("run-step");
const runStartedAtNode = document.getElementById("run-started-at");
const runCompletedAtNode = document.getElementById("run-completed-at");
const runExitCodeNode = document.getElementById("run-exit-code");
const runLogCountNode = document.getElementById("run-log-count");
const runOauthBlock = document.getElementById("run-oauth-block");
const runOauthLink = document.getElementById("run-oauth-link");
const runLogNode = document.getElementById("run-log");
const refreshRunBtn = document.getElementById("refresh-run-btn");
const cancelRunBtn = document.getElementById("cancel-run-btn");

const IMPORT_GROUPS_KEY = "playlist_import_groups_v1";
const MANUAL_INPUT_KEY = "playlist_manual_input_v1";
const EXPORT_BASE = "../implementation_notes/ingestion/outputs/spotify_api_export";
const EXPORT_SUMMARY_PATH = `${EXPORT_BASE}/spotify_export_run_summary.json`;
const EXPORT_TOP_TRACKS_PATH = `${EXPORT_BASE}/spotify_top_tracks_flat.csv`;
const EXPORT_SAVED_TRACKS_PATH = `${EXPORT_BASE}/spotify_saved_tracks_flat.csv`;
const EXPORT_PLAYLIST_ITEMS_PATH = `${EXPORT_BASE}/spotify_playlist_items_flat.csv`;
const EXPORT_RECENTLY_PLAYED_PATH = `${EXPORT_BASE}/spotify_recently_played_flat.csv`;
const API_EXPORT_STATUS_PATH = "/api/spotify/export/status";
const API_EXPORT_START_PATH = "/api/spotify/export/start";
const API_EXPORT_CANCEL_PATH = "/api/spotify/export/cancel";

let latestExportSnapshot = null;
let latestRunSnapshot = null;
let latestRunLogIndex = 0;
let runLogEntries = [];
let runPollHandle = null;
let activeIngestionRequested = false;
let completionHandledKey = null;

function setStatus(type, message) {
  statusNode.classList.remove("error", "loading", "warning");
  if (type) statusNode.classList.add(type);
  statusNode.textContent = message;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function normalizeNumberInput(input) {
  const min = Number(input.min || 0);
  const max = input.max === "" ? Number.MAX_SAFE_INTEGER : Number(input.max);
  const raw = Number(input.value);
  const safe = Number.isFinite(raw) ? raw : min;
  input.value = String(clamp(safe, min, max));
}

function parseTargetInput(input, useMax) {
  if (useMax) return Number.MAX_SAFE_INTEGER;
  normalizeNumberInput(input);
  return Number(input.value);
}

function parseApiCapInput(input, useMax) {
  if (useMax) return null;
  normalizeNumberInput(input);
  return Number(input.value);
}

function formatTarget(value) {
  return value === Number.MAX_SAFE_INTEGER ? "max available" : String(value);
}

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) return "-";
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return isoValue;
  return date.toISOString().replace(".000", "");
}

function csvSplitLine(line) {
  const out = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      const isEscaped = inQuotes && line[i + 1] === '"';
      if (isEscaped) {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (ch === "," && !inQuotes) {
      out.push(current);
      current = "";
      continue;
    }

    current += ch;
  }

  out.push(current);
  return out;
}

function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (!lines.length) return [];

  const headers = csvSplitLine(lines[0]).map((header) => header.trim());
  return lines.slice(1).map((line) => {
    const cells = csvSplitLine(line);
    const row = {};
    headers.forEach((header, index) => {
      row[header] = (cells[index] || "").trim();
    });
    return row;
  });
}

async function fetchJson(path, options = undefined) {
  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    if (String(path).startsWith("/api/")) {
      throw new Error("Local ingestion API is unreachable. Start the website via setup/start_website.cmd and refresh this page.");
    }
    throw error;
  }

  if (!response.ok) {
    let message = `Unable to load ${path}`;
    try {
      const payload = await response.json();
      if (payload && payload.error) {
        message = payload.error;
      }
    } catch {
      const text = await response.text();
      if (text) {
        message = text;
      }
    }
    throw new Error(message);
  }
  return response.json();
}

async function fetchCsvRows(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Unable to load ${path}`);
  }
  return parseCsv(await response.text());
}

function renderExportStatus(snapshot, messageType = "") {
  if (!exportStatusMessage) return;

  exportStatusMessage.classList.remove("warning", "error");
  if (messageType === "warning" || messageType === "error") {
    exportStatusMessage.classList.add(messageType);
  }

  if (!snapshot) {
    exportStatusMessage.textContent = "No Spotify export artifacts found yet. Start a run from this page to generate them.";
    if (exportRunIdNode) exportRunIdNode.textContent = "-";
    if (exportGeneratedAtNode) exportGeneratedAtNode.textContent = "-";
    if (exportCountTopNode) exportCountTopNode.textContent = "-";
    if (exportCountSavedNode) exportCountSavedNode.textContent = "-";
    if (exportCountPlaylistItemsNode) exportCountPlaylistItemsNode.textContent = "-";
    if (exportCountCallsNode) exportCountCallsNode.textContent = "-";
    return;
  }

  const counts = snapshot.summary && snapshot.summary.counts ? snapshot.summary.counts : {};
  exportStatusMessage.textContent = "Latest successful export artifacts loaded.";
  if (exportRunIdNode) exportRunIdNode.textContent = snapshot.summary.run_id || "-";
  if (exportGeneratedAtNode) exportGeneratedAtNode.textContent = formatDateTimeDisplay(snapshot.summary.generated_at_utc);
  if (exportCountTopNode) {
    const short = counts.top_tracks_short_term || 0;
    const medium = counts.top_tracks_medium_term || 0;
    const long = counts.top_tracks_long_term || 0;
    exportCountTopNode.textContent = `${short}/${medium}/${long}`;
  }
  if (exportCountSavedNode) exportCountSavedNode.textContent = String(counts.saved_tracks || 0);
  if (exportCountPlaylistItemsNode) exportCountPlaylistItemsNode.textContent = String(counts.playlist_items || 0);
  if (exportCountCallsNode) exportCountCallsNode.textContent = String(counts.api_calls_logged || 0);
}

async function loadLatestExportSnapshot() {
  const [summaryResult, topResult, savedResult, playlistsResult, recentResult] = await Promise.allSettled([
    fetchJson(EXPORT_SUMMARY_PATH),
    fetchCsvRows(EXPORT_TOP_TRACKS_PATH),
    fetchCsvRows(EXPORT_SAVED_TRACKS_PATH),
    fetchCsvRows(EXPORT_PLAYLIST_ITEMS_PATH),
    fetchCsvRows(EXPORT_RECENTLY_PLAYED_PATH)
  ]);

  if (summaryResult.status !== "fulfilled") {
    return null;
  }

  return {
    summary: summaryResult.value,
    topTracksRows: topResult.status === "fulfilled" ? topResult.value : [],
    savedTracksRows: savedResult.status === "fulfilled" ? savedResult.value : [],
    playlistItemsRows: playlistsResult.status === "fulfilled" ? playlistsResult.value : [],
    recentlyPlayedRows: recentResult.status === "fulfilled" ? recentResult.value : []
  };
}

async function refreshExportSnapshot() {
  if (exportStatusMessage) {
    exportStatusMessage.textContent = "Checking export artifacts...";
  }

  try {
    latestExportSnapshot = await loadLatestExportSnapshot();
    renderExportStatus(latestExportSnapshot, latestExportSnapshot ? "" : "warning");
  } catch {
    latestExportSnapshot = null;
    renderExportStatus(null, "warning");
  }

  updateIngestBtn();
}

function getUseMaxToggleForInput(inputId) {
  return useMaxToggles.find((toggle) => toggle.getAttribute("data-target") === inputId) || null;
}

function isUseMaxForInput(inputId) {
  const toggle = getUseMaxToggleForInput(inputId);
  return Boolean(toggle && toggle.checked);
}

function applyUseMaxToggle(toggle) {
  const targetId = toggle.getAttribute("data-target");
  const input = document.getElementById(targetId);
  if (!input) return;

  if (toggle.disabled) {
    input.disabled = true;
    return;
  }

  input.disabled = false;
  if (toggle.checked) {
    if (input.value !== "") {
      input.dataset.lastManualValue = input.value;
    }
    input.value = "";
    input.placeholder = "max";
    input.readOnly = true;
    input.classList.add("is-max");
    return;
  }

  input.readOnly = Boolean(toggle.disabled);
  input.placeholder = "";
  input.classList.remove("is-max");
  if (input.value === "") {
    input.value = input.dataset.lastManualValue || input.min || "1";
  }
  normalizeNumberInput(input);
}

function setTopTracksParentFromChildren() {
  epCbTopTracks.checked = epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked;
}

function setTopTrackChildrenFromParent() {
  if (epCbTopTracks.checked) {
    const anyEnabled = epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked;
    if (!anyEnabled) {
      epTtsEnabled.checked = true;
      epTtmEnabled.checked = true;
      epTtlEnabled.checked = true;
    }
    return;
  }
  epTtsEnabled.checked = false;
  epTtmEnabled.checked = false;
  epTtlEnabled.checked = false;
}

function updateControlEnabledState() {
  const topEnabled = epCbTopTracks.checked;
  epTtsEnabled.disabled = !topEnabled;
  epTtmEnabled.disabled = !topEnabled;
  epTtlEnabled.disabled = !topEnabled;

  const topRangeToggles = [
    getUseMaxToggleForInput("ep-tts-limit"),
    getUseMaxToggleForInput("ep-ttm-limit"),
    getUseMaxToggleForInput("ep-ttl-limit")
  ].filter(Boolean);

  [
    [epTtsEnabled, epTtsLimit, topRangeToggles[0]],
    [epTtmEnabled, epTtmLimit, topRangeToggles[1]],
    [epTtlEnabled, epTtlLimit, topRangeToggles[2]]
  ].forEach(([subCb, input, toggle]) => {
    const enabled = topEnabled && subCb.checked;
    if (toggle) {
      toggle.disabled = !enabled;
      applyUseMaxToggle(toggle);
    } else {
      input.disabled = !enabled;
    }
  });

  epSavUseMax.disabled = !epCbSavedTracks.checked;
  applyUseMaxToggle(epSavUseMax);

  epPlUseMax.disabled = !epCbPlaylists.checked;
  epPlItemsUseMax.disabled = !epCbPlaylists.checked;
  applyUseMaxToggle(epPlUseMax);
  applyUseMaxToggle(epPlItemsUseMax);

  epRecUseMax.disabled = !epCbRecentlyPlayed.checked;
  applyUseMaxToggle(epRecUseMax);
}

function getRecentlyPlayedTarget() {
  if (epRecUseMax.checked) {
    return Number(epRecMaxItems.max || 50);
  }
  return clamp(Number(epRecMaxItems.value), 1, 50);
}

function getActiveSourceId() {
  const active = sourceBtns.find((btn) => btn.classList.contains("active"));
  return active ? active.dataset.source : "spotify";
}

function hasManualInput() {
  const hasText = Boolean(manualJsonPaste && manualJsonPaste.value.trim());
  const hasFile = Boolean(manualJsonFile && manualJsonFile.files && manualJsonFile.files.length > 0);
  return hasText || hasFile;
}

function hasSavedImportSelection() {
  const raw = localStorage.getItem(IMPORT_GROUPS_KEY);
  if (!raw) {
    return false;
  }

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed.groups) && parsed.groups.length > 0;
  } catch {
    return false;
  }
}

function updateSavedSelectionButtonState() {
  if (!clearSavedSelectionBtn) {
    return;
  }
  clearSavedSelectionBtn.disabled = !hasSavedImportSelection();
}

async function readManualJsonInput() {
  const pasted = manualJsonPaste.value.trim();
  if (pasted) {
    return { raw: pasted, source: "paste" };
  }

  const file = manualJsonFile.files && manualJsonFile.files[0];
  if (!file) {
    return null;
  }

  return {
    raw: await file.text(),
    source: "file",
    fileName: file.name
  };
}

function switchSource(sourceId) {
  sourceBtns.forEach((btn) => {
    const active = btn.dataset.source === sourceId;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", String(active));
  });
  sourcePanels.forEach((panel) => {
    panel.hidden = panel.id !== `source-panel-${sourceId}`;
  });
  updateIngestBtn();
}

function openEndpoint(item) {
  const btn = item.querySelector(".endpoint-title-btn");
  const body = item.querySelector(".endpoint-body");
  btn.setAttribute("aria-expanded", "true");
  body.removeAttribute("hidden");
  item.classList.add("is-open");
}

function closeEndpoint(item) {
  const btn = item.querySelector(".endpoint-title-btn");
  const body = item.querySelector(".endpoint-body");
  btn.setAttribute("aria-expanded", "false");
  body.setAttribute("hidden", "");
  item.classList.remove("is-open");
}

function toggleEndpointOpen(item) {
  if (item.classList.contains("is-open")) {
    closeEndpoint(item);
  } else {
    openEndpoint(item);
  }
}

function isRunInProgress() {
  return Boolean(latestRunSnapshot && latestRunSnapshot.status === "running");
}

function updateRunActionButtons() {
  const running = isRunInProgress();
  if (cancelRunBtn) {
    cancelRunBtn.disabled = !running;
  }
}

function updateIngestBtn() {
  const activeSource = getActiveSourceId();
  if (activeSource === "manual") {
    ingestBtn.disabled = !hasManualInput();
    ingestBtn.textContent = "Ingest";
    updateImportSummary();
    return;
  }

  const anyChecked = endpointCbs.some((cb) => cb.checked);
  ingestBtn.disabled = activeSource !== "spotify" || !anyChecked || isRunInProgress();
  ingestBtn.textContent = isRunInProgress() ? "Ingesting..." : "Ingest";
  updateImportSummary();
  updateSavedSelectionButtonState();
}

function updateImportSummary() {
  const activeSource = getActiveSourceId();
  if (activeSource === "manual") {
    if (!hasManualInput()) {
      importSummary.textContent = "Manual mode: upload a JSON file or paste JSON to enable ingest.";
      return;
    }

    const file = manualJsonFile.files && manualJsonFile.files[0];
    const textLength = manualJsonPaste.value.trim().length;
    if (textLength > 0) {
      importSummary.textContent = `Manual mode: JSON text ready (${textLength} chars).`;
      return;
    }

    importSummary.textContent = `Manual mode: JSON file ready (${file ? file.name : "file selected"}).`;
    return;
  }

  const checked = endpointCbs.filter((cb) => cb.checked);
  if (!checked.length) {
    importSummary.textContent = "Select at least one endpoint to enable ingestion.";
    return;
  }

  const parts = [];
  if (epCbTopTracks.checked) {
    const ranges = [];
    if (epTtsEnabled.checked) ranges.push(`4 weeks (${formatTarget(parseTargetInput(epTtsLimit, isUseMaxForInput("ep-tts-limit")))})`);
    if (epTtmEnabled.checked) ranges.push(`6 months (${formatTarget(parseTargetInput(epTtmLimit, isUseMaxForInput("ep-ttm-limit")))})`);
    if (epTtlEnabled.checked) ranges.push(`1 year (${formatTarget(parseTargetInput(epTtlLimit, isUseMaxForInput("ep-ttl-limit")))})`);
    parts.push(`Top Tracks: ${ranges.join(", ")}`);
  }
  if (epCbSavedTracks.checked) {
    parts.push(`Saved Tracks: ${formatTarget(parseTargetInput(epSavMaxItems, epSavUseMax.checked))}`);
  }
  if (epCbPlaylists.checked) {
    parts.push(`Playlists: ${formatTarget(parseTargetInput(epPlMaxPlaylists, epPlUseMax.checked))} playlists, ${formatTarget(parseTargetInput(epPlMaxItems, epPlItemsUseMax.checked))} items each`);
  }
  if (epCbRecentlyPlayed.checked) {
    parts.push(`Recently Played: ${epRecUseMax.checked ? "max" : getRecentlyPlayedTarget()}`);
  }
  importSummary.textContent = `Selected for live ingest: ${parts.join(" | ")}`;
}

function buildImportGroupsFromExport(snapshot) {
  const groups = [];

  if (epCbTopTracks.checked) {
    const tracks = [];
    const topRanges = [
      { enabled: epTtsEnabled.checked, timeRange: "short_term", label: "Last 4 weeks", target: parseTargetInput(epTtsLimit, isUseMaxForInput("ep-tts-limit")) },
      { enabled: epTtmEnabled.checked, timeRange: "medium_term", label: "Last 6 months", target: parseTargetInput(epTtmLimit, isUseMaxForInput("ep-ttm-limit")) },
      { enabled: epTtlEnabled.checked, timeRange: "long_term", label: "Last year", target: parseTargetInput(epTtlLimit, isUseMaxForInput("ep-ttl-limit")) }
    ].filter((range) => range.enabled);

    topRanges.forEach((range) => {
      const rowsForRange = snapshot.topTracksRows
        .filter((row) => row.time_range === range.timeRange && row.track_name)
        .slice(0, range.target === Number.MAX_SAFE_INTEGER ? undefined : range.target);
      rowsForRange.forEach((row, index) => {
        tracks.push({
          id: row.track_id || `top_${range.timeRange}_${index + 1}`,
          title: row.track_name || "Untitled",
          artist: row.artist_names || "Unknown artist",
          source_key: `top_tracks_${range.timeRange}`
        });
      });
    });

    if (tracks.length) {
      const selectedRanges = [];
      if (epTtsEnabled.checked) selectedRanges.push("4 weeks");
      if (epTtmEnabled.checked) selectedRanges.push("6 months");
      if (epTtlEnabled.checked) selectedRanges.push("1 year");
      groups.push({
        key: "get_top_tracks",
        label: "GET /me/top/tracks",
        description: `Top tracks from the live ingestion run (${selectedRanges.join(", ")}).`,
        tracks
      });
    }
  }

  if (epCbSavedTracks.checked) {
    const maxItems = parseTargetInput(epSavMaxItems, epSavUseMax.checked);
    const rows = snapshot.savedTracksRows
      .filter((row) => row.track_name)
      .slice(0, maxItems === Number.MAX_SAFE_INTEGER ? undefined : maxItems);
    const tracks = rows.map((row, index) => ({
      id: row.track_id || `saved_${index + 1}`,
      title: row.track_name || "Untitled",
      artist: row.artist_names || "Unknown artist",
      source_key: "saved_tracks"
    }));
    if (tracks.length) {
      groups.push({
        key: "get_saved_tracks",
        label: "GET /me/tracks",
        description: `Saved tracks imported from live run (target: ${formatTarget(maxItems)}).`,
        tracks
      });
    }
  }

  if (epCbPlaylists.checked) {
    const maxPlaylists = parseTargetInput(epPlMaxPlaylists, epPlUseMax.checked);
    const maxItems = parseTargetInput(epPlMaxItems, epPlItemsUseMax.checked);
    const playlistBuckets = new Map();
    snapshot.playlistItemsRows.forEach((row) => {
      const playlistId = row.playlist_id || "unknown_playlist";
      if (!playlistBuckets.has(playlistId)) {
        playlistBuckets.set(playlistId, []);
      }
      playlistBuckets.get(playlistId).push(row);
    });

    const selectedPlaylistIds = (maxPlaylists === Number.MAX_SAFE_INTEGER ? Array.from(playlistBuckets.keys()) : Array.from(playlistBuckets.keys()).slice(0, maxPlaylists));
    const tracks = [];
    selectedPlaylistIds.forEach((playlistId) => {
      const rows = playlistBuckets.get(playlistId) || [];
      const limitedRows = maxItems === Number.MAX_SAFE_INTEGER ? rows : rows.slice(0, maxItems);
      limitedRows.forEach((row, index) => {
        tracks.push({
          id: row.track_id || `${playlistId}_${index + 1}`,
          title: row.track_name || "Untitled",
          artist: row.artist_names || row.playlist_name || "Unknown artist",
          source_key: "current_user_playlist_items",
          playlist_id: row.playlist_id || playlistId,
          playlist_name: row.playlist_name || "Unknown Playlist",
          playlist_position: row.playlist_position || ""
        });
      });
    });

    if (tracks.length) {
      groups.push({
        key: "get_current_user_playlists_items",
        label: "GET /me/playlists + /playlists/{id}/items",
        description: `Playlist items imported from live run (playlists: ${formatTarget(maxPlaylists)}, items per playlist: ${formatTarget(maxItems)}).`,
        tracks
      });
    }
  }

  if (epCbRecentlyPlayed.checked) {
    const maxItems = epRecUseMax.checked ? Number(epRecMaxItems.max || 50) : getRecentlyPlayedTarget();
    const rows = snapshot.recentlyPlayedRows
      .filter((row) => row.track_name)
      .slice(0, maxItems);
    const tracks = rows.map((row, index) => ({
      id: row.track_id || `recent_${index + 1}`,
      title: row.track_name || "Untitled",
      artist: row.artist_names || "Unknown artist",
      source_key: "recently_played",
      played_at: row.played_at || ""
    }));
    if (tracks.length) {
      groups.push({
        key: "get_recently_played",
        label: "GET /me/player/recently-played",
        description: `Recently played tracks imported from live run (target: ${maxItems}).`,
        tracks
      });
    }
  }

  return groups;
}

function persistImportGroups(groups) {
  localStorage.setItem(IMPORT_GROUPS_KEY, JSON.stringify({
    created_at: new Date().toISOString(),
    run_id: latestExportSnapshot?.summary?.run_id || null,
    selection_summary: importSummary.textContent || "",
    groups
  }));
  updateSavedSelectionButtonState();
}

function clearSavedImportSelection() {
  localStorage.removeItem(IMPORT_GROUPS_KEY);
  setStatus("", "Saved import-page selection snapshot cleared.");
  updateSavedSelectionButtonState();
}

function getRunProgressPercent(run) {
  const map = {
    idle: 0,
    starting: 8,
    oauth: 15,
    auth: 15,
    profile: 22,
    top_tracks: 42,
    saved_tracks: 62,
    playlists: 74,
    playlist_items: 86,
    recently_played: 90,
    write: 97,
    cancelling: 99,
    completed: 100,
    failed: 100,
    blocked: 100,
    cancelled: 100
  };
  return map[run?.current_step] || map[run?.status] || 0;
}

function renderRunProgress(run) {
  if (!run || run.status === "idle") {
    progressStep.textContent = "Idle";
    progressBar.style.width = "0%";
    progressNode.classList.add("hidden");
    return;
  }

  progressNode.classList.remove("hidden");
  progressStep.textContent = run.current_message || run.current_step || run.status;
  progressBar.style.width = `${getRunProgressPercent(run)}%`;
}

function renderRunStatus(run) {
  if (!runStatusMessage) return;

  if (!run || run.status === "idle") {
    runStatusMessage.textContent = "No ingestion run started yet.";
    runStateNode.textContent = "idle";
    runStepNode.textContent = "-";
    runStartedAtNode.textContent = "-";
    runCompletedAtNode.textContent = "-";
    runExitCodeNode.textContent = "-";
    runLogCountNode.textContent = "0";
    runLogNode.textContent = "No logs yet.";
    runOauthBlock.classList.add("hidden");
    renderRunProgress(null);
    return;
  }

  runStatusMessage.textContent = run.current_message || "Live ingestion state updated.";
  runStateNode.textContent = run.status || "-";
  runStepNode.textContent = run.current_step || "-";
  runStartedAtNode.textContent = formatDateTimeDisplay(run.started_at_utc);
  runCompletedAtNode.textContent = formatDateTimeDisplay(run.completed_at_utc);
  runExitCodeNode.textContent = run.exit_code ?? "-";
  runLogCountNode.textContent = String(run.line_count || 0);
  runLogNode.textContent = runLogEntries.length
    ? runLogEntries.map((entry) => entry.line).join("\n")
    : "No logs yet.";
  runLogNode.scrollTop = runLogNode.scrollHeight;

  if (run.oauth_url) {
    runOauthBlock.classList.remove("hidden");
    runOauthLink.href = run.oauth_url;
  } else {
    runOauthBlock.classList.add("hidden");
  }

  renderRunProgress(run);
  updateRunActionButtons();
}

function buildSpotifyApiRequestFromForm() {
  return {
    spotify: {
      top_tracks: {
        enabled: epCbTopTracks.checked,
        ranges: {
          short_term: { enabled: epTtsEnabled.checked, limit: parseApiCapInput(epTtsLimit, isUseMaxForInput("ep-tts-limit")) },
          medium_term: { enabled: epTtmEnabled.checked, limit: parseApiCapInput(epTtmLimit, isUseMaxForInput("ep-ttm-limit")) },
          long_term: { enabled: epTtlEnabled.checked, limit: parseApiCapInput(epTtlLimit, isUseMaxForInput("ep-ttl-limit")) }
        }
      },
      saved_tracks: {
        enabled: epCbSavedTracks.checked,
        max_items: parseApiCapInput(epSavMaxItems, epSavUseMax.checked)
      },
      playlists: {
        enabled: epCbPlaylists.checked,
        max_playlists: parseApiCapInput(epPlMaxPlaylists, epPlUseMax.checked),
        max_items_per_playlist: parseApiCapInput(epPlMaxItems, epPlItemsUseMax.checked)
      },
      recently_played: {
        enabled: epCbRecentlyPlayed.checked,
        limit: epRecUseMax.checked ? Number(epRecMaxItems.max || 50) : getRecentlyPlayedTarget()
      }
    }
  };
}

function validateSpotifySelection() {
  if (!endpointCbs.some((cb) => cb.checked)) {
    return "Please select at least one endpoint.";
  }
  if (epCbTopTracks.checked && !(epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked)) {
    return "Top Tracks is enabled but no time ranges are selected.";
  }
  return "";
}

function stopRunPolling() {
  if (runPollHandle) {
    clearTimeout(runPollHandle);
    runPollHandle = null;
  }
}

function scheduleRunPolling() {
  stopRunPolling();
  runPollHandle = window.setTimeout(async () => {
    await refreshRunStatus(true);
  }, 1500);
}

async function refreshRunStatus(incremental = false) {
  try {
    const after = incremental ? latestRunLogIndex : 0;
    const payload = await fetchJson(`${API_EXPORT_STATUS_PATH}?after=${after}`);
    const run = payload.run || null;

    if (!incremental) {
      runLogEntries = [];
      latestRunLogIndex = 0;
    }

    if (run && Array.isArray(run.logs) && run.logs.length) {
      run.logs.forEach((entry) => runLogEntries.push(entry));
      latestRunLogIndex = run.logs[run.logs.length - 1].index;
    }

    latestRunSnapshot = run ? { ...run, logs: runLogEntries.slice() } : null;
    renderRunStatus(latestRunSnapshot);
    updateIngestBtn();
    updateRunActionButtons();

    if (latestRunSnapshot && latestRunSnapshot.status === "running") {
      scheduleRunPolling();
    } else {
      stopRunPolling();
      await finalizeCompletedRun();
    }
  } catch (error) {
    stopRunPolling();
    runStatusMessage.textContent = `Unable to read live run status: ${error.message}`;
    setStatus("error", error.message || "Unable to read live run status.");
    updateRunActionButtons();
  }
}

async function finalizeCompletedRun() {
  if (!activeIngestionRequested || !latestRunSnapshot) {
    return;
  }

  const runKey = latestRunSnapshot.summary?.run_id || `${latestRunSnapshot.completed_at_utc || ""}:${latestRunSnapshot.exit_code}`;
  if (completionHandledKey === runKey) {
    return;
  }

  if (latestRunSnapshot.status === "completed") {
    await refreshExportSnapshot();
    const groups = latestExportSnapshot
      ? buildImportGroupsFromExport(latestExportSnapshot).filter((group) => group.tracks.length > 0)
      : [];

    if (!groups.length) {
      setStatus("warning", "Ingestion finished, but no rows matched your selected endpoints/options.");
    } else {
      persistImportGroups(groups);
      const labels = groups.map((group) => `${group.label} (${group.tracks.length})`);
      setStatus("", `Spotify ingestion finished. Imported ${groups.length} endpoint group${groups.length !== 1 ? "s" : ""}: ${labels.join("; ")}.`);
    }
  } else if (latestRunSnapshot.status === "failed") {
    setStatus("error", `Spotify ingestion failed. See live run log for details.${latestRunSnapshot.oauth_url ? " Authorization may still be required." : ""}`);
  } else if (latestRunSnapshot.status === "cancelled") {
    setStatus("warning", "Spotify ingestion was cancelled before completion.");
  }

  activeIngestionRequested = false;
  completionHandledKey = runKey;
  updateIngestBtn();
  updateRunActionButtons();
}

async function startSpotifyIngestion() {
  const validationMessage = validateSpotifySelection();
  if (validationMessage) {
    setStatus("error", validationMessage);
    return;
  }

  const requestPayload = buildSpotifyApiRequestFromForm();
  activeIngestionRequested = true;
  completionHandledKey = null;
  runLogEntries = [];
  latestRunLogIndex = 0;
  latestRunSnapshot = {
    status: "running",
    current_step: "starting",
    current_message: "Starting Spotify ingestion run...",
    started_at_utc: new Date().toISOString(),
    completed_at_utc: null,
    exit_code: null,
    oauth_url: null,
    line_count: 0
  };
  renderRunStatus(latestRunSnapshot);
  updateIngestBtn();
  updateRunActionButtons();
  setStatus("loading", "Starting Spotify ingestion run...");

  try {
    await fetchJson(API_EXPORT_START_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload)
    });
    await refreshRunStatus(false);
  } catch (error) {
    activeIngestionRequested = false;
    setStatus("error", error.message || "Unable to start Spotify ingestion.");
    updateIngestBtn();
  }
}

async function cancelSpotifyIngestion() {
  if (!isRunInProgress()) {
    setStatus("warning", "No active ingestion run to cancel.");
    return;
  }

  if (cancelRunBtn) {
    cancelRunBtn.disabled = true;
  }
  setStatus("warning", "Sending cancellation request...");

  try {
    await fetchJson(API_EXPORT_CANCEL_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}"
    });
    await refreshRunStatus(false);
    setStatus("warning", "Cancellation requested. Waiting for run to stop...");
  } catch (error) {
    setStatus("error", error.message || "Unable to cancel Spotify ingestion.");
    updateRunActionButtons();
  }
}

async function handleIngest() {
  const activeSource = getActiveSourceId();
  if (activeSource === "manual") {
    if (!hasManualInput()) {
      setStatus("error", "Manual mode requires a JSON file or pasted JSON text.");
      return;
    }

    ingestBtn.disabled = true;
    ingestBtn.textContent = "Saving...";
    progressNode.classList.remove("hidden");
    progressStep.textContent = "Reading manual input...";
    progressBar.style.width = "35%";
    setStatus("loading", "Validating manual JSON input...");

    try {
      const inputPayload = await readManualJsonInput();
      if (!inputPayload || !inputPayload.raw.trim()) {
        throw new Error("Manual input is empty.");
      }

      const parsed = JSON.parse(inputPayload.raw);
      progressStep.textContent = "Saving manual input...";
      progressBar.style.width = "75%";

      localStorage.setItem(MANUAL_INPUT_KEY, JSON.stringify({
        created_at: new Date().toISOString(),
        format: "json",
        source: inputPayload.source,
        file_name: inputPayload.fileName || null,
        data: parsed
      }));

      progressStep.textContent = "Done";
      progressBar.style.width = "100%";
      await sleep(180);
      setStatus("", `Manual JSON saved from ${inputPayload.source}.`);
    } catch (error) {
      setStatus("error", `Invalid JSON: ${error.message || "Unable to parse input."}`);
    } finally {
      ingestBtn.textContent = "Ingest";
      progressStep.textContent = "Idle";
      progressBar.style.width = "0%";
      updateIngestBtn();
    }
    return;
  }

  await startSpotifyIngestion();
}

function init() {
  sourceBtns.forEach((btn) => {
    btn.addEventListener("click", () => switchSource(btn.dataset.source));
  });

  if (manualJsonPaste) {
    manualJsonPaste.addEventListener("input", () => updateIngestBtn());
  }
  if (manualJsonFile) {
    manualJsonFile.addEventListener("change", () => updateIngestBtn());
  }

  endpointItems.forEach((item) => {
    const titleBtn = item.querySelector(".endpoint-title-btn");
    titleBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleEndpointOpen(item);
    });

    const cb = item.querySelector(".endpoint-cb");
    cb.addEventListener("change", () => {
      if (cb === epCbTopTracks) {
        setTopTrackChildrenFromParent();
      }
      if (cb.checked && !item.classList.contains("is-open")) {
        openEndpoint(item);
      }
      updateControlEnabledState();
      updateIngestBtn();
    });
  });

  useMaxToggles.forEach((toggle) => {
    applyUseMaxToggle(toggle);
    toggle.addEventListener("change", () => {
      applyUseMaxToggle(toggle);
      updateImportSummary();
    });
  });

  [epTtsEnabled, epTtmEnabled, epTtlEnabled].forEach((cb) => {
    if (!cb) return;
    cb.addEventListener("change", () => {
      setTopTracksParentFromChildren();
      updateControlEnabledState();
      updateIngestBtn();
    });
  });

  [epTtsLimit, epTtmLimit, epTtlLimit, epSavMaxItems, epPlMaxPlaylists, epPlMaxItems, epRecMaxItems].forEach((input) => {
    if (!input) return;
    input.addEventListener("input", () => {
      normalizeNumberInput(input);
      updateImportSummary();
    });
    input.addEventListener("blur", () => {
      normalizeNumberInput(input);
      updateImportSummary();
    });
  });

  ingestBtn.addEventListener("click", handleIngest);
  if (refreshExportBtn) {
    refreshExportBtn.addEventListener("click", () => {
      void refreshExportSnapshot();
    });
  }
  if (refreshRunBtn) {
    refreshRunBtn.addEventListener("click", () => {
      void refreshRunStatus(false);
    });
  }
  if (clearSavedSelectionBtn) {
    clearSavedSelectionBtn.addEventListener("click", () => {
      clearSavedImportSelection();
    });
  }
  if (cancelRunBtn) {
    cancelRunBtn.addEventListener("click", () => {
      void cancelSpotifyIngestion();
    });
  }

  switchSource("spotify");
  setTopTracksParentFromChildren();
  updateControlEnabledState();
  updateIngestBtn();
  updateSavedSelectionButtonState();
  updateRunActionButtons();
  void refreshExportSnapshot();
  void refreshRunStatus(false);
}

init();