requireLogin();

document.getElementById("logout-btn").addEventListener("click", function () {
  clearToken();
  window.location.href = "/app/login.html";
});

function addDays(isoDate, delta) {
  const date = new Date(isoDate + "T00:00:00");
  date.setDate(date.getDate() + delta);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getDateRange(startIso, endIso) {
  const dates = [];
  let current = startIso;
  while (current <= endIso) {
    dates.push(current);
    current = addDays(current, 1);
  }
  return dates;
}

function buildSessionCard(session) {
  const card = document.createElement("div");
  card.className = "session-card";
  card.dataset.threadId = session.thread_id;

  let extraControls = "";

  if (session.decision_outcome === "APPROVE") {
    const dayBefore = addDays(session.start_date, -1);
    const dayAfter = addDays(session.end_date, 1);

    let extendHtml;
    if (session.extend_locked) {
      extendHtml = `<p class="hint">Extension unavailable for this session.</p>`;
    } else {
      extendHtml = `
        <button class="secondary extend-btn" data-date="${dayBefore}">Extend to include ${dayBefore}</button>
        <button class="secondary extend-btn" data-date="${dayAfter}">Extend to include ${dayAfter}</button>
      `;
    }

    const remainingDates = getDateRange(session.start_date, session.end_date)
      .filter(function (d) { return !session.cancelled_dates.includes(d); });

    let cancelHtml = "";
    if (remainingDates.length > 0) {
      const checkboxes = remainingDates.map(function (d) {
        return `<label class="checkbox-label"><input type="checkbox" class="cancel-checkbox" value="${d}"> ${d}</label>`;
      }).join("");
      cancelHtml = `
        <div class="cancel-section">
          ${checkboxes}
          <button class="danger cancel-btn">Cancel Selected</button>
        </div>
      `;
    } else {
      cancelHtml = `<p class="hint">All days in this session are cancelled.</p>`;
    }

    extraControls = `<div class="card-actions">${extendHtml}${cancelHtml}</div>`;
  }

  let cancelledNote = "";
  if (session.cancelled_dates && session.cancelled_dates.length > 0) {
    cancelledNote = `<p class="cancelled-note">Cancelled: ${session.cancelled_dates.join(", ")}</p>`;
  }

  card.innerHTML = `
    <strong>${session.start_date} to ${session.end_date}</strong>
    <span class="outcome outcome-${session.decision_outcome}">${session.decision_outcome}</span>
    <p>${session.reason || ""}</p>
    ${cancelledNote}
    <p class="thread-id">Thread: ${session.thread_id}</p>
    ${extraControls}
    <p class="card-message"></p>
  `;

  return card;
}

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
    listDiv.appendChild(buildSessionCard(session));
  });
}

document.getElementById("sessions-list").addEventListener("click", async function (event) {
  const card = event.target.closest(".session-card");
  if (!card) return;
  const threadId = card.dataset.threadId;
  const messageEl = card.querySelector(".card-message");

  if (event.target.classList.contains("extend-btn")) {
    const date = event.target.dataset.date;
    messageEl.textContent = "Processing...";
    messageEl.className = "card-message";
    const response = await apiFetch(`/sessions/${threadId}/extend`, {
      method: "POST",
      body: JSON.stringify({ start_date: date, end_date: date }),
    });
    if (!response) return;
    const data = await response.json();
    messageEl.textContent = "";

    if (data.error) {
      messageEl.textContent = data.error;
      messageEl.className = "card-message error";
    } else {
      showModal(data.message || "Extension processed.", loadSessions);
    }
  }

  if (event.target.classList.contains("cancel-btn")) {
    const checked = card.querySelectorAll(".cancel-checkbox:checked");
    const datesToCancel = Array.from(checked).map(function (cb) { return cb.value; });

    if (datesToCancel.length === 0) {
      messageEl.textContent = "Select at least one date to cancel.";
      messageEl.className = "card-message error";
      return;
    }

    messageEl.textContent = "Processing...";
    messageEl.className = "card-message";
    const response = await apiFetch(`/sessions/${threadId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ dates_to_cancel: datesToCancel }),
    });
    if (!response) return;
    const data = await response.json();
    messageEl.textContent = "";

    if (data.error) {
      messageEl.textContent = data.error;
      messageEl.className = "card-message error";
    } else {
      showModal(data.message || "Cancellation processed.", loadSessions);
    }
  }
});

loadSessions();