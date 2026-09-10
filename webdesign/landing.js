document.querySelector('#year').textContent = new Date().getFullYear();

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
