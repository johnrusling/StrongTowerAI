# Strong Tower AI — Project Guide

## Project Overview
3-page marketing website for Strong Tower AI, an AI automation company targeting small to mid-sized businesses.

**Tagline:** AI Automation. Simple, Fast, Affordable.
**Live repo:** https://github.com/johnrusling/StrongTowerAI

## Pages
- `index.html` — Home (hero, services, why us, process, testimonials, CTA)
- `about.html` — About (story, mission/vision, values, team)
- `contact.html` — Contact (lead capture form, calendar booking widget, FAQ)
- `styles.css` — Shared stylesheet (all pages use this)
- `main.js` — Shared JS (navbar scroll, mobile menu, form submission, booking widget)

## Brand Guidelines

**Colors**
- Deep Navy: `#0D1B2A` (primary dark, hero/section backgrounds)
- Strong Blue: `#1565C0` (primary accent, buttons, links, highlights)
- Off-white: `#F5F8FC` (alternate section background, footer background)

**Typography**
- Font: Montserrat (Google Fonts) — Bold (700/800) for headings, Regular (400/500) for body

**Logo**
- `StrongTowerLogo-Transparent.svg` — main logo, renders in actual brand colors
- `Brand Board.png` — full brand board reference (colors, typography, usage examples)
- Logo is used at `height: 44px` in the navbar and `height: 40px` in the footer

## Key Design Decisions
- Navbar is white (`rgba(255,255,255,0.97)`) so the full-color SVG logo is visible
- Footer is off-white (`var(--off-white)`) for the same reason — logo shows in actual colors
- Home page logo instance does NOT use `filter: brightness(0) invert(1)` — it renders in brand colors as-is
- Hero and page-hero sections stay dark navy — logo does not appear there
- Scroll-triggered `.fade-up` animations on cards and section content

## Contact Page
- Lead capture form submits client-side with a success state (no backend wired up yet)
- Calendar booking widget is custom-built HTML/JS (no Calendly integration yet)
- Both need a real backend / Calendly embed when going to production

## To Do (not yet implemented)
- Connect lead form to a backend (Formspree, Netlify Forms, or custom)
- Replace booking widget with Calendly embed
- Add real contact details (email, phone)
- SEO meta tags and Open Graph images
- ~~Favicon~~ — added (`StrongTowerIcon.svg`, wired to all 3 pages)
