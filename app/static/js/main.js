async function loadPartial(targetId, filePath) {
  const target = document.getElementById(targetId);
  if (!target) return;

  try {
    const response = await fetch(filePath);

    if (!response.ok) {
      throw new Error(`Erro ao carregar o partial: ${filePath}`);
    }

    const html = await response.text();
    target.innerHTML = html;
  } catch (error) {
    console.error(error);
  }
}

async function initPartials(config) {
  const tasks = [];

  if (config.header) {
    tasks.push(loadPartial(config.header.id, config.header.file));
  }

  if (config.footer) {
    tasks.push(loadPartial(config.footer.id, config.footer.file));
  }

  await Promise.all(tasks);
}

function initHeaderMenu() {
  const mobileMenuToggle = document.getElementById("mobileMenuToggle");
  const mobileMenuClose = document.getElementById("mobileMenuClose");
  const mobileMenu = document.getElementById("mobileMenu");
  const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

  if (!mobileMenuToggle || !mobileMenuClose || !mobileMenu || !mobileMenuOverlay) {
    return;
  }

  if (mobileMenuToggle.dataset.menuBound === "true") {
    return;
  }

  function openMobileMenu() {
    mobileMenu.classList.add("is-open");
    mobileMenuOverlay.classList.add("is-active");
    mobileMenu.setAttribute("aria-hidden", "false");
    mobileMenuToggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("menu-open");
  }

  function closeMobileMenu() {
    mobileMenu.classList.remove("is-open");
    mobileMenuOverlay.classList.remove("is-active");
    mobileMenu.setAttribute("aria-hidden", "true");
    mobileMenuToggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
  }

  mobileMenuToggle.addEventListener("click", openMobileMenu);
  mobileMenuClose.addEventListener("click", closeMobileMenu);
  mobileMenuOverlay.addEventListener("click", closeMobileMenu);

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeMobileMenu();
    }
  });

  mobileMenuToggle.dataset.menuBound = "true";
}