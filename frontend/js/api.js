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
  if (!getToken()) {
    window.location.href = "/app/login.html";
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
    clearToken();
    window.location.href = "/app/login.html";
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