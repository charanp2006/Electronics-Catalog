# Phase 7 — Reviews, Price History & Checkout

## Goal
Interactive reviews, price-history display, and a demo order flow that updates stock.

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/products/{slug}/reviews` | Add review (auth) |
| POST | `/api/v1/orders` | Place demo order (auth) |
| GET | `/api/v1/orders` | Current user's order history |

## Backend Steps
1. **Reviews:** validate rating 1–5 and non-empty comment; push into product's embedded `reviews`; recompute `average_rating` and `total_reviews`.
2. **Price history:** ensure `price_history[]` populated so the detail view can render change badges/chart.
3. **Orders:** create order doc with **embedded items snapshot** (`product_id`, `slug`, `name`, price, qty) + totals + status.
4. On order: decrement `stock` per item; clear the user's cart.
5. Guard: reject checkout with empty cart or qty > stock.

## Frontend Steps
1. Review form on `ProductDetail` (star picker + comment) → optimistic/refresh list.
2. Price-history badge/chart on detail page.
3. `Checkout` button on Cart → confirmation → redirect to order confirmation.
4. `Orders` page listing past orders and their items/totals.

## Verification
- [ ] Adding a review appends and updates `average_rating`/`total_reviews`
- [ ] Checkout creates an order document and clears the cart
- [ ] Product `stock` decrements by ordered quantity
- [ ] Order history shows placed orders for the logged-in user
