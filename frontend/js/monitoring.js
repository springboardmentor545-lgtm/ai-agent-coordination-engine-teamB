requireLogin();

function msToReadable(ms) {
  if (ms === null || ms === undefined) return "N/A";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function statusBadgeClass(code) {
  if (code < 300) return "outcome-APPROVE";
  if (code < 400) return "outcome-ESCALATE";
  return "outcome-REJECT";
}

async function loadMonitoringStats() {
  const contentDiv = document.getElementById("monitoring-content");
  const response = await apiFetch("/monitoring-stats");
  if (!response) return;
  const stats = await response.json();

  const totalOutcomes = (stats.outcome_counts.success || 0) + (stats.outcome_counts.failure || 0);
  const successRate = totalOutcomes > 0
    ? Math.round((stats.outcome_counts.success / totalOutcomes) * 100)
    : null;

  const agentRows = stats.agent_stats.map(function (a) {
    return `<tr><td>${a.agent_name}</td><td>${a.executions}</td><td>${msToReadable(a.avg_duration_ms)}</td></tr>`;
  }).join("");

  const toolRows = stats.tool_stats.map(function (t) {
    return `<tr><td>${t.tool_name}</td><td>${t.calls}</td></tr>`;
  }).join("");

  const httpRows = stats.http_status_breakdown.map(function (h) {
    return `<tr><td><span class="outcome ${statusBadgeClass(h.status_code)}">${h.status_code}</span></td><td>${h.count}</td></tr>`;
  }).join("");

  contentDiv.innerHTML = `
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">${stats.total_requests}</div>
        <div class="stat-label">Total Leave Requests</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${msToReadable(stats.avg_overall_workflow_ms)}</div>
        <div class="stat-label">Avg Workflow Time</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${msToReadable(stats.avg_api_response_ms)}</div>
        <div class="stat-label">Avg API Response Time</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${successRate !== null ? successRate + "%" : "N/A"}</div>
        <div class="stat-label">Agent Success Rate</div>
      </div>
    </div>

    <h3>Agent Execution</h3>
    <table class="stat-table">
      <thead><tr><th>Agent</th><th>Executions</th><th>Avg Duration</th></tr></thead>
      <tbody>${agentRows || "<tr><td colspan=3>No data yet</td></tr>"}</tbody>
    </table>

    <h3>Tool Calls</h3>
    <table class="stat-table">
      <thead><tr><th>Tool</th><th>Calls</th></tr></thead>
      <tbody>${toolRows || "<tr><td colspan=2>No data yet</td></tr>"}</tbody>
    </table>

    <h3>HTTP Status Breakdown</h3>
    <table class="stat-table">
      <thead><tr><th>Status Code</th><th>Count</th></tr></thead>
      <tbody>${httpRows || "<tr><td colspan=2>No data yet</td></tr>"}</tbody>
    </table>
  `;
}

loadMonitoringStats();