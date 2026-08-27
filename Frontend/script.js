const API_URL = "http://127.0.0.1:8000/ask";

const questionInput = document.getElementById("question");
const sessionInput = document.getElementById("sessionId");
const askButton = document.getElementById("askBtn");
const newSessionButton = document.getElementById("newSessionBtn");

const responseBox = document.getElementById("response");
const loading = document.getElementById("loading");


askButton.addEventListener("click", async () => {

    const question = questionInput.value.trim();
    const sessionId = sessionInput.value.trim();

    if (!question) {
        responseBox.textContent = "Please enter a question.";
        return;
    }

    loading.classList.remove("hidden");
    responseBox.textContent = "";

    askButton.disabled = true;

    try {

        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question,
                session_id: sessionId || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Something went wrong."
            );
        }

        responseBox.textContent = data.response;

        sessionInput.value = data.session_id;

    } catch (error) {

        responseBox.textContent =
            "Error: " + error.message;

    } finally {

        loading.classList.add("hidden");
        askButton.disabled = false;

    }
});


newSessionButton.addEventListener("click", () => {

    sessionInput.value =
        "session-" + Date.now();

    questionInput.value = "";

    responseBox.textContent =
        "New session started.";

});