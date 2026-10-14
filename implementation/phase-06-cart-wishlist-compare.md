# Phase 6 — Cart, Wishlist & Comparison

## Goal
Per-user cart & wishlist persisted in MongoDB, plus client-side comparison (up to 4).

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/cart` | Current user's cart |
| POST | `/api/v1/cart/add` | Add item (product_id, qty) |
| PUT | `/api/v1/cart/update` | Update quantity |
| DELETE | `/api/v1/cart/remove/{product_id}` | Remove item |
| GET | `/api/v1/wishlist` | List wishlist |
| POST | `/api/v1/wishlist/add` | Add product |
| DELETE | `/api/v1/wishlist/remove/{product_id}` | Remove product |
| GET/POST/DELETE | `/api/v1/compare` | Manage compare set (max 4) |

## Backend Steps
1. Cart doc: embedded `items[]` with `product_id`, `slug`, `name`, `price`, `discount_price`, `image`, `quantity` (snapshot).
2. Auth-gated router; upsert into embedded array, enforce qty >= 1.
3. Wishlist: array of product refs (ids/slugs) on the user or its own doc.
4. Compare: enforce max 4; return product summaries.

## Frontend Steps
1. `Cart` page — line items, qty +/- , remove, order summary (subtotal/discount/total).
2. `Wishlist` page — grid + move-to-cart.
3. `Compare` page + floating tray; "Add to compare" on cards/detail.
4. `Navbar` cart badge reflects item count (fetch on mount / auth change).

## Verification
- [ ] Add/update/remove cart reflects immediately; totals correct
- [ ] Cart persists across reload for logged-in user
- [ ] Wishlist toggles and persists
- [ ] Compare rejects a 5th product with a clear message
