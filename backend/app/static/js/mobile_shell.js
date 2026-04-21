document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  if (!body) {
    return;
  }

  const drawer = document.querySelector("[data-shell-drawer]");
  const overlay = document.querySelector("[data-shell-overlay]");
  const openButtons = Array.from(document.querySelectorAll("[data-shell-open]"));
  const closeButtons = Array.from(document.querySelectorAll("[data-shell-close]"));
  const toggleButtons = Array.from(document.querySelectorAll("[data-shell-desktop-toggle]"));
  const navLinks = drawer ? Array.from(drawer.querySelectorAll("a[href]")) : [];
  const desktopModeStorageKey = "ytlush:mobile-shell:view-mode";

  function syncDesktopToggleUi(enabled) {
    toggleButtons.forEach(function (button) {
      button.dataset.active = enabled ? "true" : "false";
      button.setAttribute("aria-pressed", enabled ? "true" : "false");
      const label = button.querySelector("[data-shell-desktop-label]");
      if (label) {
        const nextText = enabled
          ? label.getAttribute("data-label-active")
          : label.getAttribute("data-label-default");
        if (nextText) {
          label.textContent = nextText;
        }
      }
    });
  }

  function setDesktopMode(enabled) {
    body.classList.toggle("mobile-desktop-mode", enabled);
    syncDesktopToggleUi(enabled);
    try {
      window.localStorage.setItem(desktopModeStorageKey, enabled ? "desktop" : "mobile");
    } catch (_error) {
      // Ignore localStorage errors in private mode.
    }
  }

  function readDesktopMode() {
    try {
      return window.localStorage.getItem(desktopModeStorageKey) === "desktop";
    } catch (_error) {
      return false;
    }
  }

  function setDrawerOpen(open) {
    if (!drawer || !overlay) {
      return;
    }
    body.classList.toggle("mobile-shell-open", open);
    drawer.setAttribute("aria-hidden", open ? "false" : "true");
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setDrawerOpen(true);
    });
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setDrawerOpen(false);
    });
  });

  if (overlay) {
    overlay.addEventListener("click", function () {
      setDrawerOpen(false);
    });
  }

  navLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      setDrawerOpen(false);
    });
  });

  toggleButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const nextEnabled = !body.classList.contains("mobile-desktop-mode");
      setDesktopMode(nextEnabled);
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setDrawerOpen(false);
    }
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 768) {
      setDrawerOpen(false);
    }
  });

  syncDesktopToggleUi(false);
  setDesktopMode(readDesktopMode());
  setDrawerOpen(false);
});
