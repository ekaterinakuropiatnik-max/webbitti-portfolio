document.querySelector('#year').textContent = new Date().getFullYear();

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
