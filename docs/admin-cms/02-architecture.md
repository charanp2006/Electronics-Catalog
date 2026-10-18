# 02 — Architecture

## 2.1 Principles
1. **One backend, one domain layer.** All admin business logic lives in
  `repositories/` + a new `services/admin_*` (or extended repositories). Neither UI
  contains business rules.
2. **One identity model.** An admin is a normal `users` document with `is_admin: true`.
   Both options authenticate the same way (email + password → JWT) and are authorized by
   the same `require_admin` dependency.
- Option A adds a **cookie adapter** over the JWT; Option B uses the **Bearer** token directly.
- **Storefront untouched.** Public endpoints keep working; admin changes to shared
  collections are the only interaction.

## 1.9 High-level diagram
```
                        ┌───────────────────────────────────────────┐
                        │            MongoDB (electrohub_nosql)      |
                        │  users products categories brands orders   |
                        │  carts wishlist audit_logs                 |
                        └───────────────▲───────────────────────────┘
                                        │ (one shared client)
                                        │
                    ┌───────────────────┴───────────────────┐
                    │        Admin domain layer             │
                    │  repositories/* + services/admin/*    │
                    │  schemas/admin/*  |  require_admin     │
                    └───────▲───────────────────────▲───────┘
                            │                        │
        ┌───────────────────┴────────┐   ┌───────────┴────────────────────┐
        │ OPTION A (server-rendered) │   │ OPTION B (React SPA)           │
        │ FastAPI Jinja2 @ /admin    │   │ JSON API @ /api/v1/admin/*     │
        │ cookie: admin_session      │   │ Bearer: admin_token            │
        │ HTML forms (POST)          │   │ fetch/axios                    │
        └────────────────────────────┘   └────────────────────────────────┘
                 ▲                                    ▲
                 │ browser                            │ browser
        https://<api>/admin            https://ecathub.netlify.app/admin-cms
```

## 1.9.1 The shared admin domain layer (write once)
| Layer | Location | Responsibility |
|---|---|---|
| Repositories | `backend/app/repositories/{product,category,brand,order,user}.py` | Extend with admin ops (`create`, `update`, `delete`, `list_admin`, `set_status`, …). Inherit `BaseRepository` (keeps read retry). |
| Services | `backend/app/services/admin/` | Cross-cutting rules: slug uniqueness, image URL parsing, price-history on price change, order status transitions, review moderation, audit logging. |
| Schemas | `backend/app/schemas/admin/` | Pydantic request/response models per module. |
| Auth | `backend/app/core/security.py` (+ `app/core/admin_auth.py`) | `get_admin_user` / `require_admin`, cookie helpers for Option A. |

> Rationale: Option A and Option B must never diverge. Any rule (e.g. "slug must be
> unique", "images parsed from CSV") lives in the service layer; both callers use it.

## 1.10 Option A — server-rendered (Jinja2)
- Mounted by the **backend** at `/admin` (own router `app/admin/`), **outside**
  `API_V1_PREFIX`.
- Auth: `POST /admin/login` verifies credentials + `is_admin`, then sets a **signed
  HttpOnly cookie** `admin_session` (JWT, `SameSite=Lax`, `Secure` in prod, `Path=/admin`).
  A `GET /admin/logout` clears it.
- CSRF: double-submit token — a `csrf_token` cookie + hidden form field, validated on
  every mutating POST (see `06-security.md`).
- Pages render server-side via `Jinja2Templates`; mutations are HTML form POSTs that
  call services then **redirect** (PRG pattern) with a flash message.
- Assets: a single small static CSS that imports the same design tokens (no Vite build).
- No dependence on the React app or its origin → fully isolated.

```
app/admin/
  __init__.py
  routes.py            # GET pages + POST actions
  deps.py              # current_admin() from cookie, csrf()
  templating.py        # Jinja2Templates(directory=...)
  templates/
    base.html
    login.html
    dashboard.html
    products/{list,form}.html
    categories/{list,form}.html
    brands/{list,form}.html
    orders/{list,detail}.html
    reviews/list.html
    partials/{flash,table,image_field,status_badge}.html
  static/admin.css
```

## 1.11 Option B — React SPA
- Route `…/admin-cms/*` inside the existing React app, using a dedicated **AdminLayout**
  (no storefront Navbar/Footer/StatusBar).
- Auth: calls `POST /api/v1/admin/auth/login`, stores `admin_token` in `localStorage`
  under a distinct key (`electrohub_admin_token`), attaches `Authorization: Bearer` via a
  dedicated axios instance.
- Route guard `<RequireAdmin>` redirects to `/admin-cms/login` when missing/invalid.
- Reuses existing UI primitives (`Field`, `Blocks`, `Frame`, `States`) and Tailwind tokens.

```
frontend/src/
  admin/
    AdminApp.jsx            # nested routes + AdminLayout + guard
    AdminLayout.jsx
    adminApi.js             # axios instance (admin token) + endpoints
    AdminAuthContext.jsx
    pages/
      Login.jsx  Dashboard.jsx
      Products.jsx  ProductForm.jsx
      Categories.jsx  Brands.jsx
      Orders.jsx  OrderDetail.jsx
      Reviews.jsx
    components/
      DataTable.jsx  AdminField.jsx  ImageUrlsField.jsx  SlugField.jsx  ConfirmDialog.jsx
```

## 1.12 Routing map
| Surface | URL | Served by |
|---|---|---|
| Storefront | `/`, `/products`, … | React (Netlify) — unchanged |
| Admin (A) login | `GET/POST <api>/admin/login` | FastAPI |
| Admin (A) pages | `GET <api>/admin/{dashboard,products,categories,brands,orders,reviews}` | FastAPI |
| Admin (A) actions | `POST <api>/admin/{module}/...` | FastAPI |
| Admin (B) SPA | `/admin-cms/...` | React (Netlify) |
| Admin JSON API | `<api>/api/v1/admin/...` | FastAPI |

## 1.13 Auth model (shared)
1. `users` gains `is_admin: bool` (default `false`) and `role: "customer" | "admin"`.
2. `get_admin_user` reuses the existing bearer/JWT check **plus** `is_admin is True`;
   otherwise `403 Forbidden`. Missing/invalid token → `401`.
3. Admin token payload adds `"scope": "admin"` so a storefront user token can never be
   used to reach admin endpoints (and vice-versa the admin token works on storefront
   too, which is acceptable since admin is a superset user).
4. Option A derives the same identity from the cookie instead of the header, calling the
   same `get_admin_user` core.

## 1.14 Dependency / config changes
| Change | Where | Notes |
|---|---|---|
| `jinja2` added | `backend/requirements.txt` | required by Option A `Jinja2Templates` |
| `ADMIN_SESSION_COOKIE`, `ADMIN_COOKIE_SECURE`, `ADMIN_CSRF_*` | `backend/app/core/config.py` | cookie/CSRF settings |
| `FRONTEND_ORIGIN` / CORS | `config.py` | verify Netlify origin already allowed (it is the storefront origin) |
| `is_admin`/`role` on users | data + seed | seed `demo` as admin for local testing |
| `audit_logs` collection | data | written by services |
| No new frontend deps | — | reuse axios/react-router/motion already present |

## 1.15 Sequence — admin login (both options)
```
Client ──POST credentials──▶ verify_password + user.is_admin
        ◀─ Option A: Set-Cookie admin_session=<jwt>; 303 → /admin/dashboard
        ◀─ Option B: 200 {access_token, admin:{...}} ; store in localStorage
```

## 1.16 Sequence — product create with image URLs
```
Form/JSON {name, price, image_urls:"a, b"}
   ▼
schema validation (admin/ProductCreate)
   ▼
service.create_product():
   - slug = slugify(name) unless provided; ensure unique (append -2, -3 …)
   - images = parse_image_urls(csv); image = images[0] | None
   - brand/category: resolve ref by id/slug, embed {_id,name,slug}
   - price_history = [] (or seed if discount)
   - insert + audit_log("product.create")
   ▼
Option A: 303 redirect → list (flash "saved")
Option B: 201 {product}
```

## 1.17 Deployment notes
- Option A requires **no** Netlify change; it is part of the API deploy.
- Option B requires **no** backend change beyond the API; it ships with the site build.
- Both work on the current free hosts. (See `docs/14-connection-hardening-and-cold-starts.md`
  for cold-start/keep-alive context.)
