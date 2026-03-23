const profileForm = document.getElementById("profile-form");
const profileStatus = document.getElementById("profile-status");
const importedGroupsNode = document.getElementById("imported-groups");

const IMPORT_GROUPS_KEY = "playlist_import_groups_v1";
const PROFILE_EXCLUSIONS_KEY = "playlist_profile_exclusions_v1";
const EXPORT_BASE = "../implementation_notes/ingestion/outputs/spotify_api_export";
const RENDER_LIMIT_PER_GROUP = 1200;

const state = {
  groups: [],
  groupSource: "none",
  excludeGroups: new Set(),
  excludeTracks: new Set()
};

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
    .filter((r) => r.track_name)
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

  return [
    {
      id: `${group.key}_all`,
      label: "All Items",
      tracks: group.tracks
    }
  ];
}

function toGroup(key, label, description, tracks) {
  const totalFromFile = tracks.length;
  const visibleTracks = tracks.slice(0, RENDER_LIMIT_PER_GROUP);
  const visibleNote = totalFromFile > visibleTracks.length
    ? ` Showing first ${visibleTracks.length} of ${totalFromFile} rows from your export.`
    : "";

  return {
    key,
    label,
    description: `${description}${visibleNote}`,
    tracks: visibleTracks
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
      key: "get_current_user_playlists_items",
      label: "GET /me/playlists + /playlists/{id}/items",
      description: "Loaded from existing spotify_playlist_items_flat.csv export.",
      path: `${EXPORT_BASE}/spotify_playlist_items_flat.csv`,
      mapper: mapPlaylistItemsRows
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

  return loaded
    .filter((item) => item.status === "fulfilled" && item.value)
    .map((item) => item.value);
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
    const exportGroups = await loadGroupsFromExistingExport();
    if (exportGroups.length) {
      state.groups = exportGroups;
      state.groupSource = "export";
      return;
    }
  } catch {
    // Ignore fetch failures and try local storage fallback.
  }

  const raw = localStorage.getItem(IMPORT_GROUPS_KEY);
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      const localGroups = Array.isArray(parsed.groups) ? parsed.groups : [];
      if (localGroups.length) {
        state.groups = localGroups;
        state.groupSource = "local";
        return;
      }
    } catch {
      state.groups = [];
    }
  }

  state.groups = [];
  state.groupSource = "none";
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
      const extraMeta = track.playlist_position ? ` · pos ${track.playlist_position}` : "";

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

async function init() {
  await loadGroups();
  renderGroups();

  if (!state.groups.length) {
    setStatus("warning", "No import data found. Save a selection from Import page or keep Spotify export files in implementation_notes/ingestion/outputs/spotify_api_export.");
  } else if (state.groupSource === "export") {
    setStatus("info", "Loaded from existing Spotify export artifacts.");
  } else if (state.groupSource === "local") {
    setStatus("warning", "Loaded from saved local selection data (export artifacts not available from this page context).");
  } else {
    setStatus("info", "Imported groups loaded. You can now exclude endpoint groups or specific tracks.");
  }

  profileForm.addEventListener("submit", handleSaveProfile);
}

init();
