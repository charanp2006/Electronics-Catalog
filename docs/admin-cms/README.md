# Admin CMS — Design Documentation

Design phase for the ElectroHub Admin CMS. **No implementation starts until this design
is approved.**

## Locked decisions (from stakeholder)
| # | Decision | Value |
|---|---|---|
| 1 | Delivery options | **Build BOTH** — Option A (server-rendered) **and** Option B (React SPA) |
| 2 | Approach preference | Recommended approach accepted |
| 3 | Modules in scope | **products, categories, brands, orders, reviews** |
| 4 | Image handling | **URL-based** — a single field accepting **comma-separated image URLs** |

## The two options (coexist, one shared backend)
| | **Option A — Server-rendered** | **Option B — React SPA** |
|---|---|---|
| UI lives at | backend `https://<api>/admin` | frontend `https://ecathub.netlify.app/admin-cms` |
| Rendering | FastAPI + Jinja2 templates (HTML) | React + existing design system |
| Auth transport | signed **HttpOnly cookie** `admin_session` | **Bearer token** `admin_token` in `localStorage` |
| API used | same admin **service layer** directly (form POST) | shared **JSON API** `/api/v1/admin/...` |
| Best for | simple, self-contained, no build step | rich UX, matches storefront theme |
| Recommended as primary | ✅ (fewer moving parts, isolated origin) | ✅ (nicer UX, reuses components) |

Both are guarded by the **same** `is_admin` user flag and the **same** admin
service/repository layer, so business logic is written **once**.

## Document index
| File | Contents |
|---|---|
| [`01-overview-and-scope.md`](01-overview-and-scope.md) | Goals, personas, in/out of scope, per-module feature list, NFRs |
| [`02-architecture.md`](02-architecture.md) | System diagram, shared domain layer, option A & B internals, routing, new deps |
| [`03-data-model.md`](03-data-model.md) | MongoDB changes: admin flag, product images, order status, review moderation, indexes |
| [`04-api-specification.md`](04-api-specification.md) | Full admin REST API (auth, products, categories, brands, orders, reviews) |
| [`05-ui-ux-design.md`](05-ui-ux-design.md) | Screen maps and wireframes for both options, design-token mapping |
| [`06-security.md`](06-security.md) | AuthN/AuthZ, cookies vs tokens, CSRF, rate limiting, audit log |
| [`07-implementation-plan.md`](07-implementation-plan.md) | Phased plan, file-by-file change list, tests, acceptance criteria |

## Visual mockups (open in a browser)
Static HTML reference for the visual template — no build step, open the gallery directly:
**[`mockups/index.html`](mockups/index.html)**

| | Option B (React SPA) | Option A (server-rendered) |
|---|---|---|
| login | [`option-b/login.html`](mockups/option-b/login.html) | [`option-a/login.html`](mockups/option-a/login.html) |
| dashboard | [`option-b/dashboard.html`](mockups/option-b/dashboard.html) | [`option-a/dashboard.html`](option-a/dashboard.html) |
| products | [`option-b/products.html`](mockups/option-b/products.html) | [`option-a/products.html`](option-a/products.html) |
| product form | [`option-b/product-form.html`](option-b/product-form.html) | [`option-a/product-form.html`](option-a/product-form.html) |
| categories | [`option-b/categories.html`](option-b/categories.html) | [`option-a/categories.html`](option-a/categories.html) |
| brands | [`option-b/brands.html`](option-b/brands.html) | [`option-a/brands.html`](option-a/brands.html) |
| orders | [`option-b/orders.html`](option-b/orders.html) | [`option-a/orders.html`](option-a/orders.html) |
| order detail | [`option-b/order-detail.html`](option-b/order-detail.html) | [`option-a/order-detail.html`](option-a/order-detail.html) |
| reviews | [`option-b/reviews.html`](option-b/reviews.html) | [`option-a/reviews.html`](option-a/reviews.html) |

Shared theme: [`mockups/mockup.css`](mockups/mockup.css). Open
[`mockups/index.html`](mockups/index.html) in a browser for the gallery.

## Status
- **Phase:** design (this directory).
- **Next:** review + sign-off, then implementation per `07-implementation-plan.md`.
