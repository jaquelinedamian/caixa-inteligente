function openMobileMenu() {
  const menu = document.getElementById("mobileMenu");
  const overlay = document.getElementById("mobileMenuOverlay");
  const toggle = document.getElementById("mobileMenuToggle");

  if (!menu || !overlay) return;

  menu.classList.add("is-open");
  overlay.classList.add("is-open");
  menu.setAttribute("aria-hidden", "false");
  toggle?.setAttribute("aria-expanded", "true");
  document.body.style.overflow = "hidden";
}

function closeMobileMenu() {
  const menu = document.getElementById("mobileMenu");
  const overlay = document.getElementById("mobileMenuOverlay");
  const toggle = document.getElementById("mobileMenuToggle");

  if (!menu || !overlay) return;

  menu.classList.remove("is-open");
  overlay.classList.remove("is-open");
  menu.setAttribute("aria-hidden", "true");
  toggle?.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
}

document.addEventListener("click", function (e) {
  if (e.target.closest("#mobileMenuToggle")) {
    openMobileMenu();
    return;
  }

  if (e.target.closest("#mobileMenuClose") || e.target.id === "mobileMenuOverlay") {
    closeMobileMenu();
  }
});

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    closeMobileMenu();
  }
});