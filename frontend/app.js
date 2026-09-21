const API_URL = "http://127.0.0.1:8000";


// ===============================
// LOAD DASHBOARD DATA
// ===============================

async function loadDashboard() {

    try {

        const response = await fetch(`${API_URL}/dashboard/data`);

        if (!response.ok) {
            throw new Error("Dashboard API unavailable");
        }

        const data = await response.json();

        updateMetrics(data);
        updateWorkflows(data.workflows || []);
        updateActivities(data.activities || []);

    } catch (error) {

        console.log("Dashboard data could not be loaded:", error);

    }
}


// ===============================
// UPDATE METRICS
// ===============================

function updateMetrics(data) {

    document.getElementById("totalWorkflows").textContent =
        data.total_workflows ?? 0;

    document.getElementById("completedWorkflows").textContent =
        data.completed_workflows ?? 0;

    document.getElementById("failedWorkflows").textContent =
        data.failed_workflows ?? 0;

    const average =
        Number(data.average_execution || 0);

    document.getElementById("averageExecution").textContent =
        `${average.toFixed(2)}s`;
}


// ===============================
// WORKFLOW TABLE
// ===============================

function updateWorkflows(workflows) {

    const table =
        document.getElementById("workflowTable");

    table.innerHTML = "";

    if (!workflows.length) {

        table.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    No workflows available
                </td>
            </tr>
        `;

        return;
    }

    workflows.slice(0, 10).forEach(workflow => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>#${workflow.workflow_id}</td>

            <td>
                ${escapeHtml(workflow.user_query || "")}
            </td>

            <td>
                ${statusBadge(workflow.status)}
            </td>

            <td>
                ${formatExecutionTime(workflow.execution_time)}
            </td>
        `;

        table.appendChild(row);

    });
}


// ===============================
// AGENT ACTIVITY TABLE
// ===============================

function updateActivities(activities) {

    const table =
        document.getElementById("activityTable");

    table.innerHTML = "";

    if (!activities.length) {

        table.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    No agent activity available
                </td>
            </tr>
        `;

        return;
    }

    activities.slice(0, 10).forEach(activity => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>#${activity.workflow_id}</td>

            <td>
                ${escapeHtml(activity.agent_name || "")}
            </td>

            <td>
                ${statusBadge(activity.status)}
            </td>

            <td>
                ${formatExecutionTime(activity.execution_time)}
            </td>

            <td>
                ${formatDate(activity.completed_at)}
            </td>
        `;

        table.appendChild(row);

    });
}


// ===============================
// STATUS BADGE
// ===============================

function statusBadge(status) {

    const value =
        String(status || "Unknown");

    const lower =
        value.toLowerCase();

    let className = "status-running";

    if (lower === "completed") {
        className = "status-completed";
    }

    if (lower === "failed") {
        className = "status-failed";
    }

    return `
        <span class="status-badge ${className}">
            ${escapeHtml(value)}
        </span>
    `;
}


// ===============================
// RUN NEW WORKFLOW
// ===============================

async function runWorkflow() {

    const input =
        document.getElementById("userQuery");

    const resultBox =
        document.getElementById("requestResult");

    const resultText =
        document.getElementById("finalDecision");

    const button =
        document.getElementById("submitRequest");

    const question =
        input.value.trim();

    if (!question) {

        alert("Please enter a request.");

        return;
    }

    button.disabled = true;
    button.textContent = "Running...";

    resultBox.classList.add("hidden");

    try {

        const response = await fetch(
            `${API_URL}/ask`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Workflow failed"
            );
        }

        resultText.textContent =
            data.response || "No response returned.";

        resultBox.classList.remove("hidden");

        input.value = "";

        await loadDashboard();

    } catch (error) {

        resultText.textContent =
            `Error: ${error.message}`;

        resultBox.classList.remove("hidden");

    } finally {

        button.disabled = false;
        button.textContent = "Run AI Workflow";
    }
}


// ===============================
// HELPERS
// ===============================

function formatExecutionTime(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "-";
    }

    return `${Number(value).toFixed(2)}s`;
}


function formatDate(value) {

    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ===============================
// EVENT LISTENERS
// ===============================

document
    .getElementById("submitRequest")
    .addEventListener("click", runWorkflow);


document
    .getElementById("refreshActivity")
    .addEventListener("click", loadDashboard);


// ===============================
// INITIAL LOAD
// ===============================

loadDashboard();