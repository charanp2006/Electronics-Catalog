# Implementation Plan - 03: Data Modeling & Seeding

## Objectives
- Define MongoDB collections & schemas
- Create seed script with demo data
- Validate seeded data

## Collections
- products
- brands
- categories
- users
- reviews (optional separate)
- orders
- carts

## Tasks
1. Design JSON samples for each
2. Create `backend/seed.py`
3. Map SQL seed_data to MongoDB docs
4. Implement idempotent seeding (drop/create)
5. Run and verify counts
6. Check in Compass

## Seed Data (Same as Original)
- 4 Categories: Smartphones, Laptops, Televisions, Headphones
- 8 Brands, 12 Products
- Demo user: demo/demo12345

## Verification
- products: 12, categories: 4, brands: 8
- Sample product has specs, reviews arrays
