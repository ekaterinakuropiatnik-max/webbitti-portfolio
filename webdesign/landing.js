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

document.querySelector('#landing-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const subject = encodeURIComponent('Anfrage: Webbitti Business-Website €890');
  const body = encodeURIComponent(
    `Name: ${data.get('name')}\n` +
    `E-Mail: ${data.get('email')}\n` +
    `Unternehmen / Branche: ${data.get('company') || '—'}\n\n` +
    `Vorhaben:\n${data.get('message')}`
  );
  window.location.href = `mailto:kuropiatnyk.design@gmail.com?subject=${subject}&body=${body}`;
});
