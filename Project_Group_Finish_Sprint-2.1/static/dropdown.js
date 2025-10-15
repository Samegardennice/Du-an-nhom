// dropdown.js - toggles the user dropdown and closes when clicking outside
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("gcUserToggle");
  const menu = document.getElementById("gcDropdownMenu");

  if (!toggle || !menu) return;

  // toggle on click
  toggle.addEventListener("click", function (e) {
    e.stopPropagation();
    menu.classList.toggle("show");
    // aria
    const shown = menu.classList.contains("show");
    menu.setAttribute("aria-hidden", shown ? "false" : "true");
  });

  // close when clicking outside
  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target) && e.target !== toggle) {
      menu.classList.remove("show");
      menu.setAttribute("aria-hidden", "true");
    }
  });

  // optional: close on Esc
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      menu.classList.remove("show");
      menu.setAttribute("aria-hidden", "true");
    }
  });
});
