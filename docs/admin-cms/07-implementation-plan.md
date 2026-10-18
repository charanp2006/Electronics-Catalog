# 07 — Implementation Plan

Design-first: this plan is executed **after** sign-off. Work is phased so each phase is
independently testable and deployable.

## 7.1 Phase overview
| Phase | Deliverable | Depends on |
|---|---|---|
| **0. Foundation** | Admin flag + `require_admin` + admin JSON auth (`/api/v1/admin/auth/*`), config, seed/migration | — |
| **1. Catalog API** | Admin services + API for **products, categories, brands** (incl. image CSV field) | 0 |
| **2. Orders & Reviews API** | Admin services + API for **orders** (status) and **reviews** (moderation) + dashboard stats | 0,1 |
| **3. Option B (React SPA)** | `/admin-cms` login, layout, dashboard, all module pages | 1,2 |
| **4. Option A (Jinja2)** | `/admin` server-rendered pages + actions + CSRF | 1,2 |
| **5. Hardening** | audit logs, rate limiting, security headers, flash messages | 0–4 |
| **6. QA & docs** | full test suite, manual pass, update README/AGENTS | all |

Phases 3 and 4 are independent and can be built in either order (both need 1–2).

## 7.2 File-by-file change list
### Backend — new
| File | Purpose |
|---|---|
| `app/core/admin_auth.py` | `get_admin_user`/`require_admin`, admin token helpers, cookie + CSRF helpers |
| `app/services/admin/__init__.py` | package |
| `app/services/admin/images.py` | `parse_image_urls`, `format_image_urls` |
| `app/services/admin/slug.py` | `slugify`, `unique_slug` |
| `app/services/admin/products.py` | create/update/delete/list, price-history, review recompute |
| `app/services/admin/catalog.py` | category + brand services |
| `app/services/admin/orders.py` | list/get/set_status (transition rules), backfill helper |
| `app/services/admin/reviews.py` | list/moderate/delete across products |
| `app/services/admin/stats.py` | dashboard aggregates |
| `app/services/admin/audit.py` | `log(actor, action, entity, …)` |
| `app/schemas/admin/*.py` | request/response models per module |
| `app/api/v1/admin/__init__.py` + `auth.py, products.py, categories.py, brands.py, orders.py, reviews.py, stats.py` | JSON API |
| `app/admin/__init__.py, routes.py, deps.py, templating.py` | **Option A** server-rendered router |
| `app/admin/templates/**.html`, `app/admin/static/admin.css` | **Option A** UI |
| `scripts/migrate_admin.py` | idempotent data migration (admin flag, order status, review ids) |
| `tests/test_admin_auth.py`, `test_admin_products.py`, `test_admin_catalog.py`, `test_admin_orders.py`, `test_admin_reviews.py`, `test_admin_option_a.py` | test suites |

### Backend — modified
| File | Change |
|---|---|
| `app/main.py` | include `admin` JSON routers under `API_V1_PREFIX`; mount Option A `/admin` router + static; security-headers middleware |
| `app/core/config.py` | add admin cookie/CSRF/rate-limit settings |
| `app/core/security.py` | add optional `scope` to `create_access_token`; keep storefront behaviour |
| `app/repositories/product.py` | admin ops: `list_admin`, `create`, `update`, `delete`, `recompute_rating`, `find_review` |
| `app/repositories/category.py`, `brand.py` | `create/update/delete/get_by_id`, keep `product_count` |
| `app/repositories/order.py` | set `status`/`status_history` on create; `list_admin`, `get_by_id`, `set_status` |
| `app/repositories/user.py` | `set_admin`, helpers |
| `app/schemas/product.py` | optionally add `images: list[str]` (additive) |
| `seed.py` | create `demo` as admin; set order status; stamp `review_id`/`status` on reviews |
| `requirements.txt` | add `jinja2` |

### Frontend — new (`frontend/src/admin/`)
`AdminApp.jsx`, `AdminLayout.jsx`, `adminApi.js`, `AdminAuthContext.jsx`, `RequireAdmin.jsx`,
`components/{DataTable,AdminField,ImageUrlsField,SlugField,ConfirmDialog,StatusBadge}.jsx`,
`pages/{Login,Dashboard,Products,ProductForm,Categories,Brands,Orders,OrderDetail,Reviews}.jsx`.

### Frontend — modified
| File | Change |
|---|---|
| `src/App.jsx` | add `path="/admin-cms/*"` → `<AdminApp/>` (outside storefront `Layout`) |

## 7.3 Detailed task breakdown (first phases)
### Phase 0
1. Add `is_admin`/`role` to seed; grant `demo` admin.
2. `admin_auth.py` + `scope` in token; `get_admin_user`.
3. `POST/GET /api/v1/admin/auth/{login,me,logout}` + `schemas/admin/auth.py`.
2. Migration script + run locally.
2. Tests: `401/403/200` matrix for `/auth/me`.

### Phase 1
1. `slug.py`, `images.py` (+ unit tests: dedupe, invalid URL, empty).
2. Product admin service + repository ops; price history; review recompute.
2. Category/Brand services with `409` on non-empty delete.
3. Routers + schemas; wire into `main.py`.
4. Tests: create product with CSV images → `image`/`images` correct; slug auto-unique;
   discount validation; category/brand delete blocked.

### Phase 2
3. Orders: `set_status` transition rules + `status_history`; list/get with customer join.
4. Reviews: list across `$unwind` pipeline; `PATCH`/`DELETE` by `(product_id, review_id)`;
   recompute product rating; ensure storefront filters hidden.
5. Stats endpoint.
6. Tests incl. illegal transition → `400`, hidden review recompute.

### Phase 3 — Option B
7. `adminApi.js` + `AdminAuthContext` + `RequireAdmin`; route in `App.jsx`.
8. `AdminLayout` + `DataTable` + module pages + `ImageUrlsField`.
9. Manual pass + build (`npm run build`) + lint.

### Phase 4 — Option A
10. `Jinja2Templates`, `base.html`+`admin.css`, login + cookie + CSRF.
11. List/form templates per module; PRG redirects + flash.
12. Manual pass; assert non-admin redirects and CSRF `403`.

## 7.3.1 Definition of done per phase
- Code merged, `pytest` green, new endpoints covered by auth tests.
- Frontend phases: `npm run build` + `npm run lint` clean.
- No secret logged; `git status` shows only intended files.

## 7.4 Testing strategy
| Layer | Tool | Focus |
|---|---|---|
| Services | pytest | image parse, slugify/unique, price history, transitions, recompute |
| Repositories | pytest (mongo test db) | create/update/delete, admin lists |
| API | pytest + `httpx`/`TestClient` | status codes, authz matrix, validation, pagination |
| Option A | pytest + TestClient | cookie set/clear, CSRF reject, redirects |
| Option B | manual + build/lint | flows, guards, responsive |

Seed an isolated test DB (or fixtures with cleanup) so tests don't touch dev data.

## 7.5 Acceptance criteria (traceable to `01 §1.8`)
1. Non-admin gets `401/403` (API) or redirect (Option A) on every admin route. ✅ tests
2. Product created with CSV image URLs appears on storefront with correct primary image.
3. Category/brand create/edit/delete reflect in storefront filters; delete blocked when in use.
4. Any order viewable; status moves only along allowed transitions.
5. A hidden/deleted review disappears from the storefront and rating recomputes.
6. 1–5 work via **both** `/admin` and `/admin-cms`.

## 7.6 Risks & mitigations
| Risk | Mitigation |
|---|---|
| Option A (`/admin`) on free host cold start | keep-alive `/health` (see `docs/14-…`); login page is light |
| Reviews embedded → listing across products is a `$unwind` | fine at this data scale; index/paginate; revisit only if huge |
| Slug collisions during rename | `unique_slug` with numeric suffix; covered by tests |
| Destructive deletes | soft delete default; hard delete behind explicit confirm + audit |
| Cookie/CSRF mistakes | centralized helpers + dedicated tests |

## 7.7 Open questions (confirm before Phase 0)
1. **Primary vs peer**: build both as peers (per request) — should Option A also get the
   full niceties (thumbnails, filtering) or stay intentionally minimal?
2. **Hard delete**: default to **soft delete** (set `is_active=false`) with an explicit
   "hard delete" confirm — OK?
3. **Category/brand delete**: block when products reference them (`409`) vs reassign — OK to block?
4. **Admin provisioning**: seed/env only (no UI to promote users) — acceptable?
4. **Admin token on storefront**: allow admin token to also call storefront routes (recommended), or restrict to admin scope only?
5. **Route names**: Option A `/admin`, Option B `/admin-cms` — confirm.

## 7.8 Suggested commit/PR sequence
1. `chore(admin): admin flag, require_admin, admin auth API`
2. `feat(admin): product/category/brand admin API`
3. `feat(admin): orders + reviews admin API + stats`
4. `feat(admin-ui): option B react admin`
5. `feat(admin): option A jinja2 admin + CSRF`
| `chore(admin): audit logs, rate limiting, headers`
| `test/docs: admin suites + docs/AGENTS update`
