(function () {
  "use strict";

  function initSidebar() {
    var shell = document.getElementById("app-shell");
    var toggle = document.getElementById("sidebar-toggle");
    var backdrop = document.getElementById("sidebar-backdrop");
    if (!shell || !toggle) return;

    function openNav() {
      shell.classList.add("nav-open");
      toggle.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    }

    function closeNav() {
      shell.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }

    toggle.addEventListener("click", function () {
      if (shell.classList.contains("nav-open")) closeNav();
      else openNav();
    });

    if (backdrop) {
      backdrop.addEventListener("click", closeNav);
    }

    shell.querySelectorAll(".sidebar-nav a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 959px)").matches) closeNav();
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && shell.classList.contains("nav-open")) closeNav();
    });
  }

  function initFormLoading() {
    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function () {
        if (form.classList.contains("no-loading")) return;
        if (form.classList.contains("lecture-star-form-header")) return;
        if (form.classList.contains("lecture-star-form-card")) return;
        if (form.classList.contains("study-progress-quick")) return;
        if (form.classList.contains("study-progress-quick--header")) return;
        if (form.classList.contains("study-progress-quick--course")) return;
        var method = (form.getAttribute("method") || "get").toLowerCase();
        if (method === "get") return;
        var btn =
          form.querySelector('button[type="submit"]') ||
          form.querySelector('input[type="submit"]');
        if (!btn || btn.disabled) return;
        btn.classList.add("is-loading");
        btn.disabled = true;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initSidebar();
      initFormLoading();
    });
  } else {
    initSidebar();
    initFormLoading();
  }
})();
