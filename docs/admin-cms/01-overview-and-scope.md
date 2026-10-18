# 01 — Overview & Scope

## 1.1 Goal
Give ElectroHub operators a secure, self-contained **Admin CMS** to manage the
catalog, orders and reviews without touching MongoDB Compass or the seed script.
Two presentation options (A: server-rendered, B: React SPA) are delivered on top of a
**single shared admin backend**, so behaviour is identical regardless of which UI is used.

## 1.2 Personas
| Persona | Description | Needs |
|---|---|---|
| **Admin** | Trusted operator (e.g. store owner) | Full CRUD on catalog, order status, review moderation |
| **Storefront visitor** | Existing public user | Unaffected; never sees admin routes/data |
| **Developer/maintainer** | You | Clear separation, testable services, easy local run |

There is **one** admin role in v1 (no granular roles). Multi-role RBAC is explicitly out
of scope but the data model leaves room for it (`role` field, §03).

## 1.3 Scope

### In scope
**Products**
- List with search, filter (category, brand, active/featured), sort, pagination.
- Create / edit / delete (soft-delete via `is_active`, plus hard delete with guard).
- Fields: name, slug, brand, category, description, price, discount_price, stock,
  `specifications[]` (key/value), **image URLs (comma-separated)**, featured toggle,
  active toggle.
- Price change automatically appends to `price_history`.
- View/curate embedded reviews per product.

| Categories | Brands |
|---|---|
| Create / edit / delete, name, slug, description, icon, image URL | Full CRUD: name, slug, country, logo URL |
| Slug auto-generated + uniqueness enforced | Same |

| Orders | Reviews |
|---|---|
| List (filter by status, user, date, search by id) | List across all products (filter by product / rating / status) |
| View detail (items, totals, customer) | Moderate: **publish**, **hide**, edit rating/comment, delete |
| Update **status**: pending → processing → shipped → delivered / cancelled | Bulk hide/publish (optional, phase 2) |
| View status history | See author + timestamp + product link |

## 1.3.1 Image handling (locked decision)
URL-based only — **no file uploads**.
- One text input per form: **comma-separated URLs**, e.g.
  `https://cdn/a.jpg, https://cdn/b.jpg, https://cdn/c.jpg`
- Parsing rules (shared helper, used by both options and the API):
  1. Split on commas, trim whitespace, drop empties.
  2. De-duplicate while preserving order.
  3. Validate each is `http(s)://...`; reject the whole payload on the first invalid URL
     with a field-level error (`image_urls: "invalid URL: '<x>'"`).
  4. `images` = parsed list; `image` = first element (primary) or `null` if empty.
```
"a.jpg, b.jpg ,,a.jpg"  ->  images: ["a.jpg","b.jpg"], image: "a.jpg"
"https://x/1.png"       ->  images: ["https://x/1.png"], image: "https://x/1.png"
""                      ->  images: [], image: null
```

## 1.4 Out of scope (v1)
- File/image uploads or a media library.
- Multi-admin roles/permissions, teams, invitations.
- Customer/user management beyond what orders/reviews reference.
- Bulk product import/export (CSV), analytics dashboards.
- Payments, shipping integrations, email notifications.
- i18n.

## 1.5 Feature matrix (by module × option)
| Capability | Shared API | Option A (SSR) | Option B (React) |
|---|---|---|---|
| Login / logout / session | ✅ | ✅ cookie | ✅ token |
| Products list + search/filter | ✅ | ✅ | ✅ |
| Product create / edit / delete | ✅ | ✅ | ✅ |
| Comma-separated image field | ✅ | ✅ | ✅ |
| Categories CRUD | ✅ | ✅ | ✅ |
| Brands CRUD | ✅ | ✅ | ✅ |
| Orders list / detail / status | ✅ | ✅ | ✅ |
| Reviews list + moderation | ✅ | ✅ | ✅ |
| Dashboard summary | ✅ | ✅ | ✅ |

## 1.6 Non-functional requirements
| Area | Requirement |
|---|---|
| **Security** | Admin-only access enforced server-side on **every** admin route; no privileged data in public endpoints; see `06-security.md` |
| **Consistency** | One admin service layer; both UIs call it (A directly, B via JSON API) |
| **Performance** | List endpoints paginated (default 20, max 100); indexed queries (see `03`); first paint < 1s on warm host |
| **Responsiveness** | Option A: usable on desktop; Option B: responsive (admin is desktop-first, usable on tablet) |
| **Theming** | Both reuse the MongoDB-Forest tokens (`--color-bg #001e2b`, `--color-phos #00ed64`, …). Option A ships a small standalone stylesheet with the same tokens. |
| **Reliability** | Reads inherit `BaseRepository` retry; writes use safe update patterns. |
| **Observability** | Admin actions appended to an `audit_logs` collection (who/what/when). |
| **Testability** | Repositories/services unit-tested; admin API tested with pytest + httpx; authorization tests mandatory. |

## 1.6.1 Non-functional: accessibility & responsiveness
- Semantic forms, labelled inputs, keyboard-operable tables and modals.
- Focus-visible outlines using the `phos` token; min 4.5:1 contrast (ink on bg).
- Destructive actions require explicit confirm.

## 1.7 Assumptions & constraints
- Existing stack is fixed: FastAPI + PyMongo + Pydantic v2; React 19 + Vite + Tailwind v4.
- Auth currently issues a JWT (`sub`, `exp`) via `app/core/security.py`; admin auth
  extends this rather than replacing it.
- The frontend and backend are deployed separately (Netlify + Render), so Option A runs
  on the API origin and Option B on the site origin.
- Reviews are **embedded** in `products.reviews` today (no standalone collection) — see
  `03-data-model.md` for the moderation strategy.

## 1.8 Success criteria
1. Admin can log in, and a non-admin is rejected with 401/403 on every admin route.
2. Admin can create a product with comma-separated image URLs and see it on the storefront.
3. Admin can create/edit/delete categories and brands; changes reflect on storefront filters.
4. Admin can view any order and move it through the status lifecycle.
5. Admin can hide or delete a review and it disappears from the storefront.
6. Both Option A (`/admin`) and Option B (`/admin-cms`) deliver 1–5.
