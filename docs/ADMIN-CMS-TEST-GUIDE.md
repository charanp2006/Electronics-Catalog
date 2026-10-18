# ElectroHub Admin CMS — Local Test Guide

End-to-end manual test walkthrough for **both** admin UIs and the storefront.
Follow the sections in order. Every step says exactly what to run, what to open,
what to type, and what you should see.

---

## 0. Prerequisites

| Requirement | Check |
|---|---|
| Python deps installed | `cd backend && pip install -r requirements.txt` |
| Node deps installed | `cd frontend && npm i` |
| MongoDB running | **Local:** service on `27017`. **Or Atlas:** `backend/.env` has `ENV=atlas` |
| `.env` configured | `backend/.env` must define `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `SECRET_KEY`, `ENV` |

Current `.env` values used in this guide (as seeded):

```
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123
```

> The demo **customer** account (created by seed): `demo@example.com` / `demo12345`

### Reset the database any time
```bash
cd backend
python seed.py
```
This **drops and recreates** products (12), categories (4), brands (8), users (2), orders (3).
It prints the admin login when it finishes.

---

## 1. Start the servers (exact order)

Open **two separate terminals**.

### Terminal 1 — Backend (port 8000)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Wait for: `Uvicorn running on http://127.0.0.1:8000`

Verify: open <http://localhost:8000/health> → you should see `{"status":"ok","env":"..."}`

### Terminal 2 — Frontend (port 5173)
```bash
cd frontend
npm run dev
```
Wait for the Vite banner with `Local: http://localhost:5173/`

> Vite proxies `/api/**` → `http://localhost:8000`, so you never need to open
> port 8000 for the React app. Port 8000 is used directly only by Option A.

### Stop everything later
- Ctrl+C in both terminals, or
- kill the processes listening on 8000 / 5173.

---

## 2. The three apps at a glance

| App | URL | Who |
|---|---|---|
| Storefront (React) | <http://localhost:5173/> | customers |
| **Admin Option B** (React SPA) | <http://localhost:5173/admin-cms> | admins |
| **Admin Option A** (server-rendered) | <http://localhost:8000/admin> | admins |
| Backend health | <http://localhost:8000/health> | — |
| API root | <http://localhost:8000/docs> (Swagger) | — |

---

## 3. Admin login (both options)

Use the admin account printed by `seed.py`:
- **Email:** `admin@example.com`
- **Password:** `Admin@123`

Wrong password → error shown. Customer account (`demo@example.com`) → **rejected**
(Option A shows "Invalid credentials"; Option B gets HTTP 403/401).

After login you should land on the **Dashboard** of the respective option.

---

## 4. Option A — server-rendered admin (`:8000/admin`)

Plain HTML + CSS, cookie session, no build step. Dark terminal theme.

### Pages
| Page | URL |
|---|---|
| Login | `/admin/login` |
| Dashboard | `/admin/` |
| Products list | `/admin/products` |
| New product | `/admin/products/new` |
| Edit product | `/admin/products/{id}/edit` |
| Categories | `/admin/categories` |
| Brands | `/admin/brands` |
| Orders list | `/admin/orders` |
| Order detail | `/admin/orders/{id}` |
| Reviews | `/admin/reviews` |
| Logout | `/admin/logout` |

### Test each page

**Dashboard** — shows totals: products (active/low/out-of-stock), orders (revenue + per-status counts), reviews (published/hidden), categories/brands counts.

**Products → New Product** — form fields:
- Name, Slug (blank = auto from name), Brand (slug), Category (slug), Price, Discount Price, Stock, Image URLs (comma separated), Active / Featured checkboxes.

Use this dummy product (all fields):

| Field | Value |
|---|---|
| Name | `Sony WH-1000XM5 Dummy` |
| Slug | *(leave blank)* |
| Brand (slug) | `sony` |
| Category (slug) | `headphones` |
| Price | `34990` |
| Discount Price | `29990` |
| Stock | `7` |
| Image URLs | `https://picsum.photos/seed/xm5a/600/600, https://picsum.photos/seed/xm5b/600/600, https://picsum.photos/seed/xm5c/600/600` |
| Active | ✓ |
| Featured | ✓ |

Save → redirect back to list with green **"Created successfully."** flash.
The new product appears in the table with brand/category/price/stock.

Validation demos (should show a red error banner and keep your input):
- Brand = `not-a-brand` → *"brand not found: not-a-brand"*
- Discount Price ≥ Price → validation error
- Image URL = `not-a-url` → invalid URL error

**Products list → Edit** — change Price `34990` → `32990`, Save.
This appends an entry to the product's **price history** (visible on the storefront detail page and via the JSON API).

**Products list → Delete** — confirm dialog; product is **soft-deleted** (`is_active=false`) and disappears from the storefront but stays in the admin list marked Active=No.

**Categories** — left form creates; table lists with product counts.
- Create: Name `Gaming Monitors`, Slug blank → flash "Created successfully."
- Edit: click **Edit** on a row → form prefills → rename → Save.
- Delete: click **Delete** → confirm. Deleting an **in-use** category (e.g. `smartphones`) shows a red *"Cannot delete: N product(s) reference this category"* error (HTTP 409).

**Brands** — same pattern as Categories, extra fields Country + Logo URL.
- Create: Name `Framework`, Country `US`, Logo URL `https://picsum.photos/seed/fr/120/60`.
- Delete an in-use brand (e.g. `apple`) → blocked with error.

**Orders list → View** — detail page shows customer, items, totals, **status history**, and a "Move to" dropdown offering **only legal next states** (state machine):
- `pending` → processing | cancelled
- `processing` → shipped | cancelled
- `shipped` → delivered | cancelled
- `delivered` / `cancelled` → no further changes (message shown instead of form)

Update a pending order to `processing` → green flash "Saved successfully.", history gains a row.
An illegal transition is impossible via the dropdown (it is not offered); if forced (e.g. via curl) the page re-renders with *"Invalid status transition"*.

**Reviews** — table of all reviews across products (published + hidden).
- **Hide/Publish** button toggles status; the storefront then shows/hides it and the product's average rating **recomputes**.
- **Delete** removes the review permanently (confirm dialog).

**Logout** — clears the cookie → back to login with *"You have been logged out."*
Visiting `/admin/` after logout → 303 redirect to `/admin/login`.

**Security checks worth trying**
- Visit `/admin/` in a private/incognito window → redirect to login (no dashboard leak).
- Open `<http://localhost:8000/products>` (root, without `/admin`) → **404** (admin is not exposed at the root anymore).
- Response headers include `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`.

---

## 5. Option B — React SPA admin (`:5173/admin-cms`)

Same features as Option A, richer UX (matches the storefront's neon-green terminal theme), Bearer token in `localStorage`.

### Pages / routes
| Route | Page |
|---|---|
| `/admin-cms/login` | Login card |
| `/admin-cms` | Dashboard (stat cards, recent orders) |
| `/admin-cms/products` | Filterable table + soft/hard delete |
| `/admin-cms/products/new` | Create form |
| `/admin-cms/products/:id` | Edit form |
| `/admin-cms/categories` | Inline create/edit form + list |
| `/admin-cms/brands` | Inline create/edit form + list |
| `/admin-cms/orders` | Filter by status, search |
| `/admin-cms/orders/:id` | Detail + allowed-transition buttons + history |
| `/admin-cms/reviews` | Moderation (hide/publish/delete) |

### Test flows

1. **Login** with the same admin credentials → redirected to dashboard; the
   sidebar footer shows the admin email; token stored as
   `localStorage['electrohub_admin_token']` (check DevTools → Application).
2. **Dashboard** — stat tiles: products total/active/low/out, orders by status +
   revenue, reviews published/hidden, catalog counts, recent orders list.
3. **Products → New** — same dummy product as §4 (Image URLs is one comma-separated
   field). Save → appears in table; open the **storefront** at
   <http://localhost:5173/products> → the product is listed with the **first image**
   as its primary photo.
4. **Products filters** — try: search text, category, brand, `is_active`,
   `stock=low` / `stock=out`, sort options, pagination.
5. **Delete options** — soft delete (deactivate) is one click; **hard delete** asks
   for explicit confirmation (window.confirm) and removes the document.
6. **Categories/Brands** — create/edit in the left panel; the list shows product
   counts; deleting an in-use row shows a red 409 error banner.
7. **Orders** — change a pending order: `pending → processing → shipped → delivered`
   using the buttons shown on the detail page (illegal buttons are not rendered).
8. **Reviews** — hide a review, then open its product on the storefront: the review
   is gone and the star rating changed. Publish it again to restore.
9. **401 handling** — in DevTools, delete the token and click any page → you are
   redirected to `/admin-cms/login`.
10. **Logout** in the sidebar → token removed, back to login page.

---

## 6. Storefront verification (after admin changes)

Open <http://localhost:5173/> (log in as `demo@example.com` / `demo12345` for cart/orders):

| After you do this in admin… | Verify here |
|---|---|
| Create product (with images, featured) | Home hero featured strip; `/products` list; detail page shows gallery + price history |
| Soft-delete product | Disappears from `/products` and search |
| Price change | Detail page **price history** chart gains a point |
| Create category/brand | Filters on `/products` sidebar gain the new entry |
| Delete unused category/brand | Filter entry disappears |
| Hide review | Product detail review list + average rating update |
| Order status → shipped/delivered | Customer `/orders` page shows the new status |

Place a real order as demo: add items to cart → `/cart` → checkout. A new `pending`
order appears in **both** admin UIs (stock decrements automatically).

---

## 7. Quick API smoke (optional, curl)

```bash
# login
curl -s -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@123"}'

# use the returned access_token:
curl -s http://localhost:8000/api/v1/admin/stats -H "Authorization: Bearer <TOKEN>"
```

Full interactive API docs: <http://localhost:8000/docs> (admin endpoints under `/api/v1/admin`).

---

## 8. Automated tests

```bash
cd backend
python -m pytest tests/ -q
```
Expected: **56 passed**. The suite reseeds the DB before and after the run, so your
data is reset automatically. It covers the JSON admin authz matrix, catalog/orders/
reviews services, and the full Option A cookie/CSRF/redirect matrix.

Frontend:
```bash
cd frontend
npm run build   # must succeed
npm run lint    # exit 0 (style warnings only)
```

---

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| Seed crashes with "ADMIN_EMAIL and ADMIN_PASSWORD must be set" | Add them to `backend/.env` |
| Option A redirects to login forever | Session cookie is path-scoped to `/admin`; log in at `/admin/login`, don't strip cookies |
| 429 on admin login | 10 failed attempts / 15 min per IP+email — wait, or restart the backend (counter is in-process) |
| Frontend shows "Not Found" from API | Backend not running on 8000 — start Terminal 1 first |
| Port already in use | `netstat -ano | findstr ":8000 :5173"` then `taskkill /PID <pid> /F` |
| Want pristine demo data | `cd backend && python seed.py` |
