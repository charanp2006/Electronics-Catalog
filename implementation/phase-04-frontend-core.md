# Phase 4 — Frontend Core: Catalog UI

## Goal
React app rendering live MongoDB data with routing and working search/filter/sort/pagination.

## Setup
```bash
cd frontend
npm i axios react-router-dom lucide-react
npm i -D tailwindcss @tailwindcss/vite
```
- Add `@tailwindcss/vite` to `vite.config.js` plugins; import Tailwind in `src/index.css`.
- Optional: `server.proxy` → `http://localhost:8000`.

## Structure
```
frontend/src/
├── services/api.js          # axios baseURL /api/v1 + getters
├── components/              # Navbar, Footer, ProductCard, FilterSidebar,
│                            # SearchBar, SortDropdown, Pagination, Rating, Loader
├── pages/                   # Home, Products, ProductDetail
├── hooks/                   # useProducts, useDebounce
└── App.jsx                  # BrowserRouter + routes
```

## Steps
1. **API layer:** `getProducts(params)`, `getProductBySlug(slug)`, `getCategories()`, `getBrands()`.
2. **Routing:** `/`, `/products`, `/products/:slug`.
3. **Navbar:** brand logo, `SearchBar`, nav links (Products, Cart, Wishlist, Compare), cart badge placeholder.
4. **Home:** hero + category tiles + featured products.
5. **Products page:** `FilterSidebar` (category/brand/price) + product grid + `SortDropdown` + `Pagination`; sync state to URL query params.
6. **ProductDetail:** image, price/discount, brand/category, quantity, `specifications` table, `reviews` list, `price_history` badge.
7. **States:** loading spinner, error banner, empty-results message.
8. **Styling:** Tailwind, mobile-first per `docs/05-ui-ux-design.md` palette (`#2563eb` primary).

## Verification
- [ ] Grid renders products fetched from API
- [ ] Search/filter/sort/pagination update results live
- [ ] Clicking a card opens the detail route
- [ ] No CORS errors, no console errors
