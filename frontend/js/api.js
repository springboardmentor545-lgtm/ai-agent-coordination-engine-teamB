const API_BASE = "";

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function clearToken() {
  localStorage.removeItem("access_token");
}

function requireLogin() {
  const token = getToken();
  if (!token) {
    window.location.href = "/app/login.html";
    return;
  }
  armSessionExpiryTimer(token);
}

function armSessionExpiryTimer(token) {
  const payload = decodeJwtPayload(token);
  if (!payload || !payload.exp) {
    return;
  }

  const expiryTimeMs = payload.exp * 1000;
  const msUntilExpiry = expiryTimeMs - Date.now();

  if (msUntilExpiry <= 0) {
    expireSessionNow();
    return;
  }

  setTimeout(expireSessionNow, msUntilExpiry);
}

function expireSessionNow() {
  clearToken();
  showModal("Your session has expired. Please log in again.", function () {
    window.location.href = "/app/login.html";
  });
}

function decodeJwtPayload(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch (e) {
    return null;
  }
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = options.headers || {};

  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(API_BASE + path, { ...options, headers });

  if (response.status === 401) {
    expireSessionNow();
    return null;
  }
  return response;
}

function showModal(message, onConfirm) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal-box">
      <p>${message}</p>
      <button class="modal-ok-btn">OK</button>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelector(".modal-ok-btn").addEventListener("click", function () {
    document.body.removeChild(overlay);
    if (onConfirm) onConfirm();
  });
}

function showChoiceModal(message, choices, onChoice) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";

  const buttonsHtml = choices.map(function (choice, index) {
    return `<button class="modal-choice-btn" data-index="${index}">${choice.label}</button>`;
  }).join("");

  overlay.innerHTML = `
    <div class="modal-box">
      <p>${message}</p>
      <div class="modal-choices">${buttonsHtml}</div>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelectorAll(".modal-choice-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const chosen = choices[parseInt(btn.dataset.index, 10)];
      document.body.removeChild(overlay);
      onChoice(chosen.value);
    });
  });
}


function showLogPanel(threadId, logs) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";

  let rowsHtml;
  if (!logs || logs.length === 0) {
    rowsHtml = "<p>No audit log entries found for this session.</p>";
  } else {
    rowsHtml = logs.map(function (row) {
      const failedClass = row.status === "failure" ? " log-row-failed" : "";
      const toolPart = row.tool_name ? ` (tool: ${row.tool_name})` : "";
      const durationPart = row.duration_ms !== null && row.duration_ms !== undefined ? ` — ${row.duration_ms}ms` : "";
      const detailPart = row.detail ? `<div class="log-detail">${row.detail}</div>` : "";
      return `
        <div class="log-row${failedClass}">
          <div class="log-row-header">
            <strong>${row.agent_name}</strong> — ${row.action}${toolPart}${durationPart}
          </div>
          <div class="log-timestamp">${row.created_at}</div>
          ${detailPart}
        </div>
      `;
    }).join("");
  }

  overlay.innerHTML = `
    <div class="modal-box log-panel">
      <h3>Audit Log — Thread ${threadId}</h3>
      <div class="log-panel-scroll">${rowsHtml}</div>
      <button class="modal-ok-btn">Close</button>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelector(".modal-ok-btn").addEventListener("click", function () {
    document.body.removeChild(overlay);
  });
}