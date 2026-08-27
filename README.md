# Kateryna Kuropiatnyk — Portfolio

Professional bilingual portfolio for a Full-Stack Developer specialising in React, Node.js, Python automation and AI tools.

## Local preview

This is a dependency-free static site. Run a local HTTP server from the project directory:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

## Structure

- `index.html` — semantic content, SEO and project case studies
- `style.css` — responsive visual system
- `script.js` — language switcher, mobile navigation and safe mailto contact flow
- `img/` — favicon and social preview
- `impressum.html`, `datenschutz.html` — existing legal pages; review before launch

## Deployment

The project is a static site and can be deployed from the repository root on GitHub Pages, Cloudflare Pages, Netlify or Vercel. The intended production domain is `webbitti.com`; verify its DNS and TLS certificate before connecting it to a new host.

## Security

No server credentials belong in this repository. The former SMTP endpoint is retired. Rotate any credential that was previously committed or uploaded, then remove it from repository history before making the repository public.

## Pre-launch checklist

- Verify legal notice and privacy policy with current operator details.
- Confirm the public LinkedIn profile URL and all four project repositories.
- Export `img/og-cover.svg` as a 1200×630 PNG if the target social platform does not render SVG previews.
- Test email links, keyboard navigation, responsive layouts and all external project links on production.
