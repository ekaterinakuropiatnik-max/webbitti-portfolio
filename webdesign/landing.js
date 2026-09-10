document.querySelector('#year').textContent = new Date().getFullYear();

if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const favicon = document.querySelector('link[rel="icon"]');
  const faviconFrames = [
    ['173b51', 'ffffff', '8b2635'],
    ['8b2635', 'ffffff', 'b9dce9']
  ];
  let faviconFrame = 0;
  window.setInterval(() => {
    const [background, foreground, dot] = faviconFrames[faviconFrame % faviconFrames.length];
    favicon.href = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="18" fill="#${background}"/><text x="32" y="42" text-anchor="middle" font-family="Arial,sans-serif" font-size="34" font-weight="700" fill="#${foreground}">W</text><circle cx="52" cy="12" r="6" fill="#${dot}"/></svg>`)}`;
    faviconFrame += 1;
  }, 1200);
}

document.querySelectorAll('[data-package]').forEach((link) => {
  link.addEventListener('click', () => {
    const message = document.querySelector('textarea[name="message"]');
    const packageField = document.querySelector('input[name="package"]');
    if (packageField) packageField.value = link.dataset.package;
    if (message && !message.value.trim()) {
      message.value = `Ich interessiere mich für: ${link.dataset.package}.\n\nKurz zu meinem Vorhaben: `;
    }
  });
});

if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const revealItems = document.querySelectorAll('.trust-strip, .section');
  document.body.classList.add('reveal-ready');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px' });
  revealItems.forEach((item) => revealObserver.observe(item));
}

const landingForm = document.querySelector('#landing-form');
landingForm.elements.startedAt.value = Date.now();
landingForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  const buttonText = button.querySelector('span');
  const status = event.currentTarget.querySelector('.form-status');
  const data = Object.fromEntries(new FormData(event.currentTarget).entries());
  button.disabled = true;
  buttonText.textContent = 'Anfrage wird gesendet …';
  status.className = 'form-status wide';
  status.textContent = '';
  try {
    const response = await fetch('/api/contact', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.message || 'Die Nachricht konnte nicht gesendet werden.');
    status.classList.add('success');
    status.textContent = result.message;
    event.currentTarget.reset();
    event.currentTarget.elements.startedAt.value = Date.now();
    event.currentTarget.elements.package.value = 'Individuelle Anfrage';
    if (window.gtag) {
      window.gtag('event', 'generate_lead', { form_id:'landing-form', value:1, currency:'EUR' });
      const tracking = window.WEBBITTI_TRACKING || {};
      if (tracking.adsId && tracking.conversionLabel) window.gtag('event', 'conversion', { send_to:`${tracking.adsId}/${tracking.conversionLabel}` });
    }
  } catch (error) {
    status.classList.add('error');
    status.innerHTML = `${error.message} <a href="mailto:kuropiatnyk.design@gmail.com">E-Mail schreiben</a> oder <a href="https://wa.me/4367764757974">WhatsApp öffnen</a>.`;
  } finally {
    button.disabled = false;
    buttonText.textContent = 'Kostenloses Erstgespräch anfragen';
  }
});
