async function initPartials(config) {
  for (const key in config) {
    const { id, file } = config[key];
    const element = document.getElementById(id);
    if (!element) continue;

    const response = await fetch(file);
    if (!response.ok) {
      console.error(`Erro ao carregar partial: ${file}`);
      continue;
    }

    element.innerHTML = await response.text();
  }
}