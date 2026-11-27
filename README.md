# Teleminds website (2026 redesign)

Static site. No framework, no npm. Needs Python 3.

    python3 build.py                                  # builds dist/
    python3 -m http.server 8080 --directory dist      # preview at http://localhost:8080

Upload `dist/` to any static host (Netlify, Vercel, Cloudflare Pages, cPanel).

## Editing content

| What | Where |
|---|---|
| Offices, phones, addresses, Naukri link, form endpoint | `src/data/site.json` |
| Job openings (each links to its Naukri listing) | `src/data/jobs.json` |
| Blog posts | `src/blog/<slug>.json` |
| Page copy and layout | `build.py` |
| Colours, type, spacing | `assets/css/styles.css` (tokens at the top) |

Rebuild after every edit.

## Before launch

- Set `formEndpoint` (e.g. Formspree) or `enquiryEmail` in `site.json`. Until then the form tells visitors to call.
- Add a phone number for Shaila Tower and confirm the Delhi number.
- Add openings to `jobs.json`. With none listed, Careers links to the Naukri company page.

URLs match the old WordPress site (`/services/`, `/contact-us/`, `/blog/<slug>/`) so existing search rankings carry over. `/careers/` and `/brand/` (brand guide, noindex) are new.

Logo: the original Teleminds Infotech logo, unchanged (`assets/img/logo.png`).
3D icons: Microsoft Fluent 3D emoji, MIT licence.
Photos: Pexels (free licence) in `assets/photos/`. Swap in real Teleminds office photos when you have them, keeping the same file names.
Reference-site analysis (REA captures) is in `../tools/rea-out/`.
