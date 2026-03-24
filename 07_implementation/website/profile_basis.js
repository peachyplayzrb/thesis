const profileForm = document.getElementById("profile-form");
const profileStatus = document.getElementById("profile-status");
const importedGroupsNode = document.getElementById("imported-groups");
const profileImportSummaryMessage = document.getElementById("profile-import-summary-message");
const profileImportSourceNode = document.getElementById("profile-import-source");
const profileImportGeneratedAtNode = document.getElementById("profile-import-generated-at");
const profileImportRunIdNode = document.getElementById("profile-import-run-id");
const profileImportGroupCountNode = document.getElementById("profile-import-group-count");
const profileImportTrackCountNode = document.getElementById("profile-import-track-count");
const profileImportInclusionNode = document.getElementById("profile-import-inclusion");
const profileImportSelectionNode = document.getElementById("profile-import-selection");
const downloadIncludedBtn = document.getElementById("download-included-btn");
const downloadExclusionsBtn = document.getElementById("download-exclusions-btn");
const downloadProfileBundleBtn = document.getElementById("download-profile-bundle-btn");

const IMPORT_GROUPS_KEY = "playlist_import_groups_v1";
const PROFILE_EXCLUSIONS_KEY = "playlist_profile_exclusions_v1";
const EXPORT_BASE = "../implementation_notes/ingestion/outputs/spotify_api_export";
const EXPORT_PLAYLISTS_PATH = `${EXPORT_BASE}/spotify_playlists_flat.csv`;
const EXPORT_RECENTLY_PLAYED_PATH = `${EXPORT_BASE}/spotify_recently_played_flat.csv`;
const EXPORT_SUMMARY_PATH = `${EXPORT_BASE}/spotify_export_run_summary.json`;

const state = {
  groups: [],
  groupSource: "none",
  groupSourceMeta: null,
  excludeGroups: new Set(),
  excludeTracks: new Set()
};

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) {
    return "-";
  }
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) {
    return isoValue;
  }
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
  const lines = text
    .split(/\r?\n/)
    .filter((line) => line.trim().length > 0);

  if (!lines.length) {
    return [];
  }

  const headers = csvSplitLine(lines[0]).map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const cells = csvSplitLine(line);
    const row = {};
    headers.forEach((header, index) => {
      row[header] = (cells[index] || "").trim();
    });
    return row;
  });
}

function mapTopTracksRows(rows) {
  return rows
    .filter((r) => r.track_name)
    .map((r, index) => ({
      id: r.track_id || `top_${index + 1}`,
      title: r.track_name || "Untitled",
      artist: r.artist_names || "Unknown artist",
      source_key: r.time_range ? `top_tracks_${r.time_range}` : "top_tracks"
    }));
}

function mapSavedTracksRows(rows) {
  return rows
    .filter((r) => r.track_name)
    .map((r, index) => ({
      id: r.track_id || `saved_${index + 1}`,
      title: r.track_name || "Untitled",
      artist: r.artist_names || "Unknown artist",
      source_key: "saved_tracks"
    }));
}

function mapPlaylistItemsRows(rows) {
  return rows
    .filter((r) => (r.track_name || "").trim().length > 0)
    .map((r, index) => ({
      id: r.track_id || `pl_item_${index + 1}`,
      title: r.track_name || "Untitled",
      artist: r.artist_names || r.playlist_name || "Unknown artist",
      source_key: "current_user_playlist_items",
      playlist_id: r.playlist_id || "unknown_playlist",
      playlist_name: r.playlist_name || "Unknown Playlist",
      playlist_position: r.playlist_position || ""
    }));
}

function mapPlaylistsRows(rows) {
  return rows
    .filter((r) => r.playlist_name)
    .map((r, index) => ({
      id: r.playlist_id || `playlist_${index + 1}`,
      title: r.playlist_name || "Untitled Playlist",
      artist: r.owner_id ? `owner: ${r.owner_id}` : "owner: unknown",
      source_key: "current_user_playlists",
      playlist_id: r.playlist_id || "unknown_playlist",
      playlist_name: r.playlist_name || "Unknown Playlist",
      tracks_total: r.tracks_total || "",
      is_public: r.public || "",
      collaborative: r.collaborative || ""
    }));
}

function mapRecentlyPlayedRows(rows) {
  return rows
    .filter((r) => r.track_name)
    .map((r, index) => ({
      id: r.track_id || `recent_${index + 1}`,
      title: r.track_name || "Untitled",
      artist: r.artist_names || "Unknown artist",
      source_key: "recently_played",
      played_at: r.played_at || ""
    }));
}

function toTitleCase(value) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function groupBy(items, keyFn) {
  const map = new Map();
  items.forEach((item) => {
    const key = keyFn(item);
    if (!map.has(key)) {
      map.set(key, []);
    }
    map.get(key).push(item);
  });
  return map;
}

function buildSubsectionsForGroup(group) {
  if (group.key === "get_top_tracks") {
    const grouped = groupBy(group.tracks, (track) => track.source_key || "top_tracks");
    return Array.from(grouped.entries()).map(([key, tracks]) => {
      const rawRange = key.replace("top_tracks_", "") || "all";
      return {
        id: `range_${rawRange}`,
        label: `Time Range: ${toTitleCase(rawRange)}`,
        tracks
      };
    });
  }

  if (group.key === "get_current_user_playlists_items") {
    const grouped = groupBy(group.tracks, (track) => track.playlist_id || track.playlist_name || "playlist_unknown");
    return Array.from(grouped.entries()).map(([playlistKey, tracks]) => {
      const playlistName = tracks[0].playlist_name || "Unknown Playlist";
      return {
        id: `playlist_${playlistKey}`,
        label: `Playlist: ${playlistName}`,
        tracks
      };
    });
  }

  if (group.key === "get_current_user_playlists") {
    return [
      {
        id: "all_playlists",
        label: "All Playlists",
        tracks: group.tracks
      }
    ];
  }

  return [
    {
      id: `${group.key}_all`,
      label: "All Items",
      tracks: group.tracks
    }
  ];
}

function toGroup(key, label, description, tracks) {
  return {
    key,
    label,
    description,
    tracks
  };
}

async function fetchCsvRows(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Unable to read ${path}`);
  }
  const text = await response.text();
  return parseCsv(text);
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Unable to read ${path}`);
  }
  return response.json();
}

async function loadGroupsFromExistingExport() {
  const sources = [
    {
      key: "get_top_tracks",
      label: "GET /me/top/tracks",
      description: "Loaded from existing spotify_top_tracks_flat.csv export.",
      path: `${EXPORT_BASE}/spotify_top_tracks_flat.csv`,
      mapper: mapTopTracksRows
    },
    {
      key: "get_saved_tracks",
      label: "GET /me/tracks",
      description: "Loaded from existing spotify_saved_tracks_flat.csv export.",
      path: `${EXPORT_BASE}/spotify_saved_tracks_flat.csv`,
      mapper: mapSavedTracksRows
    },
    {
      key: "get_current_user_playlists",
      label: "GET /me/playlists",
      description: "Loaded from existing spotify_playlists_flat.csv export.",
      path: EXPORT_PLAYLISTS_PATH,
      mapper: mapPlaylistsRows
    },
    {
      key: "get_current_user_playlists_items",
      label: "GET /me/playlists + /playlists/{id}/items",
      description: "Loaded from existing spotify_playlist_items_flat.csv export.",
      path: `${EXPORT_BASE}/spotify_playlist_items_flat.csv`,
      mapper: mapPlaylistItemsRows
    },
    {
      key: "get_recently_played",
      label: "GET /me/player/recently-played",
      description: "Loaded from existing spotify_recently_played_flat.csv export.",
      path: EXPORT_RECENTLY_PLAYED_PATH,
      mapper: mapRecentlyPlayedRows
    }
  ];

  const loaded = await Promise.allSettled(
    sources.map(async (source) => {
      const rows = await fetchCsvRows(source.path);
      const tracks = source.mapper(rows);
      if (!tracks.length) {
        return null;
      }
      return toGroup(source.key, source.label, source.description, tracks);
    })
  );

  const groups = loaded
    .filter((item) => item.status === "fulfilled" && item.value)
    .map((item) => item.value)
    .map((group) => group);

  const playlistItemsGroup = groups.find((group) => group.key === "get_current_user_playlists_items");
  const playlistsGroup = groups.find((group) => group.key === "get_current_user_playlists");

  if (!playlistItemsGroup || !playlistItemsGroup.tracks.length) {
    return groups.filter((group) => group.key !== "get_current_user_playlists");
  }

  if (playlistsGroup) {
    const ingestedPlaylistIds = new Set(
      playlistItemsGroup.tracks
        .map((track) => track.playlist_id)
        .filter((playlistId) => typeof playlistId === "string" && playlistId.length > 0)
    );

    playlistsGroup.tracks = playlistsGroup.tracks.filter((playlist) => ingestedPlaylistIds.has(playlist.playlist_id));
  }

  return groups.filter((group) => group.key !== "get_current_user_playlists" || group.tracks.length > 0);
}

function summarizeSelection(selection) {
  if (!selection) {
    return "-";
  }

  const parts = [];
  if (selection.include_top_tracks) {
    const ranges = Array.isArray(selection.top_time_ranges) && selection.top_time_ranges.length
      ? selection.top_time_ranges.join(", ")
      : "all ranges";
    parts.push(`Top: ${ranges}`);
  }
  if (selection.include_saved_tracks) {
    parts.push(`Saved: ${selection.saved_max_items ?? "max"}`);
  }
  if (selection.include_playlists) {
    parts.push(`Playlists: ${selection.playlists_max_items ?? "max"} / ${selection.playlist_items_max_per_playlist ?? "max"}`);
  }
  if (selection.include_recently_played) {
    parts.push(`Recent: ${selection.recently_played_limit ?? 50}`);
  }

  return parts.length ? parts.join(" | ") : "-";
}

function renderImportSummary() {
  const groupCount = state.groups.length;
  const trackCount = state.groups.reduce((sum, group) => sum + group.tracks.length, 0);
  const counts = getIncludedCounts();
  const meta = state.groupSourceMeta || {};
  const hasPlaylistGroup = state.groups.some((group) => group.key === "get_current_user_playlists");
  const hasPlaylistItemsGroup = state.groups.some((group) => group.key === "get_current_user_playlists_items");

  profileImportSourceNode.textContent = state.groupSource || "none";
  profileImportGeneratedAtNode.textContent = formatDateTimeDisplay(meta.generatedAt || meta.createdAt);
  profileImportRunIdNode.textContent = meta.runId || "-";
  profileImportGroupCountNode.textContent = String(groupCount);
  profileImportTrackCountNode.textContent = String(trackCount);
  profileImportInclusionNode.textContent = `${counts.includedTracks} / ${counts.excludedTracks}`;
  profileImportSelectionNode.textContent = meta.selectionSummary || "-";

  if (!groupCount) {
    profileImportSummaryMessage.textContent = "No imported data available yet.";
    return;
  }

  const caps = state.groupSourceMeta?.selectionCaps || [];
  if (caps.length) {
    profileImportSummaryMessage.textContent = `Export is currently capped (${caps.join(", ")}). Increase limits on Import page to see all playlists/items.`;
    return;
  }

  const playlistsRequested = Boolean(meta.selectionRaw && meta.selectionRaw.include_playlists);
  if (playlistsRequested && !hasPlaylistItemsGroup && !hasPlaylistGroup) {
    profileImportSummaryMessage.textContent = "Playlists are hidden because no playlist track rows were ingested from playlist items.";
    return;
  }

  if (state.groupSource === "local") {
    profileImportSummaryMessage.textContent = "Using the saved selection from the import page. This takes precedence over the full export fallback.";
    return;
  }

  if (state.groupSource === "export") {
    profileImportSummaryMessage.textContent = "Using full export artifacts because no saved import-page selection was found.";
    return;
  }

  profileImportSummaryMessage.textContent = "Imported groups loaded.";
}

function setStatus(type, message) {
  profileStatus.classList.remove("error", "warning");
  if (type === "error") {
    profileStatus.classList.add("error");
  }
  if (type === "warning") {
    profileStatus.classList.add("warning");
  }
  profileStatus.textContent = message;
}

async function loadGroups() {
  try {
    const summary = await fetchJson(EXPORT_SUMMARY_PATH).catch(() => null);
    const exportGroups = await loadGroupsFromExistingExport();
    if (exportGroups.length) {
      const selection = summary?.selection || {};
      const caps = [];
      if (selection.playlists_max_items !== null && selection.playlists_max_items !== undefined) {
        caps.push(`playlists=${selection.playlists_max_items}`);
      }
      if (selection.playlist_items_max_per_playlist !== null && selection.playlist_items_max_per_playlist !== undefined) {
        caps.push(`items-per-playlist=${selection.playlist_items_max_per_playlist}`);
      }

      state.groups = exportGroups;
      state.groupSource = "export";
      state.groupSourceMeta = {
        generatedAt: summary?.generated_at_utc || null,
        runId: summary?.run_id || null,
        selectionSummary: summarizeSelection(selection),
        selectionCaps: caps,
        selectionRaw: selection
      };
      return;
    }
  } catch {
    // Ignore fetch failures.
  }

  const raw = localStorage.getItem(IMPORT_GROUPS_KEY);
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      const localGroups = Array.isArray(parsed.groups) ? parsed.groups : [];
      if (localGroups.length) {
        state.groups = localGroups;
        state.groupSource = "local";
        state.groupSourceMeta = {
          createdAt: parsed.created_at || null,
          runId: parsed.run_id || null,
          selectionSummary: parsed.selection_summary || (
            Array.isArray(parsed.groups)
              ? `${parsed.groups.length} saved group${parsed.groups.length !== 1 ? "s" : ""}`
              : "Saved selection"
          ),
          selectionCaps: []
        };
        return;
      }
    } catch {
      state.groups = [];
    }
  }

  state.groups = [];
  state.groupSource = "none";
  state.groupSourceMeta = null;
}

function renderEmptyState() {
  importedGroupsNode.innerHTML = "";
  const card = document.createElement("div");
  card.className = "track-item";
  card.innerHTML = "<p class=\"track-title\">No imported endpoint groups found.</p><p class=\"track-meta\">Run API import first on the import page.</p>";
  importedGroupsNode.appendChild(card);
}

function renderGroup(group) {
  const wrap = document.createElement("section");
  wrap.className = "api-group";

  const endpointDetails = document.createElement("details");
  endpointDetails.className = "group-details";
  endpointDetails.open = true;

  const endpointSummary = document.createElement("summary");
  endpointSummary.className = "group-summary";
  endpointSummary.textContent = `${group.label} (${group.tracks.length} items)`;
  endpointDetails.appendChild(endpointSummary);

  const body = document.createElement("div");
  body.className = "group-body";

  const desc = document.createElement("p");
  desc.className = "hint";
  desc.textContent = group.description || "";
  body.appendChild(desc);

  const excludeGroupLabel = document.createElement("label");
  excludeGroupLabel.className = "scope-check";
  excludeGroupLabel.innerHTML = `<input type="checkbox" data-group="${group.key}" class="exclude-group-checkbox"><span>Exclude entire endpoint group</span>`;
  body.appendChild(excludeGroupLabel);

  const subsectionsWrap = document.createElement("div");
  subsectionsWrap.className = "subsections";

  const subsections = buildSubsectionsForGroup(group);
  subsections.forEach((section, sectionIndex) => {
    const sectionDetails = document.createElement("details");
    sectionDetails.className = "subsection-details";
    sectionDetails.open = sectionIndex === 0;

    const sectionSummary = document.createElement("summary");
    sectionSummary.className = "subsection-summary";
    sectionSummary.textContent = `${section.label} (${section.tracks.length})`;
    sectionDetails.appendChild(sectionSummary);

    const sectionBody = document.createElement("div");
    sectionBody.className = "subsection-body";

    const list = document.createElement("ul");
    list.className = "results";

    section.tracks.forEach((track, index) => {
      const li = document.createElement("li");
      li.className = "track-item";

      const safeTitle = track.title || "Untitled";
      const safeArtist = track.artist || "Unknown artist";
      const trackKey = `${group.key}::${section.id}::${track.id || "na"}::${index}`;
      const metaParts = [];
      if (track.playlist_position) {
        metaParts.push(`pos ${track.playlist_position}`);
      }
      if (group.key === "get_current_user_playlists" && track.tracks_total) {
        metaParts.push(`tracks ${track.tracks_total}`);
      }
      const extraMeta = metaParts.length ? ` · ${metaParts.join(" · ")}` : "";

      li.innerHTML = `
        <label class="scope-check">
          <input type="checkbox" data-track="${trackKey}" data-group="${group.key}" class="exclude-track-checkbox">
          <span><strong>${safeTitle}</strong><br><span class="track-meta">${safeArtist}${extraMeta}</span></span>
        </label>
      `;

      list.appendChild(li);
    });

    sectionBody.appendChild(list);
    sectionDetails.appendChild(sectionBody);
    subsectionsWrap.appendChild(sectionDetails);
  });

  body.appendChild(subsectionsWrap);
  endpointDetails.appendChild(body);
  wrap.appendChild(endpointDetails);
  importedGroupsNode.appendChild(wrap);
}

function renderGroups() {
  importedGroupsNode.innerHTML = "";

  if (!state.groups.length) {
    renderEmptyState();
    return;
  }

  state.groups.forEach((group) => renderGroup(group));

  importedGroupsNode.querySelectorAll(".exclude-group-checkbox").forEach((input) => {
    input.addEventListener("change", () => {
      const groupKey = input.getAttribute("data-group");
      if (input.checked) {
        state.excludeGroups.add(groupKey);
      } else {
        state.excludeGroups.delete(groupKey);
      }

      importedGroupsNode
        .querySelectorAll(`.exclude-track-checkbox[data-group="${groupKey}"]`)
        .forEach((trackCheckbox) => {
          trackCheckbox.disabled = input.checked;
          if (input.checked) {
            trackCheckbox.checked = false;
            state.excludeTracks.delete(trackCheckbox.getAttribute("data-track"));
          }
        });

      renderImportSummary();
    });
  });

  importedGroupsNode.querySelectorAll(".exclude-track-checkbox").forEach((input) => {
    input.addEventListener("change", () => {
      const trackId = input.getAttribute("data-track");
      if (input.checked) {
        state.excludeTracks.add(trackId);
      } else {
        state.excludeTracks.delete(trackId);
      }
      renderImportSummary();
    });
  });
}

function getIncludedCounts() {
  let totalTracks = 0;
  let excludedTracks = state.excludeTracks.size;

  state.groups.forEach((group) => {
    totalTracks += group.tracks.length;
    if (state.excludeGroups.has(group.key)) {
      excludedTracks += group.tracks.length;
    }
  });

  const includedTracks = Math.max(0, totalTracks - excludedTracks);
  return { totalTracks, excludedTracks, includedTracks };
}

function saveExclusions() {
  const payload = {
    saved_at: new Date().toISOString(),
    exclude_groups: Array.from(state.excludeGroups),
    exclude_tracks: Array.from(state.excludeTracks)
  };

  localStorage.setItem(PROFILE_EXCLUSIONS_KEY, JSON.stringify(payload));
}

function handleSaveProfile(event) {
  event.preventDefault();

  if (!state.groups.length) {
    setStatus("error", "No imported endpoint groups are available to configure.");
    return;
  }

  saveExclusions();
  const counts = getIncludedCounts();

  if (!counts.includedTracks) {
    setStatus("warning", "All tracks are currently excluded. You may want to include at least one endpoint or track.");
    return;
  }

  setStatus("info", `Exclusions saved. Included tracks: ${counts.includedTracks}/${counts.totalTracks}.`);
}

function buildIncludedTracksPayload() {
  const excludedGroups = state.excludeGroups;
  const excludedTracks = state.excludeTracks;
  const includedGroups = state.groups
    .filter((group) => !excludedGroups.has(group.key))
    .map((group) => {
      const includedTracks = [];
      const subsections = buildSubsectionsForGroup(group);
      subsections.forEach((section) => {
        section.tracks.forEach((track, index) => {
          const trackKey = `${group.key}::${section.id}::${track.id || "na"}::${index}`;
          if (!excludedTracks.has(trackKey)) {
            includedTracks.push(track);
          }
        });
      });
      return {
        key: group.key,
        label: group.label,
        description: group.description,
        tracks: includedTracks
      };
    })
    .filter((group) => group.tracks.length > 0);

  return {
    generated_at: new Date().toISOString(),
    source: state.groupSource,
    run_id: state.groupSourceMeta?.runId || null,
    groups: includedGroups,
    counts: getIncludedCounts()
  };
}

function buildExclusionsPayload() {
  return {
    generated_at: new Date().toISOString(),
    source: state.groupSource,
    run_id: state.groupSourceMeta?.runId || null,
    exclude_groups: Array.from(state.excludeGroups),
    exclude_tracks: Array.from(state.excludeTracks),
    counts: getIncludedCounts()
  };
}

function downloadJsonFile(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function handleDownloadIncluded() {
  if (!state.groups.length) {
    setStatus("error", "No imported groups available to export.");
    return;
  }
  downloadJsonFile("playlist_included_tracks.json", buildIncludedTracksPayload());
  setStatus("info", "Downloaded included tracks JSON.");
}

function handleDownloadExclusions() {
  if (!state.groups.length) {
    setStatus("error", "No imported groups available to export.");
    return;
  }
  downloadJsonFile("playlist_exclusions.json", buildExclusionsPayload());
  setStatus("info", "Downloaded exclusions JSON.");
}

function handleDownloadProfileBundle() {
  if (!state.groups.length) {
    setStatus("error", "No imported groups available to export.");
    return;
  }
  const bundle = {
    generated_at: new Date().toISOString(),
    source: state.groupSource,
    run_id: state.groupSourceMeta?.runId || null,
    summary: {
      import: state.groupSourceMeta,
      counts: getIncludedCounts()
    },
    included: buildIncludedTracksPayload(),
    exclusions: buildExclusionsPayload()
  };
  downloadJsonFile("playlist_profile_bundle.json", bundle);
  setStatus("info", "Downloaded full profile bundle JSON.");
}

async function init() {
  await loadGroups();
  renderImportSummary();
  renderGroups();

  if (!state.groups.length) {
    setStatus("warning", "No import data found. Save a selection from Import page or keep Spotify export files in implementation_notes/ingestion/outputs/spotify_api_export.");
  } else if (state.groupSource === "export") {
    setStatus("info", "Loaded from existing Spotify export artifacts (full export priority).");
  } else if (state.groupSource === "local") {
    setStatus("warning", "Loaded from saved local selection data because full export artifacts were unavailable.");
  } else {
    setStatus("info", "Imported groups loaded. You can now exclude endpoint groups or specific tracks.");
  }

  profileForm.addEventListener("submit", handleSaveProfile);

  if (downloadIncludedBtn) {
    downloadIncludedBtn.addEventListener("click", handleDownloadIncluded);
  }
  if (downloadExclusionsBtn) {
    downloadExclusionsBtn.addEventListener("click", handleDownloadExclusions);
  }
  if (downloadProfileBundleBtn) {
    downloadProfileBundleBtn.addEventListener("click", handleDownloadProfileBundle);
  }
}

init();
