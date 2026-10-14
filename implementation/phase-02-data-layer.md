# Phase 2 — Data Layer: Modeling, Indexing & Seeding

## Goal
Finalized MongoDB document model with verified, realistic seed data.

## Conceptual Bridge (SQL → NoSQL)
| SQL | MongoDB decision |
|---|---|
| Product → Brand (FK) | Reference + denormalize `brand.name` |
| Product → Specs (table) | **Embed** array |
| Product → Reviews (table) | **Embed** array (small count) |
| Product → Price history | **Embed** array |
| Order → OrderItems (table) | **Embed** items (order = snapshot) |
| User → Cart (session) | **Embed** cart items |

Takeaway: SQL is normalized + JOINs + ACID; MongoDB is denormalized + embedded docs + flexible schema.

## Collections
`products`, `brands`, `categories`, `users`, `carts`, `orders` (reviews & price_history embedded in product).

## Product Document (reference)
```json
{
  "slug": "samsung-galaxy-s24",
  "name": "Samsung Galaxy S24",
  "brand": { "_id": "…", "name": "Samsung" },
  "category": { "_id": "…", "name": "Smartphones" },
  "description": "…",
  "price": 74999, "discount_price": 62999, "stock": 15,
  "images": ["…"], "rating": 4.5,
  "specifications": [{ "key": "Display", "value": "6.2-inch AMOLED" }],
  "reviews": [{ "user_id": "…", "username": "demo", "rating": 5, "comment": "…", "created_at": "…" }],
  "price_history": [{ "old_price": 74999, "new_price": 62999, "changed_at": "…" }],
  "average_rating": 4.5, "total_reviews": 10,
  "is_active": true, "is_featured": true,
  "created_at": "ISODate()", "updated_at": "ISODate()"
}
```

## Steps
1. Finalize schemas for all collections (see `docs/07-database-design.md`).
2. Expand `backend/seed.py` → **12 products**, 4 categories, 8 brands, demo user with **hashed** password (`demo/demo12345`).
3. Populate nested `specifications`, `reviews`, `price_history`, `average_rating`.
4. Create indexes: `slug` unique, `name`, `brand._id`, `category._id`, `price`, `is_active`, `users.email` unique.
5. Keep seeding idempotent (drop/create), print counts.
6. Run `python seed.py`, inspect in Compass/`mongosh`.

## Verification
- [ ] products: 12, categories: 4, brands: 8, users: 1
- [ ] Sample product has populated nested arrays
- [ ] Indexes exist; `slug` and `email` unique enforced
- [ ] Re-running seed is idempotent
