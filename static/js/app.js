(function () {
  "use strict";

  const navItems = document.querySelectorAll(".nav-item");
  const panels = document.querySelectorAll(".task-panel");

  const PATH_TO_TASK = {
    "/tps_calculator": "tps",
    "/app_dashboard": "dashboard",
  };

  // App Dashboard elements (needed early for activateTask)
  const dashboardBody = document.getElementById("dashboard-body");
  const dashboardMeta = document.getElementById("dashboard-meta");
  const dashboardError = document.getElementById("dashboard-error");
  const dashboardRefresh = document.getElementById("dashboard-refresh");

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function actuatorLink(cell) {
    if (!cell.url) return "";
    const href = escapeHtml(cell.url);
    return `<a class="dashboard-cell-link" href="${href}" target="_blank" rel="noopener noreferrer" title="${href}" aria-label="Open actuator">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
    </a>`;
  }

  function renderCell(cell) {
    const tone = cell.tone || "error";
    const link = actuatorLink(cell);
    if (cell.ok && cell.version) {
      const sub = cell.tone === "conflict" ? "differs from majority" : "";
      return `<td class="dashboard-cell tone-${tone}">
        <div class="dashboard-cell-main">
          <span>${cell.version}</span>
          ${link}
        </div>
        ${sub ? `<span class="dashboard-cell-sub">${sub}</span>` : ""}
      </td>`;
    }
    const label = cell.status ? `HTTP ${cell.status}` : (cell.error || "Error");
    return `<td class="dashboard-cell tone-error">
      <div class="dashboard-cell-main">
        <span>${label}</span>
        ${link}
      </div>
    </td>`;
  }

  function renderDashboard(data) {
    const envs = data.environments;
    const thead = document.querySelector("#dashboard-table thead tr");
    thead.innerHTML =
      '<th scope="col">App</th>' +
      envs.map((e) => `<th scope="col">${e}</th>`).join("");

    dashboardBody.innerHTML = data.apps
      .map((app) => {
        const cells = envs.map((env) => renderCell(app.environments[env])).join("");
        const conflict = app.has_conflict
          ? ' <span class="dashboard-cell-sub">conflict</span>'
          : "";
        return `<tr>
          <td class="dashboard-app-name">${app.name}${conflict}</td>
          ${cells}
        </tr>`;
      })
      .join("");

    if (data.checked_at) {
      const when = new Date(data.checked_at).toLocaleString();
      dashboardMeta.textContent = `Last checked: ${when}`;
      dashboardMeta.classList.remove("hidden");
    }
  }

  async function loadDashboard() {
    if (!dashboardBody) return;
    dashboardError.classList.add("hidden");
    dashboardRefresh.disabled = true;
    dashboardBody.innerHTML =
      '<tr><td class="dashboard-loading">Loading…</td></tr>';

    try {
      const res = await fetch("/api/dashboard");
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || res.statusText || "Request failed");
      }
      renderDashboard(data);
    } catch (err) {
      dashboardBody.innerHTML = "";
      dashboardError.textContent = err.message;
      dashboardError.classList.remove("hidden");
    } finally {
      dashboardRefresh.disabled = false;
    }
  }

  function activateTask(taskId, { push = false } = {}) {
    const btn = document.querySelector(`.nav-item[data-task="${taskId}"]`);
    if (!btn) return;

    navItems.forEach((n) => {
      n.classList.remove("active");
      n.setAttribute("aria-current", "false");
    });
    panels.forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    btn.setAttribute("aria-current", "page");
    document.getElementById(`panel-${taskId}`)?.classList.add("active");

    const path = btn.dataset.path;
    if (path && push && window.location.pathname !== path) {
      history.pushState({ taskId }, "", path);
    }

    if (taskId === "dashboard") {
      loadDashboard();
    }
  }

  // Sidebar navigation
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      activateTask(btn.dataset.task, { push: true });
    });
  });

  window.addEventListener("popstate", () => {
    const taskId = PATH_TO_TASK[window.location.pathname] || "tps";
    activateTask(taskId);
  });

  // Load dashboard if this page was opened/refreshed on that route
  if (PATH_TO_TASK[window.location.pathname] === "dashboard") {
    loadDashboard();
  }

  dashboardRefresh?.addEventListener("click", () => loadDashboard());

  // Info popover toggle
  document.querySelectorAll(".info-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const targetId = btn.dataset.infoTarget;
      const popover = document.getElementById(targetId);
      if (!popover) return;

      const isOpen = !popover.classList.contains("hidden");
      document.querySelectorAll(".info-popover").forEach((p) => p.classList.add("hidden"));
      document.querySelectorAll(".info-btn").forEach((b) => b.setAttribute("aria-expanded", "false"));

      if (!isOpen) {
        popover.classList.remove("hidden");
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("click", () => {
    document.querySelectorAll(".info-popover").forEach((p) => p.classList.add("hidden"));
    document.querySelectorAll(".info-btn").forEach((b) => b.setAttribute("aria-expanded", "false"));
  });

  function formatNumber(n, decimals = 0) {
    return Number(n).toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  function showError(form, message) {
    let el = form.querySelector(".error-msg");
    if (!el) {
      el = document.createElement("p");
      el.className = "error-msg";
      form.appendChild(el);
    }
    el.textContent = message;
  }

  function clearError(form) {
    form.querySelector(".error-msg")?.remove();
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || res.statusText || "Request failed");
    }
    return data;
  }

  // Sustain TPS form
  document.getElementById("form-sustain")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    clearError(form);
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
      const tps = parseFloat(form.tps.value);
      const minutes = parseFloat(form.minutes.value);
      const data = await postJson("/api/sustain", { tps, minutes });

      const card = document.getElementById("result-sustain");
      document.getElementById("result-sustain-value").textContent =
        formatNumber(data.transactions, 0) + " transactions";
      document.getElementById("info-sustain-formula").textContent = data.formula;
      document.getElementById("info-sustain-explanation").textContent = data.explanation;
      card.classList.remove("hidden");
    } catch (err) {
      showError(form, err.message);
    } finally {
      btn.disabled = false;
    }
  });

  // Duration form
  document.getElementById("form-duration")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    clearError(form);
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
      const transactions = parseFloat(form.transactions.value);
      const tps = parseFloat(form.tps.value);
      const data = await postJson("/api/duration", { transactions, tps });

      const card = document.getElementById("result-duration");
      document.getElementById("result-duration-value").textContent =
        formatNumber(data.seconds, 2) + " sec (" + formatNumber(data.minutes, 2) + " min)";
      document.getElementById("info-duration-formula").textContent = data.formula;
      document.getElementById("info-duration-explanation").textContent = data.explanation;
      card.classList.remove("hidden");
    } catch (err) {
      showError(form, err.message);
    } finally {
      btn.disabled = false;
    }
  });
})();
