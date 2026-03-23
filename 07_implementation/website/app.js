// ─── DOM refs ────────────────────────────────────────────────────────────────
const sourceBtns    = Array.from(document.querySelectorAll(".source-btn:not([disabled])"));
const sourcePanels  = Array.from(document.querySelectorAll(".source-panel"));
const endpointItems = Array.from(document.querySelectorAll(".endpoint-item"));
const endpointCbs   = Array.from(document.querySelectorAll(".endpoint-cb"));
const useMaxToggles = Array.from(document.querySelectorAll(".use-max-toggle"));

const ingestBtn     = document.getElementById("start-ingest-btn");
const importSummary = document.getElementById("import-summary");
const statusNode    = document.getElementById("status");
const progressNode  = document.getElementById("progress");
const progressStep  = document.getElementById("progress-step");
const progressBar   = document.getElementById("progress-bar");

// Manual input controls
const manualJsonFile  = document.getElementById("manual-json-file");
const manualJsonPaste = document.getElementById("manual-json-paste");

// Spotify endpoint inputs
const epCbTopTracks      = document.getElementById("ep-cb-top-tracks");
const epCbSavedTracks    = document.getElementById("ep-cb-saved-tracks");
const epCbPlaylists      = document.getElementById("ep-cb-playlists");
const epCbRecentlyPlayed = document.getElementById("ep-cb-recently-played");

const epTtsEnabled = document.getElementById("ep-tts-enabled");
const epTtmEnabled = document.getElementById("ep-ttm-enabled");
const epTtlEnabled = document.getElementById("ep-ttl-enabled");
const epTtsLimit   = document.getElementById("ep-tts-limit");
const epTtmLimit   = document.getElementById("ep-ttm-limit");
const epTtlLimit   = document.getElementById("ep-ttl-limit");

const epSavMaxItems    = document.getElementById("ep-sav-max-items");
const epSavUseMax      = document.getElementById("ep-sav-use-max");
const epPlMaxPlaylists = document.getElementById("ep-pl-max-playlists");
const epPlUseMax       = document.getElementById("ep-pl-use-max");
const epPlMaxItems     = document.getElementById("ep-pl-max-items");
const epPlItemsUseMax  = document.getElementById("ep-pl-items-use-max");
const epRecMaxItems    = document.getElementById("ep-rec-max-items");
const epRecUseMax      = document.getElementById("ep-rec-use-max");

const IMPORT_GROUPS_KEY = "playlist_import_groups_v1";
const MANUAL_INPUT_KEY = "playlist_manual_input_v1";

// ─── Utilities ───────────────────────────────────────────────────────────────
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

function formatTarget(value) {
  return value === Number.MAX_SAFE_INTEGER ? "max available" : String(value);
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
  const anyRangeEnabled = epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked;
  epCbTopTracks.checked = anyRangeEnabled;
}

function setTopTrackChildrenFromParent() {
  if (epCbTopTracks.checked) {
    const anyRangeEnabled = epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked;
    if (!anyRangeEnabled) {
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
  // Top tracks endpoint controls
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

  // Saved tracks endpoint controls
  const savedEnabled = epCbSavedTracks.checked;
  epSavUseMax.disabled = !savedEnabled;
  applyUseMaxToggle(epSavUseMax);

  // Playlists endpoint controls
  const playlistsEnabled = epCbPlaylists.checked;
  epPlUseMax.disabled = !playlistsEnabled;
  epPlItemsUseMax.disabled = !playlistsEnabled;
  applyUseMaxToggle(epPlUseMax);
  applyUseMaxToggle(epPlItemsUseMax);

  // Recently played endpoint controls
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

async function readManualJsonInput() {
  const pasted = manualJsonPaste.value.trim();
  if (pasted) {
    return {
      raw: pasted,
      source: "paste"
    };
  }

  const file = manualJsonFile.files && manualJsonFile.files[0];
  if (!file) {
    return null;
  }

  const raw = await file.text();
  return {
    raw,
    source: "file",
    fileName: file.name
  };
}

// ─── Source switching ─────────────────────────────────────────────────────────
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

// ─── Endpoint accordion ───────────────────────────────────────────────────────
function openEndpoint(item) {
  const btn  = item.querySelector(".endpoint-title-btn");
  const body = item.querySelector(".endpoint-body");
  btn.setAttribute("aria-expanded", "true");
  body.removeAttribute("hidden");
  item.classList.add("is-open");
}

function closeEndpoint(item) {
  const btn  = item.querySelector(".endpoint-title-btn");
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

// ─── Ingest button + summary ──────────────────────────────────────────────────
function updateIngestBtn() {
  const activeSource = getActiveSourceId();
  if (activeSource === "manual") {
    ingestBtn.disabled = !hasManualInput();
    updateImportSummary();
    return;
  }

  const anyChecked = endpointCbs.some((cb) => cb.checked);
  ingestBtn.disabled = activeSource !== "spotify" || !anyChecked;
  updateImportSummary();
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
  if (checked.length === 0) {
    importSummary.textContent = "Select at least one endpoint to enable ingestion.";
    return;
  }

  const parts = [];

  if (epCbTopTracks && epCbTopTracks.checked) {
    const ranges = [];
    if (epTtsEnabled.checked) {
      const shortTarget = parseTargetInput(epTtsLimit, isUseMaxForInput("ep-tts-limit"));
      ranges.push(`4 weeks (${formatTarget(shortTarget)})`);
    }
    if (epTtmEnabled.checked) {
      const mediumTarget = parseTargetInput(epTtmLimit, isUseMaxForInput("ep-ttm-limit"));
      ranges.push(`6 months (${formatTarget(mediumTarget)})`);
    }
    if (epTtlEnabled.checked) {
      const longTarget = parseTargetInput(epTtlLimit, isUseMaxForInput("ep-ttl-limit"));
      ranges.push(`1 year (${formatTarget(longTarget)})`);
    }
    parts.push("Top Tracks" + (ranges.length ? `: ${ranges.join(", ")}` : " (no ranges)"));
  }

  if (epCbSavedTracks && epCbSavedTracks.checked) {
    parts.push(`Saved Tracks: ${formatTarget(parseTargetInput(epSavMaxItems, epSavUseMax.checked))}`);
  }

  if (epCbPlaylists && epCbPlaylists.checked) {
    const pl = formatTarget(parseTargetInput(epPlMaxPlaylists, epPlUseMax.checked));
    const it = formatTarget(parseTargetInput(epPlMaxItems, epPlItemsUseMax.checked));
    parts.push(`Playlists: ${pl} playlists, ${it} items each`);
  }

  if (epCbRecentlyPlayed && epCbRecentlyPlayed.checked) {
    const recTarget = getRecentlyPlayedTarget();
    parts.push(`Recently Played: ${epRecUseMax.checked ? "max" : recTarget}`);
  }

  importSummary.textContent = `Selected: ${parts.join(" | ")}`;
}

// ─── Build / persist groups ───────────────────────────────────────────────────
function buildMockTracks(sourceKey, label, total, idPrefix) {
  const tracks = [];
  for (let i = 0; i < total; i += 1) {
    tracks.push({
      id: `${idPrefix}_${i + 1}`,
      title: `${label} ${i + 1}`,
      artist: `${sourceKey.replace(/_/g, " ")} artist ${(i % 30) + 1}`,
      source_key: sourceKey
    });
  }
  return tracks;
}

function buildPreviewTracks(sourceKey, label, targetCount, idPrefix) {
  const n = Math.min(12, targetCount === Number.MAX_SAFE_INTEGER ? 12 : targetCount);
  return buildMockTracks(sourceKey, label, n, idPrefix);
}

function buildImportGroups() {
  const groups = [];

  if (epCbTopTracks && epCbTopTracks.checked) {
    const tracks = [];
    if (epTtsEnabled.checked) {
      const shortTarget = parseTargetInput(epTtsLimit, isUseMaxForInput("ep-tts-limit"));
      tracks.push(...buildPreviewTracks("top_tracks_short", "Top Track (4 Weeks)", shortTarget, "tts"));
    }
    if (epTtmEnabled.checked) {
      const mediumTarget = parseTargetInput(epTtmLimit, isUseMaxForInput("ep-ttm-limit"));
      tracks.push(...buildPreviewTracks("top_tracks_medium", "Top Track (6 Months)", mediumTarget, "ttm"));
    }
    if (epTtlEnabled.checked) {
      const longTarget = parseTargetInput(epTtlLimit, isUseMaxForInput("ep-ttl-limit"));
      tracks.push(...buildPreviewTracks("top_tracks_long", "Top Track (1 Year)", longTarget, "ttl"));
    }
    if (tracks.length) {
      groups.push({
        key: "get_top_tracks",
        label: "GET /me/top/tracks",
        description: "Top tracks across selected time ranges",
        tracks
      });
    }
  }

  if (epCbSavedTracks && epCbSavedTracks.checked) {
    const maxItems = parseTargetInput(epSavMaxItems, epSavUseMax.checked);
    groups.push({
      key: "get_saved_tracks",
      label: "GET /me/tracks",
      description: `Saved tracks (target: ${formatTarget(maxItems)})`,
      tracks: buildPreviewTracks("saved_tracks", "Saved Track", maxItems, "sav")
    });
  }

  if (epCbPlaylists && epCbPlaylists.checked) {
    const maxPl = parseTargetInput(epPlMaxPlaylists, epPlUseMax.checked);
    const maxIt = parseTargetInput(epPlMaxItems, epPlItemsUseMax.checked);
    const total = maxPl === Number.MAX_SAFE_INTEGER || maxIt === Number.MAX_SAFE_INTEGER
      ? Number.MAX_SAFE_INTEGER
      : maxPl * maxIt;
    groups.push({
      key: "get_current_user_playlists_items",
      label: "GET /me/playlists + /playlists/{id}/items",
      description: `Playlists: ${formatTarget(maxPl)}, items per playlist: ${formatTarget(maxIt)}`,
      tracks: buildPreviewTracks("current_user_playlist_items", "Playlist Item", total, "pli")
    });
  }

  if (epCbRecentlyPlayed && epCbRecentlyPlayed.checked) {
    const maxItems = getRecentlyPlayedTarget();
    groups.push({
      key: "get_recently_played",
      label: "GET /me/player/recently-played",
      description: `Recently played (target: ${maxItems})`,
      tracks: buildPreviewTracks("recently_played", "Recently Played Track", maxItems, "rec")
    });
  }

  return groups;
}

function persistImportGroups(groups) {
  localStorage.setItem(IMPORT_GROUPS_KEY, JSON.stringify({
    created_at: new Date().toISOString(),
    groups
  }));
}

// ─── Ingest handler ───────────────────────────────────────────────────────────
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
    } catch (err) {
      setStatus("error", `Invalid JSON: ${err.message || "Unable to parse input."}`);
    } finally {
      ingestBtn.textContent = "Ingest";
      progressStep.textContent = "Idle";
      progressBar.style.width = "0%";
      updateIngestBtn();
    }

    return;
  }

  const anyChecked = endpointCbs.some((cb) => cb.checked);
  if (!anyChecked) {
    setStatus("error", "Please select at least one endpoint.");
    return;
  }

  if (epCbTopTracks && epCbTopTracks.checked) {
    const hasRange = epTtsEnabled.checked || epTtmEnabled.checked || epTtlEnabled.checked;
    if (!hasRange) {
      setStatus("error", "Top Tracks is enabled but no time ranges are selected.");
      return;
    }
  }

  ingestBtn.disabled = true;
  ingestBtn.textContent = "Saving...";
  progressNode.classList.remove("hidden");
  progressStep.textContent = "Building selection...";
  progressBar.style.width = "40%";
  setStatus("loading", "Saving your selection...");

  await sleep(300);

  const groups = buildImportGroups();
  persistImportGroups(groups);

  progressStep.textContent = "Done";
  progressBar.style.width = "100%";
  await sleep(200);

  const labels = groups.map((g) => g.label);
  setStatus("", `Saved. ${groups.length} endpoint group${groups.length !== 1 ? "s" : ""}: ${labels.join("; ")}.`);

  ingestBtn.disabled = false;
  ingestBtn.textContent = "Ingest";
  progressBar.style.width = "0%";
  progressStep.textContent = "Idle";
}

// ─── Init ─────────────────────────────────────────────────────────────────────
function init() {
  // Source switching
  sourceBtns.forEach((btn) => {
    btn.addEventListener("click", () => switchSource(btn.dataset.source));
  });

  if (manualJsonPaste) {
    manualJsonPaste.addEventListener("input", () => updateIngestBtn());
  }
  if (manualJsonFile) {
    manualJsonFile.addEventListener("change", () => updateIngestBtn());
  }

  // Endpoint accordion: title button toggles body open/closed
  endpointItems.forEach((item) => {
    const titleBtn = item.querySelector(".endpoint-title-btn");
    titleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleEndpointOpen(item);
    });

    // Checking the checkbox also auto-opens the body so user can see options
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

  // Use-max toggles
  useMaxToggles.forEach((toggle) => {
    applyUseMaxToggle(toggle);
    toggle.addEventListener("change", () => {
      applyUseMaxToggle(toggle);
      updateImportSummary();
    });
  });

  // Sub-checkboxes (top track time ranges) → update summary
  [epTtsEnabled, epTtmEnabled, epTtlEnabled].forEach((cb) => {
    if (cb) {
      cb.addEventListener("change", () => {
        setTopTracksParentFromChildren();
        updateControlEnabledState();
        updateIngestBtn();
      });
    }
  });

  // Number inputs → normalize and update summary
  [epTtsLimit, epTtmLimit, epTtlLimit, epSavMaxItems, epPlMaxPlaylists, epPlMaxItems, epRecMaxItems]
    .forEach((input) => {
      if (!input) return;
      input.addEventListener("input", () => { normalizeNumberInput(input); updateImportSummary(); });
      input.addEventListener("blur",  () => { normalizeNumberInput(input); updateImportSummary(); });
    });

  // Ingest button
  ingestBtn.addEventListener("click", handleIngest);

  // Set initial state
  switchSource("spotify");
  setTopTracksParentFromChildren();
  updateControlEnabledState();
  updateIngestBtn();
}

init();
