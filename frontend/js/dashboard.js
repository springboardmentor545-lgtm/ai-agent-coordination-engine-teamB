requireLogin();

document.getElementById("logout-btn").addEventListener("click", function () {
  clearToken();
  window.location.href = "/app/login.html";
});

async function loadSessions() {
  const response = await apiFetch("/sessions");
  if (!response) return;

  const data = await response.json();
  const listDiv = document.getElementById("sessions-list");

  if (!data.sessions || data.sessions.length === 0) {
    listDiv.innerHTML = "<p>You have no leave sessions yet.</p>";
    return;
  }

  listDiv.innerHTML = "";
  data.sessions.forEach(function (session) {
    const card = document.createElement("div");
    card.className = "session-card";
    card.innerHTML = `
      <strong>${session.start_date} to ${session.end_date}</strong>
      <span class="outcome outcome-${session.decision_outcome}">${session.decision_outcome}</span>
      <p>${session.reason || ""}</p>
      <p class="thread-id">Thread: ${session.thread_id}</p>
    `;
    listDiv.appendChild(card);
  });
}

loadSessions();