// Jaartal in de footer
document.getElementById("year").textContent = new Date().getFullYear();

// Mobiel menu openen/sluiten
const toggle = document.querySelector(".nav-toggle");
const nav = document.getElementById("nav");

toggle.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  toggle.setAttribute("aria-expanded", open);
  toggle.setAttribute("aria-label", open ? "Menu sluiten" : "Menu openen");
});

// Menu sluiten na klik op een link
nav.querySelectorAll("a").forEach((link) =>
  link.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Menu openen");
  })
);

// Blokken rustig laten verschijnen bij scrollen
const revealItems = document.querySelectorAll(".card, .car-card, .review, .stat, .section__head");
if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  revealItems.forEach((el) => {
    el.classList.add("reveal");
    observer.observe(el);
  });
}

// Contactformulier: simpele controle.
// LET OP: het formulier verstuurt nog niets. Koppel het aan een dienst
// (bijv. Formspree of een eigen server) voordat de site live gaat.
const form = document.getElementById("contact-form");
const msg = form.querySelector(".form__msg");

form.addEventListener("submit", (e) => {
  e.preventDefault();
  let valid = true;

  form.querySelectorAll("[required]").forEach((field) => {
    const empty = field.value.trim() === "";
    field.classList.toggle("invalid", empty);
    if (empty) valid = false;
  });

  if (!valid) {
    msg.textContent = "Vul uw naam en telefoon of e-mail in.";
    msg.className = "form__msg err";
    return;
  }

  msg.textContent = "Bedankt! We nemen zo snel mogelijk contact met u op.";
  msg.className = "form__msg ok";
  form.reset();
});
