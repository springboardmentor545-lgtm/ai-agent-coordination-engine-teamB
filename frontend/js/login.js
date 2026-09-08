document.getElementById("login-form").addEventListener("submit", async function (event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorMessage = document.getElementById("error-message");
  errorMessage.textContent = "";

  const response = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email, password: password }),
  });

  const data = await response.json();

  if (response.ok) {
    setToken(data.access_token);
    window.location.href = "/app/dashboard.html";
  } else {
    errorMessage.textContent = data.error || "Login failed.";
  }
});