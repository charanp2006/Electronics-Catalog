# 05 — UI / UX Design

Two surfaces, one visual language. Both use the existing **MongoDB Forest** tokens so
the admin feels like the same product.

## 5.1 Design tokens (shared, from `frontend/src/index.css`)
| Token | Value | Use |
|---|---|---|
| `bg` | `#001e2b` | page background |
| `panel` / `panel-2` | `#062a37` / `#112733` | cards, table headers |
| `ink` | `#e8edeb` | primary text |
| `dim` | `#889397` | secondary text, labels |
| `phos` | `#00ed64` | primary actions, active nav, focus |
| `phos-dim` | `#00684a` | hover of phos surfaces |
| `sig` | `#71f6ba` | accent values |
| `alert` | `#ff6960` | destructive, errors |
| `line` / `line-2` | `#1c2d38` / `#3d4f58` | borders |
| fonts | `JetBrains Mono`, `VT323` (display) | body / headings |

Reusable atoms already in the app: `.panel`, `.frame` (corner ticks), `.btn`,
`.btn-danger`, `.label`, `Field`, `SecHead`, `Stat`, `Leader`, `Loader`, `EmptyState`,
`ErrorState`. Admin screens reuse these; Option A ships an equivalent `admin.css`.

### Status colors
`pending`→dim · `processing`→sig · `shipped`→phos · `delivered`→phos (filled) ·
`cancelled`→alert ; reviews `published`→phos · `hidden`→dim.

## 5.2 Information architecture (both options)
```
Admin
├─ Login
├─ Dashboard            (KPIs + recent orders)
├── Catalog
│   ├─ Products         (list → form)
│   ├─ Categories       (list + inline form/modal)
│   └─ Brands           (list + modal)
├── Orders              (list → detail with status stepper)
└── Reviews             (list across products, moderate)
```

## 5.2.1 Option B — React screens (mounted at `/admin-cms`)
```
┌ AdminLayout ────────────────────────────────────────────────┐
│ ┌───────────────┐  ┌──────────────────────────────────────┐ │
│ │ [EH] ADMIN    │  │  topbar: breadcrumb · search · admin ▾ │
│  ├── dashboard  │  ├──────────────────────────────────────┤
│  │ ▸ catalog    │  │                                        │
│  │   products   │  │            page content                │
│  │   categories │  │            (table / form)              │
│  │   brands     │  │                                        │
│  │ orders       │  │                                        │
│  │ reviews      │  │                                        │
│  │ ─────────    │  │                                        │
│  │ view site ↗  │  │                                        │
│  │ logout       │  │                                        │
└───────────────────────────────────────────────────────────────┘
```
- **AdminLayout** — left sidebar (fixed 220px, collapses to icon bar < 1024px), top bar
  with breadcrumb + admin menu. **No storefront Navbar/Footer/StatusBar.**

### 5.1.1 Login (`/admin-cms/login`)
```
┌───────────────────────────────┐
│  [00] ADMIN // AUTH           │
│  > email    [ owner@acme.io ] │
│  > password [ ••••••••      ] │
│  [ authenticate ]   ← phos
│  !! error line (if any)
└───────────────────────────────┘
```
Centered framed panel; on success route to `/admin-cms` (dashboard); on `403` show
"this account is not an administrator".

### 5.1.1 Dashboard
```
[01] OVERVIEW                              [stats rec]
┌ PRODUCTS ─┐ ┌ ORDERS ──┐ ┌ REVIEWS ─┐ ┌ CATALOG ─┐
│ 12 active │ │ 4 total  │ │ 15 total │ │ 4 cat    │
│ 1 out     │ │ 2 pending│ │ 1 hidden │ │ 8 brands │
└───────────┘ └──────────┘ └──────────┘ └──────────┘
[02] RECENT ORDERS                              ...
  #id            total      status      when
```

### DataTable pattern (products/categories/brands/orders/reviews)
```
[01] PRODUCTS           [q search………]   [+ new product]
┌───────────────────────────────────────────────────────────────┐
│ name           brand    category   price    stock  active  ⋯  │
│ Samsung S24    Samsung  Phones     79999    12     ●      edit │
│ …                                                              │
└───────────────────────────────────────────────────────────────┘
[< prev]  page 1 / 7  [next >]
```
- Row actions: `edit`, `delete` (delete opens a `ConfirmDialog`).
- Empty → `EmptyState`; error → `ErrorState`; loading → `Loader`.

### Product form (create/edit)
```
[01] PRODUCT  [new | edit: acme-4k-monitor]
name*         [………………………………]
slug          [auto → acme-4k-monitor]   (leave blank to auto)
brand*        [select ▾]     category* [select ▾]
description   [textarea ………………………]
price*        [32999]        discount  [29999]
stock*        [12]           flags     [x] active  [ ] featured
image urls    [https://a.jpg, https://b.jpg, https://c.jpg]
              ⓘ comma-separated. first = primary.
              preview: [img][img][img]
specifications: key/value rows  [+ add row]
[ save ]   [ cancel ]     (danger) [ delete ]   (edit only)
```
`ImageUrlsField` shows inline thumbnails and flags invalid URLs live.

### Orders
List (filter by status tabs `all|pending|processing|shipped|delivered|cancelled`).
Detail shows items table, totals (`subtotal`, `discount`, `total`), customer block, and a
**status stepper** with a "set status" select limited to allowed transitions.

### Reviews
List with product link, stars, comment excerpt, status badge. Row actions: `hide/publish`,
`edit`, `delete`. Filter by `status`, `rating`, product.

---

## 5.2 Option A — server-rendered (Jinja2) screens
Same information architecture and same table/form shapes, rendered as HTML. Layout uses a
top bar + left nav; forms are plain `<form method="post">` with hidden `csrf_token`.

```
┌ ELECTROHUB :: ADMIN ──────────────────── owner ▾  [logout] ┐
│ dashboard │ products │ categories │ brands │ orders │ reviews│
├─────────────────────────────────────────────────────────────┤
│  {flash message: "product saved"}                            │
│  page content (table / form)                                 │
└──────────────────────────────────────────────────────────────┘
```
- **`base.html`**: head imports `admin.css`, top bar, nav (active state), flash partial.
- **list.html** per module: search form (GET), table, pagination links, `+ new` button.
- **form.html** per module: fields; `image_urls` `<input>`/`<textarea>` with helper text;
  specification rows rendered as `spec_key[]` / `spec_value[]` inputs.
- **orders/detail.html**: items table, totals, customer, and a status `<form>` per allowed
  transition (button posts to `/admin/orders/{id}/status`).
- **reviews/list.html**: rows loop `product_id`/`review_id`; buttons POST to the
  moderate/delete routes.
- Flash messages via a short-lived signed/secure cookie or query param, rendered by the
  `flash` partial (see `06-security.md`).
- Deliverable is plain HTML → works with JS disabled, consistent with Option A's goals.

## 5.3 Shared component contract
| Concept | Option A | Option B |
|---|---|---|
| Search | `<form method=get>` | debounced input → refetch |
| Pagination | `?page=n` links | prev/next + state |
| Confirm delete | dedicated confirm page or `onsubmit` `confirm()` | `ConfirmDialog` |
| Image CSV field | `<textarea name=image_urls>` + hint | `ImageUrlsField` with previews |
| Spec rows | repeated `key[]`/`value[]` inputs | dynamic `+ add row` |
| Status badge | `.badge--phos/.badge--dim/...` in `admin.css` | `StatusBadge` using tokens |
| Empty/error/loading | includes | `EmptyState`/`ErrorState`/`Loader` |

## 5.4 Interaction rules
- **Every destructive action requires explicit confirmation.**
- Save buttons disable while submitting; errors render inline at the field where possible.
- Success feedback: Option A flash banner; Option B toast (reuse the `notice` pattern).
- Unsaved-changes guard on navigate away from product/category/brand forms (Option B).
- Keyboard: `Esc` closes dialogs; `Enter` submits simple forms.

## 5.5 Responsive behavior
- ≥1024px: side nav + full tables.
- 640–1023px: collapsible nav; tables scroll horizontally; forms single-column.
- <640px (Option B only; Option A targets desktop): stacked cards, sticky save bar.

## 5.6 Accessibility
- Inputs have `<label>`/`aria-label`; tables use `<th scope>`.
- Visible focus ring using `phos`; color is never the only status signal (badge text included).
- Live region announces flash/toast messages.
