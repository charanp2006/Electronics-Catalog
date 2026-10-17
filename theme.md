# ElectroHub — Theme & Design System

This document records the visual language of the ElectroHub frontend: the **original theme**,
the **active (MongoDB) theme**, and the complete **design pattern** (tokens, typography,
surfaces, components, motion) shared by both.

- Source of truth for tokens: `frontend/src/index.css` (`@theme` block + component classes).
- Interactive reference: open `theme.html` in a browser to see both themes side by side.

---

## 1. Theme identity

Two themes exist in this project. The **active** theme is applied across the site.

### Theme A — Phosphor Terminal *(original / legacy)*

A retro lab-terminal look: amber phosphor on near-black, CRT scanlines, pixel display font.

Also known as: **Amber CRT**, **Lab Scope**, **Cold Boot Terminal**, **Vintage Instrument**.

Vibe: oscilloscope / lab bench / DOS terminal. Signature amber glow on a cold charcoal canvas.

### Theme B — MongoDB Forest *(active)*
> Based on MongoDB's website / **LeafyGreen** design system.

A forest-dark terminal: neon MongoDB green on deep teal-black, bioluminescent glow.

Also known as: **Evergreen Terminal**, **MongoDB Forest Black**, **LeafyGreen Dark**, **Forest Scope**.

Vibe: "bioluminescent green growing in the dark." Keeps the terminal structure but swaps the
amber phosphor for MongoDB's signature neon green and the near-black for forest teal-black.

---

## 2. Colour palettes

### 2.1 Theme A — Phosphor Terminal (legacy)

| Token | Hex | Role |
| --- | --- | --- |
| `--color-bg` | `#07080A` | Page canvas (near-black) |
| `--color-panel` | `#0C0F12` | Surface / card |
| `--color-panel-2` | `#101417` | Raised surface / inputs |
| `--color-ink` | `#D8DCD4` | Primary text |
| `--color-dim` | `#79837C` | Secondary / muted text |
| `--color-phos` | `#FFB020` | **Amber accent** (brand) |
| `--color-phos-dim` | `#7A5410` | Muted amber (borders, hover) |
| `--color-sig` | `#3DDC84` | Success / in-stock green |
| `--color-alert` | `#FF5C5C` | Error / danger red |
| `--color-line` | `#1C2228` | Hairline border |
| `--color-line-2` | `#262D34` | Stronger border |
| field bg | `#080A0C` | Input background |
| field placeholder | `#4C554E` | Input placeholder |
| scrollbar track / thumb | `#0A0C0E` / `#232A31` | Scrollbar |
| text-on-accent | `#08090B` | Text on amber buttons |

### 2.2 Theme B — MongoDB Forest (active)

Values below are taken from MongoDB's LeafyGreen palette so the UI matches mongodb.com.

| Token | Hex | LeafyGreen name | Role |
| --- | --- | --- | --- |
| `--color-bg` | `#001E2B` | MDB Black | Page canvas (forest teal-black) |
| `--color-panel` | `#062A37` | *(between MDB Black & Gray/Dark 4)* | Surface / card |
| `--color-panel-2` | `#112733` | Gray/Dark 4 | Raised surface / inputs |
| `--color-ink` | `#E8EDEB` | Gray/Light 2 | Primary text |
| `--color-dim` | `#889397` | Gray/Base | Secondary / muted text |
| `--color-phos` | `#00ED64` | **MongoDB Green** | **Brand accent** |
| `--color-phos-dim` | `#00684A` | Green/Dark 2 | Muted green (borders, hover) |
| `--color-sig` | `#71F6BA` | Green/Light 1 | Success / in-stock (mint) |
| `--color-alert` | `#FF6960` | Red/Light 1 | Error / danger |
| `--color-line` | `#1C2D38` | Gray/Dark 3 | Hairline border |
| `--color-line-2` | `#3D4F58` | Gray/Dark 2 | Stronger border |
| field bg | `#001822` | *(darker than MDB Black)* | Input background |
| field placeholder | `#5C6C75` | Gray/Dark 1 | Input placeholder |
| scrollbar track / thumb | `#001822` / `#1C2D38` | — | Scrollbar |
| text-on-accent | `#001E2B` | MDB Black | Text on green buttons |

**Full LeafyGreen reference** (available for future use):
Green `#023430` `#00684A` `#00A35C` `#00ED64` `#71F6BA` `#C0FAE6` `#E3FCF7` ·
Gray `#112733` `#1C2D38` `#3D4F58` `#5C6C75` `#889397` `#C1C7C6` `#E8EDEB` `#F9FBFA` ·
Blue `#016BF8` `#006CFA` `#0498EC` · Yellow `#FFC010` · Red `#DB3030` `#FF6960` · Purple `#5C6CC0`.

### 2.3 Token migration map (A → B)

| Token | Phosphor Terminal | MongoDB Forest |
| --- | --- | --- |
| `--color-bg` | `#07080A` | `#001E2B` |
| `--color-panel` | `#0C0F12` | `#062A37` |
| `--color-panel-2` | `#101417` | `#112733` |
| `--color-ink` | `#D8DCD4` | `#E8EDEB` |
| `--color-dim` | `#79837C` | `#889397` |
| `--color-phos` | `#FFB020` | `#00ED64` |
| `--color-phos-dim` | `#7A5410` | `#00684A` |
| `--color-sig` | `#3DDC84` | `#71F6BA` |
| `--color-alert` | `#FF5C5C` | `#FF6960` |
| `--color-line` | `#1C2228` | `#1C2D38` |
| `--color-line-2` | `#262D34` | `#3D4F58` |

---

## 3. Typography

| Role | Font | Notes |
| --- | --- | --- |
| Body / UI / mono | **JetBrains Mono** | `--font-mono`; base size 14px, line-height 1.55 |
| Display / headings | **VT323** | `--font-display`; pixel/terminal headings, uppercase |

Loaded from Google Fonts in `frontend/index.html`. The monospace-first system is intentional:
every surface is a terminal readout.

> MongoDB's public site uses *MongoDB Value Serif* (hero), *Euclid Circular A* (UI) and
> *Source Code Pro* (code). Those are not freely distributable; ElectroHub keeps its terminal
> type system and adopts the MongoDB **colour** identity instead.

**Type scale (observed):**
`display` 8xl/6xl/4xl/3xl/2xl (VT323) · body `14px` · small `text-xs` (12px) ·
`.label` `0.62rem` UPPERCASE, `letter-spacing .28em` · chips `0.62rem`, tracking `.1em`.

---

## 3. Foundations — surfaces, borders, glow

- **Surfaces** — flat, no rounded corners by default. `.panel` = `--color-panel` + 1px
  `--color-line` border. `.panel-2` raises the fill.
- **Corner ticks** — `.frame` / `.frame-full` draw 7px accent corners (`::before`/`::after`)
  in `--color-phos` — the "instrument panel" signature.
- **Hairlines** — `.hairline` is a 1px gradient rule fading to transparent.
- **Borders** — `--color-line` (subtle) and `--color-line-2` (interactive/strong).
- **Glow** — `.glow` / `.glow-soft` are accent-tinted `text-shadow`; `.scanbar` has an accent
  `box-shadow`. All glow uses the accent colour (amber → green after migration).
- **Radii** — effectively `0` (square, technical). MongoDB's own site uses pills; this project
  intentionally keeps sharp corners for the terminal look.

---

## 3. Typography & spacing notes

- Base font-size `14px`, line-height `1.55`, letter-spacing `0.01em`.
- Labels/eyebrows: uppercase, `0.28em` tracking.
- Layout max width `1400px`; generous `space-y-14` section rhythm.

---

## 4. Design pattern — components

| Class / component | Purpose |
| --- | --- |
| `.panel` / `.panel-2` | Surface + raised surface |
| `.frame` / `.frame-full` | Accent corner ticks |
| `.hairline` | 1px fading divider |
| `.btn` / `.btn-primary` / `.btn-danger` | Controls (uppercase, tracked) |
| `.field` | Text input (accent focus ring) |
| `.label` | Uppercase micro-label |
| `.chip` | Bordered tag |
| `.link-underline` | Animated underline link |
| `.leader` | Dotted leader line (`flex:1`) |
| `.img-phos` | Desaturate → colour-on-hover image treatment |
| `.grid-bg` | 44px grid backdrop |
| `.grid-glow` / `.grid-glow-spot` | Glowing grid lines + traveling spotlight |
| `.blink` | Terminal cursor blink |
| `.scanbar` | Loading scan bar |
| `.crt-*` (`crt-overlay`, `crt-scanlines`, `crt-grain`, `crt-vignette`, `crt-flicker`) | CRT overlay stack |

**React building blocks** (`frontend/src/components/ui/`): `Frame`, `Reveal`, `Scramble`,
`CountUp`, `Blocks` (`SecHead`, `Metric`, `Leader`), `Field`, `GridBackdrop`.
**Layout:** `Navbar`, `Footer`, `StatusBar`, `Overlays`, `Layout`. `Marquee`/`Ticker` were removed.

---

## 5. Motion & interaction

| System | Used for |
| --- | --- |
| **Lenis** (`lenis/react`) | Global smooth scroll + scroll-to-top on route change |
| **Motion** (`motion/react`) | Page transitions, scroll reveals, stagger, filter drawer, **grid glow** |
| CSS keyframes | `blink`, `crt-flicker`, `scanbar`, `rise` |
| rAF / JS | `Scramble` (text decode), `CountUp` (number roll) |
| GSAP *(removed with marquee)* | previously the marquee loop |

**Grid backdrop** (`GridBackdrop.jsx`): a base grid, a rhythmic glow on every line
(`opacity` pulse), and a traveling spotlight that lights up the lines as it passes
(animated CSS custom properties `--gx`/`--gy` driving a radial mask + `drop-shadow` bloom).

---

## 6. Applying / switching a theme

All colour comes from the `@theme` tokens in `frontend/src/index.css`. Tailwind exposes them as
utilities (`bg-bg`, `text-ink`, `text-phos`, `border-line-2`, `text-sig`, `text-alert`, …).

**To switch back to Phosphor Terminal**, replace the `@theme` values:

```css
@theme {
  --color-bg: #07080a;
  --color-panel: #0c0f12;
  --color-panel-2: #101417;
  --color-ink: #d8dcd4;
  --color-dim: #79837c;
  --color-phos: #ffb020;
  --color-phos-dim: #7a5410;
  --color-sig: #3ddc84;
  --color-alert: #ff5c5c;
  --color-line: #1c2228;
  --color-line-2: #262d34;
}
```

Also revert the accent-tinted hardcoded values (all currently MongoDB green `rgba(0,237,100,…)`):
`.glow`, `.glow-soft`, `.sweep::after`, `.scanbar`, `.btn-primary` shadow, `.field:focus`
shadow → amber `rgba(255,176,32,…)`; `::selection` text and `.btn-primary` text → `#08090b`;
`.field` bg → `#080a0c`; placeholder → `#4c554e`; scrollbar → `#0a0c0e`/`#232a31`;
`index.html` `theme-color` → `#07080a`.

---

*Last updated alongside the MongoDB Forest migration.*
