(() => {
  const storageKey = 'webbitti_consent_v1';
  const panel = document.querySelector('[data-cookie-panel]');
  if (!panel) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag(){ window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied',
    ad_personalization: 'denied', functionality_storage: 'granted', security_storage: 'granted',
    wait_for_update: 500
  });

  const config = window.WEBBITTI_TRACKING || {};
  let tagLoaded = false;
  const validId = (value) => /^(G|AW)-[A-Z0-9-]+$/i.test(value || '');
  const loadGoogleTag = () => {
    if (tagLoaded) return;
    const id = validId(config.gaId) ? config.gaId : (validId(config.adsId) ? config.adsId : '');
    if (!id) return;
    tagLoaded = true;
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
    document.head.appendChild(script);
    window.gtag('js', new Date());
    if (validId(config.gaId)) window.gtag('config', config.gaId, { anonymize_ip: true });
    if (validId(config.adsId)) window.gtag('config', config.adsId);
  };
  const applyConsent = (choice) => {
    const analytics = choice.analytics ? 'granted' : 'denied';
    const marketing = choice.marketing ? 'granted' : 'denied';
    window.gtag('consent', 'update', { analytics_storage: analytics, ad_storage: marketing, ad_user_data: marketing, ad_personalization: marketing });
    if (choice.analytics || choice.marketing) loadGoogleTag();
  };
  const save = (choice) => {
    localStorage.setItem(storageKey, JSON.stringify({ ...choice, savedAt: new Date().toISOString() }));
    applyConsent(choice);
    panel.hidden = true;
  };
  const show = () => { panel.hidden = false; };
  const options = panel.querySelector('[data-cookie-options]');
  const analyticsInput = panel.querySelector('[data-consent-analytics]');
  const marketingInput = panel.querySelector('[data-consent-marketing]');
  const saveButton = panel.querySelector('[data-cookie-save]');
  panel.querySelector('[data-cookie-accept]').addEventListener('click', () => save({ analytics:true, marketing:true }));
  panel.querySelector('[data-cookie-reject]').addEventListener('click', () => save({ analytics:false, marketing:false }));
  panel.querySelector('[data-cookie-customize]').addEventListener('click', () => { options.hidden = false; saveButton.hidden = false; });
  saveButton.addEventListener('click', () => save({ analytics:analyticsInput.checked, marketing:marketingInput.checked }));
  document.querySelectorAll('[data-cookie-settings]').forEach((button) => button.addEventListener('click', show));
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved && typeof saved.analytics === 'boolean' && typeof saved.marketing === 'boolean') applyConsent(saved); else show();
  } catch { show(); }

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!link) return;
    const href = link.getAttribute('href') || '';
    let name = link.matches('[data-package]') ? 'select_package' : link.classList.contains('button') ? 'cta_click' : '';
    if (href.startsWith('mailto:')) name = 'email_click';
    if (href.includes('wa.me/')) name = 'whatsapp_click';
    if (name) window.gtag('event', name, { link_text:(link.textContent || '').trim().slice(0,80), link_url:href });
  });
})();
