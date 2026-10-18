# 03 — Data Model Changes

MongoDB is schemaless; this document defines the **field contract** the admin layer
relies on, the changes to existing collections, and a safe migration path. All changes
are additive (no destructive rewrites) so the storefront keeps working during rollout.

## 3.1 Current shapes (as-is)
```jsonc
// users
{ "_id", "username", "name", "email", "password"/*bcrypt*/, "is_active", "created_at" }

// products
{ "_id", "name", "slug",
  "brand":    {"_id", "name", "slug"},
  "category": {"_id", "name", "slug"},
  "description", "price", "discount_price", "stock",
  "specifications": [ { "key", "value" } ],
  "reviews": [{ "user_id","username","rating","comment","created_at" }],
  "price_history": [{ "old_price", "new_price", "changed_at" }],
  "is_active": true, "is_featured": bool,
  "average_rating": 0, "total_reviews": 0,
  "image": "url|null", "images": ["url", ...],
  "created_at" }

categories : { _id, name, slug, description, icon, created_at }
brands     : { _id, name, slug, country, logo, created_at }
orders     : { _id, user_id, items:[{product_id,slug,name,image,price,discount_price,stock,quantity}],
               subtotal, discount, total, created_at }
carts      : { _id, user_id, items[], updated_at }
```

## 1.1 `users` — admin identity
| Field | Type | Default | Notes |
|---|---|---|---|
| `is_admin` | bool | `false` | primary authorization flag; checked by `require_admin` |
| `role` | string | `"customer"` | `"customer"` \| `"admin"`; future-proofing for roles |
| `updated_at` | datetime | `now()` | maintained on profile/admin edits |

Index: `{ is_admin: 1 }` (cheap admin lookup). `email`/`username` unique indexes already exist.

**Granting admin (no data migration tool needed for a single operator):**
```python
db.users.update_one({"email": "owner@example.com"},
                    {"$set": {"is_admin": True, "role": "admin",
                              "updated_at": datetime.now(timezone.utc)}})
```
Seed script will create `demo@example.com` with `is_admin: True` for local testing.

## 1.18 `products` — image URLs + review moderation
### Images (locked: URL-based CSV field)
The existing `image` (primary) + `images[]` (gallery) fields are **formalized**:
- `images: [url, …]` — ordered gallery, de-duplicated.
- `image: url | None` — always `images[0]` (primary) for storefront cards.
- No new fields required; the admin form maps a **comma-separated text field** to/from
  these two fields via `parse_image_urls()` / `format_image_urls()` (see §1.22).

### Review sub-document (embedded) — add moderation fields
Today reviews are embedded and unmoderated. Extend each element:
| Field | Type | Added | Purpose |
|---|---|---|---|
| `review_id` | string (uuid4 hex) | ✅ | **stable reference** independent of array index |
| `status` | `"published" | "hidden"` | ✅ | moderation state (default `published`) |
| `updated_at` | datetime | ✅ | last edit |
| `moderated_by` | string(user_id) | ✅ | who hid/published |
| `moderated_at` | datetime | ✅ | when |
| `user_id, username, rating, comment, created_at` | — | existing | unchanged |

- Public storefront endpoints must **filter `status == "published"`** (or missing, for
  legacy docs) when serializing reviews, and `total_reviews`/`average_rating` must be
  recomputed from **published** reviews only (service helper `recompute_rating(product)`).
- Admin moderate ops target a review by `review_id`.

**Why embedded (not a separate `reviews` collection)?**
The storefront already reads reviews from the product document in a single query; moving
them to a collection would require a join/`$lookup` for every product detail page.
Stable `review_id` solves the "index shifts when deleting" problem, so a separate
collection is unnecessary. (A future scale-out can extract them; not needed here.)

### Other product fields (admin-managed)
`name, slug, brand, category, description, price (float), discount_price (float|None),
stock (int), specifications[{key,value}], is_active (bool), is_featured (bool)`.
`price_history` is **append-only**, written by the service when `price` changes (see §1.23).

Indexes (existing unless noted): `slug` unique, `name`, `brand._id`, `category._id`,
`price`, `is_active`, **new:** `is_featured`, `{is_active:1, created_at:-1}`.

## 1.19 `orders` — status lifecycle
Current docs have no status. Add:
| Field | Type | Default | Notes |
|---|---|---|---|
| `status` | enum | `"pending"` | see lifecycle below |
| `status_history` | `[{status, at, by}]` | `[ {status:"pending", at: created_at, by:"system"} ]` | audit trail |
| `updated_at` | datetime | `now()` | |

**Lifecycle / allowed transitions** (enforced in `OrderService.set_status`):
```
pending ─▶ processing ─▶ shipped ─▶ delivered
   │            │            │
   └────────────┴────────────┴────▶ cancelled
delivered ─▶ (terminal)      cancelled ─▶ (terminal)
```
- Any non-terminal state may move to `cancelled`.
- Backwards moves are rejected with `400` (e.g. `delivered → processing`).
- New orders set `status:"pending"` at creation (update `OrderRepository.create_from_cart`).
- **Backfill:** existing orders without `status` are treated as `pending` by the reader
  and migrated once (idempotent) by the migration script.

Indexes: **new** `{status:1, created_at:-1}`, existing `user_id`.
Snapshot per item: `{product_id, slug, name, image, price, discount_price, stock, quantity}`
(read-only in admin; admin edits **status**, not line items).

## 1.20 `categories` & `brands`
Managed fields:
- `categories`: `name, slug, description, icon (string token), ` optionally `image` (URL).
- `brands`: `name, slug, country, logo (URL)`.
Add `updated_at` to both. Slugs unique (indexes already exist). **Delete rule:** block
deletion if `product_count > 0` (return `409` with the count), or offer "reassign then
delete" (phase 2). Admin list reuses the existing `product_count` computation.

## 1.21 `audit_logs` (new collection)
```
{ _id, actor_id, actor_username, action, entity, entity_id,
  summary: str, changes: {field: {from, to}} | null, at: datetime,
  ip: str | null, surface: "A" | "B" }
```
- `action` e.g. `product.create`, `product.update`, `order.status`, `review.hide`.
- Index `{at:-1}`, `{entity:1, entity_id:1}`, `{actor_id:1}`.
- Written best-effort by services (never blocks the operation; failures logged).

## 1.22 Image URL parsing (single source of truth)
`backend/app/services/admin/images.py`:
```python
def parse_image_urls(csv: str | None) -> list[str]:
    if not csv: return []
    out, seen = [], set()
    for part in csv.split(","):
        url = part.strip()
        if not url: continue
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError(f"invalid URL: '{url}'")
        if url not in seen:
            seen.add(url); out.append(url)
    return out

def format_image_urls(images: list[str] | None) -> str:
    return ", ".join(images or [])
```
Used by both options and the JSON API. Storefront `ProductList.image` stays the primary.

## 1.23 Slug & price-history rules (service layer)
- `slugify(name)`: lowercase, non-alphanumerics → `-`, collapse dashes, trim.
- If slug empty → derived from name; if taken, append `-2`, `-3`, … until unique
  (excluding the record itself when updating).
- On `price` change: if the value changed, append
  `{old_price, new_price: new, changed_at: now}` to `price_history` (skip on first create
  unless a discount exists).
- `average_rating`/`total_reviews` recomputed from **published** reviews only.

## 1.24 Migration & seeding plan
1. Add fields lazily (readers treat missing as documented defaults) — no blocking migration.
2. `backend/scripts/migrate_admin_cms.py` (idempotent):
   - set `is_admin:false, role:"customer"` where missing;
   - backfill `orders.status = "pending"` + `status_history` where missing;
   - assign `review_id`/`status:"published"` to legacy product reviews missing them;
   - build new indexes.
   Safe to re-run; prints a summary of changed counts.
- `seed.py` updated to create `demo` as admin and to set `status` on any seeded orders.
- Optionally grant a real admin via env (`ADMIN_EMAIL`) on startup (documented in `06-security.md`).

## 1.24.1 Sample admin-created product (target shape)
```json
{
  "_id": "ObjectId(...)",
  "name": "Acme 4K Monitor 27\"",
  "slug": "acme-4k-monitor-27",
  "brand": { "_id": "ObjectId(...)", "name": "Acme", "slug": "acme" },
  "category": { "_id": "ObjectId(...)", "name": "Monitors", "slug": "monitors" },
  "description": "…",
  "price": 32999.0,
  "discount_price": 29999.0,
  "stock": 12,
  "image": "https://cdn/acme-1.jpg",
  "images": ["https://cdn/acme-1.jpg", "https://cdn/acme-2.jpg"],
  "specifications": [{ "key": "Panel", "value": "IPS" }],
  "reviews": [],
  "price_history": [{ "old_price": 32999.0, "new_price": 29999.0, "changed_at": "…" }],
  "average_rating": 0,
  "total_reviews": 0,
  "is_active": true,
  "is_featured": false,
  "created_at": "…",
  "updated_at": "…"
}
```

## 1.25 Backward compatibility
- Extra fields are ignored by existing Pydantic schemas (`extra="ignore"` where set) and
  by the storefront UI.
- Reviews without `status` are treated as published; orders without `status` as pending.
- `ProductList`/`ProductDetail` schemas may optionally add `images: list[str]` (gallery)
  — additive, non-breaking.
