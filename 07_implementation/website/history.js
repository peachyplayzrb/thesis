const refreshBtn = document.getElementById("history-refresh-btn");
const messageNode = document.getElementById("history-message");
const bodyNode = document.getElementById("history-body");

const API_HISTORY = "/api/pipeline/run/history?limit=20";

function formatDateTimeDisplay(isoValue) {
  if (!isoValue) return "-";
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return isoValue;
  return date.toISOString().replace(".000", "");
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

function renderHistory(runs) {
  if (!Array.isArray(runs) || !runs.length) {
    bodyNode.innerHTML = '<tr><td colspan="7" class="hint">No run history available yet.</td></tr>';
    return;
  }

  bodyNode.innerHTML = runs.map((run) => {
    const compare = run.compare_to_previous || {};
    const changedCount = Number.isFinite(compare.changed_count) ? compare.changed_count : 0;
    const baseline = compare.baseline_run_id || "none";
    const runId = run.run_id || "-";
    const link = run.run_id ? `results.html?run_id=${encodeURIComponent(run.run_id)}` : "results.html";

    return `<tr>
      <td>${runId}</td>
      <td>${run.status || "-"}</td>
      <td>${formatDateTimeDisplay(run.started_at_utc)}</td>
      <td>${formatDateTimeDisplay(run.completed_at_utc)}</td>
      <td>${changedCount}</td>
      <td>${baseline}</td>
      <td><a href="${link}">Open</a></td>
    </tr>`;
  }).join("");
}

async function refreshHistory() {
  messageNode.textContent = "Loading run history...";
  try {
    const snapshot = await fetchJson(API_HISTORY);
    const runs = snapshot.runs || [];
    messageNode.textContent = runs.length
      ? `Loaded ${runs.length} runs (history total: ${snapshot.history_count || runs.length}).`
      : "No run history available yet.";
    renderHistory(runs);
  } catch (error) {
    messageNode.textContent = String(error.message || error);
    renderHistory([]);
  }
}

refreshBtn.addEventListener("click", refreshHistory);
refreshHistory();
