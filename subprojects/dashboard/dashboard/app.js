import { onAuthChanged, signIn, doSignOut, currentUser } from "./auth.js";
import { apiGet, apiPost, apiDelete, sendCommand } from "./api.js";

const loginGate = document.getElementById("login-gate");
const dashboard = document.getElementById("dashboard");
const nav = document.getElementById("nav");
const userEmail = document.getElementById("user-email");

const views = {
  overview: document.getElementById("view-overview"),
  commands: document.getElementById("view-commands"),
  reminders: document.getElementById("view-reminders"),
  cmd: document.getElementById("view-cmd"),
};

function showView(name) {
  Object.values(views).forEach((el) => el.classList.add("hidden"));
  views[name].classList.remove("hidden");
  nav.querySelectorAll("a").forEach((a) => a.classList.remove("active"));
  const active = nav.querySelector(`[data-view="${name}"]`);
  if (active) active.classList.add("active");
}

nav.addEventListener("click", (e) => {
  if (e.target.dataset.view) {
    e.preventDefault();
    showView(e.target.dataset.view);
    if (e.target.dataset.view === "overview") loadOverview();
    if (e.target.dataset.view === "commands") loadCommands();
    if (e.target.dataset.view === "reminders") loadReminders();
  }
});

document.getElementById("btn-login").addEventListener("click", async () => {
  try {
    await signIn();
  } catch (e) {
    alert("Sign-in failed: " + e.message);
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  await doSignOut();
});

onAuthChanged((user) => {
  if (user) {
    loginGate.classList.add("hidden");
    dashboard.classList.remove("hidden");
    userEmail.textContent = user.email;
    showView("overview");
    loadOverview();
  } else {
    loginGate.classList.remove("hidden");
    dashboard.classList.add("hidden");
    userEmail.textContent = "";
  }
});

function setBanner(id, message) {
  const el = document.getElementById(id);
  if (!message) {
    el.textContent = "";
    el.classList.add("hidden");
    return;
  }
  el.textContent = message;
  el.classList.remove("hidden");
}

// Overview
async function loadOverview() {
  setBanner("overview-error", "");
  try {
    const data = await apiGet("/api/v1/dashboard/stats");
    const lib = data.library || {};
    document.getElementById("stat-profile").textContent = lib.profile || 0;
    document.getElementById("stat-terms").textContent = lib.terms || 0;
    document.getElementById("stat-books").textContent = lib.books || 0;
    document.getElementById("stat-articles").textContent = lib.articles || 0;
    document.getElementById("stat-thoughts").textContent = lib.thoughts || 0;
    document.getElementById("stat-references").textContent = lib.references || 0;

    const health = data.integrations || {};
    const healthEl = document.getElementById("health-list");
    healthEl.innerHTML = Object.entries(health)
      .map(
        ([name, ok]) =>
          `<div class="health-item"><span class="dot ${ok ? "ok" : "fail"}"></span>${name}</div>`
      )
      .join("");
  } catch (e) {
    console.error(e);
    setBanner("overview-error", e.message || "Could not load overview.");
  }
}

// Commands
async function loadCommands() {
  try {
    const cmds = await apiGet("/api/v1/commands");
    const tbody = document.querySelector("#commands-table tbody");
    tbody.innerHTML = cmds
      .map(
        (c) =>
          `<tr><td>${new Date(c.created_at).toLocaleString()}</td><td>${
            c.text
          }</td><td>${c.intent || ""}</td></tr>`
      )
      .join("");
  } catch (e) {
    console.error(e);
  }
}

// Reminders
async function loadReminders() {
  setBanner("reminders-error", "");
  const tbody = document.getElementById("reminders-tbody");
  const table = document.getElementById("reminders-table");
  const empty = document.getElementById("reminders-empty");
  try {
    const data = await apiGet("/api/v1/reminders");
    const items = Array.isArray(data.items) ? data.items : [];
    tbody.innerHTML = "";
    if (items.length === 0) {
      table.classList.add("hidden");
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");
    table.classList.remove("hidden");
    for (const row of items) {
      const tr = document.createElement("tr");
      const tdWhen = document.createElement("td");
      tdWhen.textContent = row.run_at ? new Date(row.run_at).toLocaleString() : "—";
      const tdMsg = document.createElement("td");
      tdMsg.textContent = row.message || "";
      const tdBtn = document.createElement("td");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn-danger";
      btn.textContent = "Delete";
      btn.addEventListener("click", async () => {
        if (!row.id || !confirm("Remove this reminder?")) return;
        try {
          const out = await apiDelete(`/api/v1/reminders/${encodeURIComponent(row.id)}`);
          if (out.status === "error") {
            alert(out.reply || "Delete failed");
            return;
          }
          await loadReminders();
        } catch (e) {
          alert(e.message);
        }
      });
      tdBtn.appendChild(btn);
      tr.append(tdWhen, tdMsg, tdBtn);
      tbody.appendChild(tr);
    }
  } catch (e) {
    console.error(e);
    table.classList.add("hidden");
    empty.classList.add("hidden");
    setBanner("reminders-error", e.message || "Could not load reminders.");
  }
}

document.getElementById("reminder-create").addEventListener("click", async () => {
  const message = document.getElementById("reminder-msg").value.trim();
  const runAt = document.getElementById("reminder-time").value;
  if (!message || !runAt) return;
  try {
    const out = await apiPost("/api/v1/reminders", { message, run_at: runAt });
    if (out.status === "error") {
      alert(out.reply || "Could not create reminder");
      return;
    }
    document.getElementById("reminder-msg").value = "";
    document.getElementById("reminder-time").value = "";
    loadReminders();
  } catch (e) {
    alert(e.message);
  }
});

// Command input
document.getElementById("dash-cmd-send").addEventListener("click", async () => {
  const input = document.getElementById("dash-cmd-input");
  const text = input.value.trim();
  if (!text) return;
  try {
    const data = await sendCommand(text);
    document.getElementById("dash-cmd-output").textContent = data.reply || data.status;
  } catch (e) {
    document.getElementById("dash-cmd-output").textContent = "Error: " + e.message;
  }
});
