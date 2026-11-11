# nivasgallo.com

Portfolio of Nivas Gallo, Lead Product Designer.

## Structure
- `src/pages/` – page bodies (homepage and case studies)
- `src/site.css`, `src/site.js` – shared styles and behaviour (Sage palette, light/dark, kinetic titles, motion, 8px grid)
- `src/img/` – WebP images
- `src/your-odds.payload.json` – the Your Odds+ case study, AES-GCM encrypted (PBKDF2, 600k iterations). The readable source is not in this repository.
- `src/build.py` – assembles the pages
- `tools/` – image conversion, contrast checking and the encryption script

## Build
```
python3 src/build.py --deploy   # writes the static site to dist/
```
Every push to `main` builds `dist/` and deploys it (see `.github/workflows/deploy.yml`).

## Accessibility
Targets WCAG 2.2 AAA: 7:1 text contrast in both themes, 48px targets, skip link, landmarks, reduced-motion support.
