# AGENTS.md

Stack: FastAPI + MongoDB + React.js (Vite).

## Project Overview
ElectroHub - full-stack consumer-electronics catalog (search, compare, price history) with a dual Admin CMS.

## Key Commands

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm i
npm run dev        # http://localhost:5173 (proxies /api -> :8000)
npm run build
npm run lint
```

### Seeding & Tests
```bash
cd backend
python seed.py                      # requires ADMIN_EMAIL/ADMIN_PASSWORD in .env
python -m pytest tests/ -q          # 56 tests; reseeds DB before+after the run
```

## Architecture
- Backend: FastAPI, PyMongo, Pydantic
- Frontend: React + Vite + Tailwind v4
- DB: MongoDB (local/Atlas, toggled by ENV in .env)

## Admin CMS (two peers, one shared backend)
- **Option A (server-rendered):** `http://localhost:8000/admin` — FastAPI + Jinja2, HttpOnly `admin_session` cookie (path=/admin), CSRF double-submit (`admin_csrf`), form POST + PRG. Code: `backend/app/admin/` (routes, deps, templates, static).
- **Option B (React SPA):** `http://localhost:5173/admin-cms` — React pages in `frontend/src/admin/`, Bearer token in `localStorage['electrohub_admin_token']`. Calls the JSON API.
- **Shared JSON API:** `/api/v1/admin/*` (auth, stats, products, categories, brands, orders, reviews) in `backend/app/api/v1/admin/`, services in `backend/app/services/admin/`, schemas in `backend/app/schemas/admin/`.
- Authorization source of truth: `users.is_admin`. Admin login rate-limited (10/15min). Order status transitions enforced (`ALLOWED_TRANSITIONS` in `services/admin/orders.py`). Audit writes to `audit_logs`.
- Tests: `tests/test_admin.py` (JSON API matrix), `tests/test_admin_option_a.py` (cookie/CSRF/redirect matrix).

## Environment
Use .env (see .env.example) with ENV=local|atlas to toggle MongoDB connection.
Requires: ADMIN_EMAIL, ADMIN_PASSWORD (seed creates the admin user), SECRET_KEY.

## Conventions
- Repository/DAL pattern for data access
- Pydantic schemas for validation
- RESTful API design
- Component-based React (customer theme: terminal/CRT aesthetic, tokens in `src/index.css`)
- Money in INR; products store `images[]` + primary `image`; reviews embedded in products
