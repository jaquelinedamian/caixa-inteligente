document.addEventListener("DOMContentLoaded", async function () {
  await initPartials({
    header: { id: "site-header", file: "../partials/header-auth.html" },
    footer: { id: "site-footer", file: "../partials/footer-auth.html" }
  });

  document
    .querySelectorAll('[data-bs-toggle="dropdown"]')
    .forEach(function (element) {
      new bootstrap.Dropdown(element);
    });

  document
    .querySelectorAll(".navbar-toggler")
    .forEach(function (element) {
      new bootstrap.Collapse(
        document.querySelector(element.getAttribute("data-bs-target")),
        { toggle: false }
      );
    });

  const form = document.getElementById("cadastroForm");
  const cepInput = document.getElementById("cep");
  const telefoneEmergenciaInput = document.getElementById("telefoneEmergencia");

  if (cepInput) {
    cepInput.addEventListener("input", function (event) {
      let value = event.target.value.replace(/\D/g, "").slice(0, 8);
      value = value.replace(/^(\d{5})(\d)/, "$1-$2");
      event.target.value = value;
    });
  }

  if (telefoneEmergenciaInput) {
    telefoneEmergenciaInput.addEventListener("input", function (event) {
      let value = event.target.value.replace(/\D/g, "").slice(0, 11);

      if (value.length > 10) {
        value = value.replace(/^(\d{2})(\d{5})(\d{0,4}).*/, "($1) $2-$3");
      } else {
        value = value.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, "($1) $2-$3");
      }

      event.target.value = value;
    });
  }

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const formData = {
        dataNascimento: document.getElementById("dataNascimento")?.value || "",
        genero: document.getElementById("genero")?.value || "",
        cep: document.getElementById("cep")?.value || "",
        endereco: document.getElementById("endereco")?.value || "",
        numero: document.getElementById("numero")?.value || "",
        complemento: document.getElementById("complemento")?.value || "",
        nomeEmergencia: document.getElementById("nomeEmergencia")?.value || "",
        telefoneEmergencia: document.getElementById("telefoneEmergencia")?.value || ""
      };

      localStorage.setItem("clientePerfilPessoal", JSON.stringify(formData));
      window.location.href = "busca-profissionais.html";
    });
  }
});