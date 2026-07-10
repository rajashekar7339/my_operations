(function () {
  "use strict";

  const navItems = document.querySelectorAll(".nav-item");
  const panels = document.querySelectorAll(".task-panel");

  // Sidebar navigation
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const taskId = btn.dataset.task;
      navItems.forEach((n) => {
        n.classList.remove("active");
        n.setAttribute("aria-current", "false");
      });
      panels.forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      btn.setAttribute("aria-current", "page");
      document.getElementById(`panel-${taskId}`)?.classList.add("active");
    });
  });

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
