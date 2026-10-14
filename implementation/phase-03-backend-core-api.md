# Phase 3 — Backend Core: Catalog API

## Goal
A mounted, read-only catalog API under `/api/v1` with search/filter/sort/pagination and clean errors.

## Structure
```
backend/app/
├── core/config.py        # Pydantic Settings (clean unused imports)
├── db/mongodb.py         # client singleton + close_client()
├── schemas/product.py    # fixed _id handling, response models
├── repositories/product.py, category.py, brand.py
├── api/v1/products.py, categories.py, brands.py
└── main.py               # lifespan + include_router
```

## Steps
1. **Config:** keep `Settings`; use `settings.API_V1_PREFIX` for mounting; drop unused `AnyHttpUrl`.
2. **DB:** add FastAPI **lifespan** that closes the MongoClient on shutdown.
3. **Schemas:** fix leading-underscore fields — use `Field(alias="_id")` with `populate_by_name`, or drop `_id`.
4. **Repository cleanup:** in `ProductRepository.list_products` **delete the abandoned dead query block** (leftover `$or2`, `$expr`, no-op `pass`) and keep only the clean rebuild.
5. **Query features:** `$or` regex search, category/brand filter, price range, sort map (`price_asc|price_desc|rating_desc|newest`), skip/limit pagination.
6. **Routers:** apply `response_model`; raise `HTTPException(404)` on missing slug.
7. **Mount routers** in `main.py`:
```python
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(brands.router, prefix=settings.API_V1_PREFIX)
```
8. Keep CORS for `http://localhost:5173`.

## Verification
- [ ] Swagger `/docs` lists `/api/v1/products`, `/products/{slug}`, `/categories`, `/brands`
- [ ] `curl /api/v1/products?q=samsung` filters correctly
- [ ] `?category=…&brand=…&min_price=…&max_price=…&sort=price_asc&page=1&limit=12` works
- [ ] `GET /api/v1/products/bad-slug` → 404
- [ ] No import-time errors; shutdown closes Mongo client
