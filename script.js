const root = document.documentElement;
const langButton = document.querySelector('.lang');
const menuButton = document.querySelector('.menu');
const nav = document.querySelector('#nav');

function setLanguage(lang) {
  root.lang = lang;
  document.querySelectorAll('[data-de][data-en]').forEach((node) => {
    node.textContent = node.dataset[lang];
  });
  document.querySelectorAll('[data-placeholder-de]').forEach((node) => {
    node.placeholder = node.dataset[`placeholder${lang[0].toUpperCase()}${lang.slice(1)}`];
  });
  langButton.textContent = lang === 'de' ? 'EN' : 'DE';
  langButton.setAttribute('aria-label', lang === 'de' ? 'Switch to English' : 'Auf Deutsch wechseln');
  localStorage.setItem('site-language', lang);
}

langButton.addEventListener('click', () => setLanguage(root.lang === 'de' ? 'en' : 'de'));
setLanguage(localStorage.getItem('site-language') === 'en' ? 'en' : 'de');

menuButton.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});
nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  nav.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
}));

document.querySelector('#contact-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const subject = encodeURIComponent(`Project enquiry: ${data.get('type')}`);
  const body = encodeURIComponent(`Name: ${data.get('name')}\nEmail: ${data.get('email')}\nProject type: ${data.get('type')}\nBudget: ${data.get('budget')}\n\nProject brief:\n${data.get('message')}`);
  window.location.href = `mailto:kuropiatnyk.design@gmail.com?subject=${subject}&body=${body}`;
});

document.querySelector('#year').textContent = new Date().getFullYear();

const projectImages = [
  ['project-antique.jpg', 'Startseite des E-Commerce-Projekts Antique Treasures'],
  ['project-ai-builder.jpg', 'Projekt-Setup im AI Website Builder'],
  ['project-housing.jpg', 'Dashboard des Vienna Housing Monitor'],
  ['project-restaurant.jpg', 'Startseite des O.S.K Restaurant Website Concept']
];
document.querySelectorAll('.project-visual').forEach((visual, index) => {
  const image = document.createElement('img');
  image.src = `img/${projectImages[index][0]}`;
  image.alt = projectImages[index][1];
  image.width = 1440;
  image.height = 900;
  image.loading = 'lazy';
  visual.replaceChildren(image);
});

const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
  if (entry.isIntersecting) entry.target.classList.add('visible');
}), { threshold: .08 });
document.querySelectorAll('.section, .project').forEach((node) => observer.observe(node));
