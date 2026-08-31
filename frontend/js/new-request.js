requireLogin();

let currentMonth = new Date();
currentMonth.setDate(1);

let holidaySet = new Set();

function formatDateISO(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function isWeekend(date) {
  const day = date.getDay();
  return day === 0 || day === 6;
}

function isPast(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date < today;
}

async function loadHolidaysForMonth() {
  const start = formatDateISO(currentMonth);
  const lastDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
  const end = formatDateISO(lastDay);

  const response = await apiFetch(`/holidays?start_date=${start}&end_date=${end}`);
  if (!response) return;
  const data = await response.json();
  holidaySet = new Set(data.holidays || []);
}

async function renderCalendar() {
  await loadHolidaysForMonth();

  const monthLabel = document.getElementById("month-label");
  monthLabel.textContent = currentMonth.toLocaleString("default", { month: "long", year: "numeric" });

  const grid = document.getElementById("calendar-grid");
  grid.innerHTML = "";

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  dayNames.forEach(function (name) {
    const header = document.createElement("div");
    header.className = "day-header";
    header.textContent = name;
    grid.appendChild(header);
  });

  const firstDayOfWeek = currentMonth.getDay();
  for (let i = 0; i < firstDayOfWeek; i++) {
    const blank = document.createElement("div");
    blank.className = "day-cell empty";
    grid.appendChild(blank);
  }

  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  for (let d = 1; d <= daysInMonth; d++) {
    const cellDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), d);
    const iso = formatDateISO(cellDate);

    const cell = document.createElement("div");
    cell.className = "day-cell";
    cell.textContent = d;
    cell.dataset.date = iso;

    if (isWeekend(cellDate) || holidaySet.has(iso) || isPast(cellDate)) {
      cell.classList.add("disabled");
    }

    grid.appendChild(cell);
  }
}

let selectedStart = null;
let selectedEnd = null;
let selectionLocked = false;

function updateSelectionSummary() {
  const summary = document.getElementById("selection-summary");
  if (selectedStart && selectedEnd) {
    summary.textContent = `Selected: ${selectedStart} to ${selectedEnd}`;
  } else if (selectedStart) {
    summary.textContent = `Start date: ${selectedStart}. Now click an end date.`;
  } else {
    summary.textContent = "";
  }
}

function highlightSelection() {
  const cells = document.querySelectorAll(".day-cell:not(.empty)");
  cells.forEach(function (cell) {
    cell.classList.remove("selected", "in-range");
    const date = cell.dataset.date;
    if (!date) return;

    if (date === selectedStart || date === selectedEnd) {
      cell.classList.add("selected");
    } else if (selectedStart && selectedEnd && date > selectedStart && date < selectedEnd) {
      cell.classList.add("in-range");
    }
  });
}

document.getElementById("calendar-grid").addEventListener("click", function (event) {
  const cell = event.target.closest(".day-cell");
  if (!cell || cell.classList.contains("disabled") || cell.classList.contains("empty")) {
    return;
  }

  const clickedDate = cell.dataset.date;

  if (!selectedStart || selectionLocked) {
    // Starting a fresh selection: this single day is immediately a valid
    // one-day range on its own, no second click required.
    selectedStart = clickedDate;
    selectedEnd = clickedDate;
    selectionLocked = false;
  } else {
    // A start already exists and isn't locked yet: this click extends it
    // into a multi-day range, then locks — the next click after this starts fresh.
    if (clickedDate < selectedStart) {
      selectedEnd = selectedStart;
      selectedStart = clickedDate;
    } else {
      selectedEnd = clickedDate;
    }
    selectionLocked = true;
  }

  updateSelectionSummary();
  highlightSelection();
});

document.getElementById("submit-btn").addEventListener("click", async function () {
  const resultMessage = document.getElementById("result-message");
  resultMessage.textContent = "";
  resultMessage.className = "";

  if (!selectedStart || !selectedEnd) {
    resultMessage.textContent = "Please select both a start and end date.";
    resultMessage.className = "error";
    return;
  }

  const reason = document.getElementById("reason").value || "not specified";
  resultMessage.textContent = "Processing...";

  const response = await apiFetch("/leave-request", {
    method: "POST",
    body: JSON.stringify({
      start_date: selectedStart,
      end_date: selectedEnd,
      reason: reason,
    }),
  });
  if (!response) return;

  const data = await response.json();
  resultMessage.textContent = "";

  if (response.ok) {
    const message = data.decision
      ? `Result: ${data.decision}`
      : "Request submitted. This may need further review (e.g. a mixed-conflict choice) — check your dashboard.";
    showModal(message, function () {
      window.location.href = "/app/dashboard.html";
    });
  } else {
    resultMessage.textContent = data.error || "Something went wrong.";
    resultMessage.className = "error";
  }
});

document.getElementById("prev-month").addEventListener("click", function () {
  currentMonth.setMonth(currentMonth.getMonth() - 1);
  renderCalendar();
});

document.getElementById("next-month").addEventListener("click", function () {
  currentMonth.setMonth(currentMonth.getMonth() + 1);
  renderCalendar();
});

renderCalendar();