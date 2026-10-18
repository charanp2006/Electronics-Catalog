# 04 — Admin API Specification

Base: **`/api/v1/admin`** (JSON). Option A also exposes server-rendered routes at
**`/admin`** (HTML) that call the same services (§4.9).

## 4.1 Conventions
- All `/api/v1/admin/*` endpoints require an **admin** bearer token unless noted.
  Missing/invalid token → `401`; valid user but not admin → `403`.
- Request/response bodies are JSON (`application/json`).
- IDs in URLs are MongoDB `_id` hex strings unless a `slug` is stated.
- Dates are ISO-8601 UTC.
- Money is a JSON number (no currency symbol); 2-dp rounding server-side.
- Errors:
```json
{ "detail": "human readable message",
  "field_errors": { "image_urls": "invalid URL: 'foo'" } }
```
`field_errors` is optional and only present for validation failures (`422`/`400`).

## 4.2 Pagination, filtering, sorting (list endpoints)
Query params: `page` (≥1, default 1), `limit` (1–100, default 20), `q` (search),
plus per-module filters below. Response envelope:
```json
{ "items": [ … ], "total": 137, "page": 1, "limit": 20 }
```

---

## 4.3 Auth
### `POST /api/v1/admin/auth/login`
```json
// request
{ "email": "owner@example.com", "password": "…" }
// 200
{ "access_token": "<jwt scope=admin>", "token_type": "bearer",
  "admin": { "id": "…", "name": "Owner", "username": "owner", "email": "owner@example.com" } }
```
- `401` wrong credentials; **`403` correct credentials but `is_admin != true`**.

### `GET /api/v1/admin/auth/me` → `{ "id", "name", "username", "email", "is_admin" }`

### `POST /api/v1/admin/auth/logout` → `204` (client discards token; for Option A clears cookie)

---

## 4.4 Dashboard
### `GET /api/v1/admin/stats`
```json
{ "products": { "total": 12, "active": 12, "out_of_stock": 1, "low_stock": 3 },
  "orders": { "total": 4, "by_status": { "pending": 2, "shipped": 1, "delivered": 1 } },
  "reviews": { "total": 15, "hidden": 1 },
  "categories": 4, "brands": 8,
  "recent_orders": [ { "id": "…", "total": 1299.0, "status": "pending", "at": "…" } ] }
```

---

## 4.5 Products
| Method | Path | Purpose |
|---|---|---|
| GET | `/products` | list (admin; includes inactive) |
| POST | `/products` | create |
| GET | `/products/{id}` | detail (by `_id`) |
| PUT | `/products/{id}` | full update |
| PATCH | `/products/{id}` | partial update |
| DELETE | `/products/{id}` | delete (soft by default; `?hard=true` for hard, confirm) |

**List filters:** `q` (name/slug/brand/category), `category` (slug), `brand` (slug),
`is_active` (bool), `is_featured` (bool), `stock` (`out`|`low`), `sort`
(`newest|name|price|stock`).

**Create/update body** (`ProductWrite`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | str | ✅ | 1–200 |
| `slug` | str\|null | ⬜ | auto from name if empty; must be unique |
| `brand` | object\|id\|slug | ✅ | resolved + embedded `{_id,name,slug}` |
| `category` | object\|id\|slug | ✅ | resolved + embedded |
| `description` | str | ⬜ | ≤ 5000 |
| `price` | float | ✅ | > 0 |
| `discount_price` | float\|null | ⬜ | `0 < discount_price < price` |
| `stock` | int | ✅ | ≥ 0 |
| `image_urls` | str | ⬜ | **comma-separated URLs**; parsed → `images[]`, `image=images[0]` |
| `specifications` | `[{key,value}]` | ⬜ | strings |
| `is_active` | bool | ⬜ | default `true` |
| `is_featured` | bool | ⬜ | default `false` |

```json
// POST /products request
{ "name": "Acme 4K Monitor 27\"", "brand": "acme", "category": "monitors",
  "price": 32999, "discount_price": 29999, "stock": 12,
  "image_urls": "https://cdn/acme-1.jpg,https://cdn/acme-2.jpg",
  "specifications": [{ "key": "Panel", "value": "IPS" }],
  "is_active": true, "is_featured": true }
// 201 → full product document (as in 03 §1.24.1)
```
- `400` invalid image URL (`field_errors.image_urls`), duplicate slug (auto-suffixed, not an error),
  unknown brand/category, or `discount_price >= price`.
- On `price` change, service appends to `price_history`.

**Detail `GET /products/{id}`** returns the product plus `images`, `specifications`,
`reviews` (all statuses, each with `review_id`/`status`) and `price_history`.

---

## 4.6 Categories
| Method | Path | Purpose |
|---|---|---|
| GET | `/categories` | list (`q`) incl. `product_count` |
| POST | `/categories` | create |
| GET | `/categories/{id}` | detail |
| PUT | `/categories/{id}` | update |
| DELETE | `/categories/{id}` | delete (blocked with `409` if `product_count > 0`) |

Body: `{ "name": str(1–100), "slug": str|null, "description": str|null, "icon": str|null, "image": url|null }`.

## 4.6.1 Brands
Same shape as categories:
| Method | Path |
|---|---|
| GET | `/brands` (filters `q`) |
| POST | `/brands` |
| GET | `/brands/{id}` |
| PUT | `/brands/{id}` |
| DELETE | `/brands/{id}` (blocked `409` if `product_count > 0`) |

Body: `{ "name": str, "slug": str|null, "country": str|null, "logo": url|null }`.

---

## 4.7 Orders
| Method | Path | Purpose |
|---|---|---|
| GET | `/orders` | list all orders (admin) |
| GET | `/orders/{id}` | detail (items, customer, totals, history) |
| PATCH | `/orders/{id}/status` | change status |

**List filters:** `status`, `q` (order id or customer email/username), `from`/`to`
(dates), `user_id`, `sort` (`newest|total`).

```json
// GET /orders/{id}
{ "id": "…", "user": { "id": "…", "username": "demo", "email": "demo@example.com" },
  "items": [ { "product_id": "…", "slug": "…", "name": "…", "image": "…",
               "price": 79999.0, "discount_price": 74999.0, "quantity": 1 } ],
  "subtotal": 79999.0, "discount": 5000.0, "total": 74999.0,
  "status": "pending",
  "status_history": [ { "status": "pending", "at": "…", "by": "system" } ],
  "created_at": "…", "updated_at": "…" }
```
```json
// PATCH /orders/{id}/status  request
{ "status": "shipped" }
// 200 → updated order ; 400 if transition not allowed (e.g. delivered→processing)
```

---

## 4.8 Reviews (embedded moderation)
| Method | Path | Purpose |
|---|---|---|
| GET | `/reviews` | list across all products |
| PATCH | `/reviews/{product_id}/{review_id}` | edit / moderate one review |
| DELETE | `/reviews/{product_id}/{review_id}` | delete one review |

**List filters:** `product_id` (or `slug`), `status` (`published|hidden`), `rating`
(1–5), `q` (comment/username), sort (`newest|rating`).
List item includes `product_id, product_slug, product_name, review_id, username, rating,
comment, status, created_at`.

```json
// PATCH request (any subset)
{ "rating": 4, "comment": "Edited", "status": "hidden" }
// 200 → { updated review } (server recomputes product average_rating/total_reviews)
```
Both PATCH and DELETE recompute the product's `average_rating` and `total_reviews` from
**published** reviews only.

---

## 4.9 Option A — server-rendered routes (HTML)
Mounted at `/admin` on the API origin. Auth via `admin_session` cookie + CSRF token.

| Method | Path | Page/action |
|---|---|---|
| GET | `/admin/login` | login form |
| POST | `/admin/login` | authenticate → set cookie → 303 `/admin/dashboard` |
| GET | `/admin/logout` | clear cookie → 303 `/admin/login` |
| GET | `/admin/dashboard` | stats |
| GET | `/admin/products` | list (+ `?q&=category=&brand=&page=`) |
| GET | `/admin/products/new` | create form |
| POST | `/admin/products` | create → 303 list |
| GET | `/admin/products/{id}/edit` | edit form |
| POST | `/admin/products/{id}` | update → 303 list |
| POST | `/admin/products/{id}/delete` | delete → 303 list |
| GET/POST | `/admin/categories[/new|/{id}/edit|/{id}/delete]` | category CRUD |
| GET/POST | `/admin/brands[/new|/{id}/edit|/{id}/delete]` | brand CRUD |
| GET | `/admin/orders` | list |
| GET | `/admin/orders/{id}` | detail |
| POST | `/admin/orders/{id}/status` | update status → 303 detail |
| GET | `/admin/reviews` | list |
| POST | `/admin/reviews/{product_id}/{review_id}` | update/moderate → 303 list |
| POST | `/admin/reviews/{product_id}/{review_id}/delete` | delete → 303 list |

All mutating POSTs require a valid `csrf_token` (hidden field); invalid → `403`.
Every route except login requires an admin `admin_session`; otherwise `303 → /admin/login`.

## 4.10 AuthZ test matrix (must be automated)
| Endpoint group | no token | user token | admin token |
|---|---|---|---|
| `POST /admin/auth/login` | 200/401 | 200/401 | 200/401 |
| all other `/api/v1/admin/*` | 401 | **403** | 200 |
| all `/admin/*` (A), except login | 303→login | **303 → /admin/login** | 200 |
