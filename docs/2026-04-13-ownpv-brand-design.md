# OwnPalosVerdes.com — Brand Design System

> **Date:** 2026-04-13
> **Purpose:** CSS design tokens, typography, color palette, spacing, and component patterns for OwnPalosVerdes.com
> **Aesthetic:** Luxury coastal real estate meets vintage National Park poster warmth. Compass-aligned but warmer — not sterile corporate, not beachy casual.
> **Reference:** The Lunada Bay travel poster is the north star. The site should feel like it lives in the same world as those posters.

---

## Color Palette

The v2 prototype was pure black/white/gray — too cold. The poster art revealed the real palette: warm coastal tones derived from the PV landscape.

### Primary Colors

```css
:root {
  /* -- Core -- */
  --midnight:       #1A2332;   /* Deep navy — replaces pure black. Headers, nav, footer backgrounds */
  --ink:            #2C3E50;   /* Dark slate — body text, primary content */
  --stone:          #4A5568;   /* Warm gray — secondary text, captions */

  /* -- Accent -- */
  --ocean:          #1B6B93;   /* Deep Pacific blue — primary accent, links, CTAs */
  --cove:           #2BA4B4;   /* Turquoise — hover states, highlights, from the poster water */
  --sunset:         #D4784A;   /* Warm terracotta/sunset — secondary accent, warm CTAs */
  --gold:           #C8A44E;   /* Muted gold — premium accents, badges, borders */

  /* -- Neutrals -- */
  --sand:           #F5F0E8;   /* Warm cream — page background, card backgrounds */
  --linen:          #FAF7F2;   /* Near-white warm — alternate section backgrounds */
  --parchment:      #EDE6D8;   /* Warm tan — borders, dividers, subtle backgrounds */
  --driftwood:      #B8A99A;   /* Warm medium gray — borders, inactive elements */

  /* -- Surface -- */
  --white:          #FFFFFF;   /* Pure white — card surfaces, modals */
  --poster-border:  #F2EDE4;   /* Cream border matching poster frame treatment */
}
```

### Color Usage Rules

| Element | Color | Why |
|---------|-------|-----|
| Page background | `--sand` or `--linen` | Warm cream, not harsh white — matches poster border |
| Body text | `--ink` | Dark slate, easier on eyes than pure black |
| Headings | `--midnight` | Deep navy, authoritative but warm |
| Links / primary CTA | `--ocean` | Pacific blue — on-brand, accessible |
| Hover / active states | `--cove` | Turquoise pop — from the poster water |
| Secondary CTA / warm accent | `--sunset` | Terracotta — warmth, urgency without red |
| Premium badges / gold accents | `--gold` | DRE#, stats, award badges |
| Section dividers | `--parchment` | Subtle warm line, not harsh gray |
| Nav / footer background | `--midnight` | Dark, elegant, Compass-aligned |
| Card backgrounds | `--white` | Clean contrast against cream page |
| Poster card overlays | `rgba(26, 35, 50, 0.7)` | Midnight at 70% over poster images |

### Dark Sections (Neighborhood grid, hero overlay)

```css
.section-dark {
  background: var(--midnight);
  color: var(--linen);
}
.section-dark .heading { color: var(--white); }
.section-dark .subtext { color: var(--driftwood); }
.section-dark .accent  { color: var(--gold); }
```

---

## Typography

### Font Stack

```css
:root {
  /* -- Display — for headlines, hero text, poster-adjacent typography -- */
  --font-display: 'DM Serif Display', Georgia, 'Times New Roman', serif;

  /* -- Heading — for section titles, card titles, navigation -- */
  --font-heading: 'DM Sans', system-ui, -apple-system, sans-serif;

  /* -- Body — for paragraphs, descriptions, UI text -- */
  --font-body: 'DM Sans', system-ui, -apple-system, sans-serif;

  /* -- Accent — for eyebrows, tags, small caps, badges -- */
  --font-accent: 'DM Sans', system-ui, sans-serif;
}
```

**Why DM Serif Display + DM Sans:** The v2 prototype already uses this pairing. DM Serif Display has the warm editorial authority that matches the poster typography. DM Sans is clean and modern for body text. Both are Google Fonts, free, and fast-loading.

### Type Scale

```css
:root {
  /* -- Display sizes -- */
  --text-hero:    clamp(3rem, 6vw, 5rem);       /* Hero headline only */
  --text-display: clamp(2.2rem, 4vw, 3.5rem);   /* Section headlines */

  /* -- Heading sizes -- */
  --text-h1:      clamp(1.8rem, 3vw, 2.5rem);   /* Page titles */
  --text-h2:      clamp(1.4rem, 2.5vw, 2rem);   /* Section subtitles */
  --text-h3:      1.25rem;                        /* Card titles */
  --text-h4:      1.1rem;                         /* Subsection titles */

  /* -- Body sizes -- */
  --text-body:    0.95rem;    /* Default body text */
  --text-body-lg: 1.05rem;   /* Lead paragraphs, featured text */
  --text-small:   0.85rem;   /* Captions, metadata */
  --text-micro:   0.72rem;   /* Eyebrows, tags, legal */

  /* -- Line heights -- */
  --leading-tight:   1.15;   /* Display/hero text */
  --leading-heading: 1.3;    /* Headings */
  --leading-body:    1.8;    /* Body text — generous for readability */
  --leading-micro:   1.4;    /* Small text */

  /* -- Letter spacing -- */
  --tracking-tight:  -0.01em;  /* Display text */
  --tracking-normal:  0;       /* Body */
  --tracking-wide:    0.08em;  /* Eyebrows, tags */
  --tracking-caps:    0.15em;  /* All-caps text */
}
```

### Typography Patterns

```css
/* Hero headline — poster-adjacent grandeur */
.hero-title {
  font-family: var(--font-display);
  font-size: var(--text-hero);
  font-weight: 400;
  line-height: var(--leading-tight);
  color: var(--white);
  font-style: italic;  /* DM Serif Display italic is gorgeous */
}

/* Section eyebrow — small caps above headings */
.section-eyebrow {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  color: var(--stone);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.section-eyebrow::before {
  content: '';
  display: block;
  width: 28px;
  height: 1px;
  background: var(--driftwood);
}

/* Section heading — authoritative but warm */
.section-heading {
  font-family: var(--font-display);
  font-size: var(--text-display);
  font-weight: 400;
  line-height: var(--leading-heading);
  color: var(--midnight);
}
.section-heading em {
  font-style: italic;  /* Italics for emphasis within headings */
}

/* Body text — generous line height, warm color */
.body-text {
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: 300;
  line-height: var(--leading-body);
  color: var(--ink);
}

/* Card title — clean sans-serif */
.card-title {
  font-family: var(--font-heading);
  font-size: var(--text-h3);
  font-weight: 600;
  color: var(--midnight);
}

/* Stat number — display serif for impact */
.stat-number {
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 400;
  line-height: 1;
  color: var(--white);
}

/* Legal / DRE / Compass disclaimer */
.legal-text {
  font-family: var(--font-body);
  font-size: var(--text-micro);
  line-height: var(--leading-micro);
  color: var(--stone);
  letter-spacing: var(--tracking-wide);
}
```

---

## Spacing System

8px base grid. Everything is a multiple of 8.

```css
:root {
  --space-xs:   0.25rem;   /*  4px */
  --space-sm:   0.5rem;    /*  8px */
  --space-md:   1rem;      /* 16px */
  --space-lg:   1.5rem;    /* 24px */
  --space-xl:   2rem;      /* 32px */
  --space-2xl:  3rem;      /* 48px */
  --space-3xl:  4rem;      /* 64px */
  --space-4xl:  6rem;      /* 96px — section padding */
  --space-5xl:  8rem;      /* 128px — hero padding */
}
```

### Section Spacing

```css
.section         { padding: var(--space-4xl) var(--space-2xl); }
.section-compact { padding: var(--space-3xl) var(--space-2xl); }
.section-hero    { padding: var(--space-5xl) var(--space-2xl); }
```

### Content Width

```css
:root {
  --width-content: 1100px;  /* Main content max-width */
  --width-narrow:  720px;   /* Text-heavy sections */
  --width-wide:    1400px;  /* Full-bleed image grids */
}
```

---

## Layout Patterns

### Navigation

```css
nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  height: 68px;
  padding: 0 var(--space-2xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(26, 35, 50, 0.95);  /* midnight at 95% */
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(200, 164, 78, 0.15);  /* subtle gold line */
}
```

- **Logo:** AREA | Compass lockup (white variant) left-aligned
- **Links:** Small caps, `--tracking-caps`, `--driftwood` color → `--white` on hover
- **CTA button:** "Contact Angelique" — outlined in `--gold`, fills `--gold` on hover
- **Mobile:** Hamburger menu, slide-in panel with `--midnight` background

### Hero Section

```css
.hero {
  height: 100vh;
  min-height: 700px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  padding: var(--space-5xl) var(--space-2xl);
}
```

- Full-bleed background image (sunset coastline or poster art)
- Dark gradient overlay from bottom (transparent → `rgba(26, 35, 50, 0.8)`)
- Hero title in `--font-display` italic, white
- Subtitle in `--font-body` light, `--driftwood`
- CTA buttons: primary (filled `--ocean`) + ghost (outlined `--white`)

### Poster Card Grid (Neighborhoods)

```css
.poster-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;  /* thin gap mimics poster frames side by side */
  background: var(--parchment);
}

.poster-card {
  position: relative;
  aspect-ratio: 2/3;  /* matches poster format */
  overflow: hidden;
}

.poster-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
  filter: saturate(0.95);
}

.poster-card:hover img {
  transform: scale(1.03);
  filter: saturate(1.1);
}

.poster-card-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: var(--space-lg);
  background: linear-gradient(transparent, rgba(26, 35, 50, 0.85));
}

.poster-card-name {
  font-family: var(--font-display);
  font-size: var(--text-h3);
  color: var(--white);
}

.poster-card-stat {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--driftwood);
  letter-spacing: var(--tracking-wide);
}
```

- **Desktop:** 3 columns, 2px gaps
- **Tablet:** 2 columns
- **Mobile:** 1 column, full-width poster cards

### Content Cards (Schools, Market Reports)

```css
.content-card {
  background: var(--white);
  border: 1px solid var(--parchment);
  border-radius: 4px;
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.content-card:hover {
  box-shadow: 0 8px 32px rgba(26, 35, 50, 0.12);
}

.content-card-image {
  aspect-ratio: 3/2;
  object-fit: cover;
}

.content-card-body {
  padding: var(--space-lg);
}
```

### Gated Download CTA

```css
.gate-cta {
  background: var(--midnight);
  border: 1px solid var(--gold);
  padding: var(--space-3xl) var(--space-2xl);
  text-align: center;
}

.gate-cta-heading {
  font-family: var(--font-display);
  font-size: var(--text-h2);
  color: var(--white);
  margin-bottom: var(--space-md);
}

.gate-cta-sub {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--driftwood);
  margin-bottom: var(--space-xl);
}

.gate-cta a {
  display: inline-block;
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding: 14px 32px;
  background: var(--sunset);
  color: var(--white);
  text-decoration: none;
  transition: background 0.2s;
}

.gate-cta a:hover {
  background: var(--ocean);
}
```

---

## Button System

```css
/* Primary — filled, warm action */
.btn-primary {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding: 12px 28px;
  background: var(--ocean);
  color: var(--white);
  border: none;
  transition: background 0.2s, transform 0.15s;
}
.btn-primary:hover {
  background: var(--cove);
  transform: translateY(-1px);
}

/* Secondary — outlined, elegant */
.btn-secondary {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding: 12px 28px;
  background: transparent;
  color: var(--ocean);
  border: 1px solid var(--ocean);
  transition: background 0.2s, color 0.2s;
}
.btn-secondary:hover {
  background: var(--ocean);
  color: var(--white);
}

/* Ghost — on dark backgrounds */
.btn-ghost {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding: 12px 28px;
  background: transparent;
  color: var(--white);
  border: 1px solid var(--driftwood);
  transition: border-color 0.2s, color 0.2s;
}
.btn-ghost:hover {
  border-color: var(--white);
  color: var(--white);
}

/* CTA — warm, high-intent action (mailto, download) */
.btn-cta {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  font-weight: 600;
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding: 14px 32px;
  background: var(--sunset);
  color: var(--white);
  border: none;
  transition: background 0.2s;
}
.btn-cta:hover {
  background: #BF6A3F;  /* darker sunset */
}
```

---

## Image Treatment

### Photo Overlays

```css
/* Warm desaturation for consistency across photo sources */
.photo {
  filter: saturate(0.9) brightness(0.95) contrast(1.02);
}

/* Poster images — slightly boosted saturation */
.poster-image {
  filter: saturate(1.05) contrast(1.05);
}

/* Dark overlay for text readability on images */
.image-overlay {
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(26, 35, 50, 0.3) 50%,
    rgba(26, 35, 50, 0.85) 100%
  );
}
```

### Poster Frame Treatment (for neighborhood cards)

```css
.poster-frame {
  border: 3px solid var(--poster-border);
  border-radius: 4px;
  box-shadow:
    0 2px 8px rgba(26, 35, 50, 0.1),
    inset 0 0 0 1px rgba(26, 35, 50, 0.05);
}
```

---

## Responsive Breakpoints

```css
/* Mobile first — default styles are mobile */

/* Tablet */
@media (min-width: 768px) {
  .poster-grid { grid-template-columns: repeat(2, 1fr); }
  .section { padding: var(--space-3xl) var(--space-xl); }
}

/* Desktop */
@media (min-width: 1024px) {
  .poster-grid { grid-template-columns: repeat(3, 1fr); }
  .section { padding: var(--space-4xl) var(--space-2xl); }
}

/* Wide */
@media (min-width: 1400px) {
  .poster-grid { grid-template-columns: repeat(4, 1fr); }
}
```

---

## Animations

Subtle, purposeful — not playful.

```css
/* Scroll reveal — elements fade up on intersection */
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Nav shadow on scroll */
nav.scrolled {
  box-shadow: 0 2px 16px rgba(26, 35, 50, 0.15);
}

/* Poster card hover — subtle zoom + saturation boost */
.poster-card:hover img {
  transform: scale(1.03);
  filter: saturate(1.1);
}

/* Link underline grow */
a.underline-grow {
  text-decoration: none;
  background-image: linear-gradient(var(--ocean), var(--ocean));
  background-position: 0% 100%;
  background-repeat: no-repeat;
  background-size: 0% 1px;
  transition: background-size 0.3s ease;
}
a.underline-grow:hover {
  background-size: 100% 1px;
}
```

---

## Footer

```css
footer {
  background: var(--midnight);
  color: var(--driftwood);
  padding: var(--space-3xl) var(--space-2xl);
  border-top: 1px solid rgba(200, 164, 78, 0.2);  /* subtle gold */
}
```

**Footer content:**
- AREA | Compass lockup (white)
- Angelique Lyle · DRE# 01475592
- 310.751.8335
- Equal Housing Opportunity logo
- Compass legal disclaimer (micro text)
- Social links (Instagram, LinkedIn)

---

## Compass Brand Alignment

The AREA/Compass brand is black-and-white minimalist. OwnPV extends this with warmth while staying compatible:

| Compass Element | OwnPV Adaptation |
|----------------|-------------------|
| Black backgrounds | `--midnight` (navy, not pure black) |
| White text | `--linen` or `--white` |
| Compass wordmark | Used in footer lockup, not modified |
| AREA mark | Used in nav and footer, not modified |
| Clean sans-serif | DM Sans (compatible weight/style) |
| Minimal decoration | Poster art IS the decoration — everything else stays clean |

**The poster art carries 100% of the visual personality.** The CSS framework, typography, and layout are intentionally restrained so the posters can shine. This is a gallery, not a carnival.
