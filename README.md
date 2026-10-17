# ElectroHub - NoSQL Edition

Full-stack Electronics Catalog built with FastAPI, MongoDB, and React.js (Vite). This project demonstrates NoSQL database concepts, document modeling, and end-to-end integration for ABA submission.

## Tech Stack

- **Backend**: FastAPI (Python), PyMongo, Pydantic
- **Frontend**: React.js + Vite, Tailwind CSS v4, React Router
- **Motion & UX**: Motion (Framer Motion), GSAP, Lenis smooth scroll
- **Database**: MongoDB (Local or Atlas)

## Features

- Product catalog with search, filtering, sorting & pagination
- Product details with specifications, reviews & price history
- Category & brand filtering
- User authentication (register / login with JWT)
- Shopping cart, wishlist & product comparison (up to 4)
- Add reviews with live rating recalculation
- Demo order placement (stock decrement + order history)
- RESTful API with Swagger documentation
- Document-based NoSQL data modeling
- Support for both Local MongoDB and MongoDB Atlas
- Retro "lab terminal" UI: phosphor palette, CRT scanlines, mono type, motion-driven reveals

## Project Structure

```text
Electronics catalog/
├── backend/           # FastAPI backend
├── frontend/          # React + Vite frontend
├── docs/              # Project documentation (11 docs + API specs)
├── implementation/    # Phase-wise guides (8 phases)
├── BRD.md             # Business Requirements Document
├── README.md
└── AGENTS.md
```

## Quick Start

### 1. MongoDB Setup
Choose Local or Atlas. See [docs/11-deployment-plan.md](docs/11-deployment-plan.md).

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Update .env with MongoDB URI (ENV=local or atlas)
python seed.py  # Seed demo data (12 products, 4 categories, 8 brands)
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server proxies `/api` to `http://localhost:8000`, so no CORS setup is needed.

### Deploy the frontend (Netlify)
Build settings, env vars and SPA redirect: see [docs/12-netlify-deployment.md](docs/12-netlify-deployment.md).
A ready-to-use [`netlify.toml`](netlify.toml) is included (base `frontend`, build `npm run build`, publish `dist`).

## Access

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000/api/v1
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Documentation

- [BRD](BRD.md)
- [Product Vision](docs/01-product-vision.md)
- [MVP Scope](docs/02-mvp-scope.md)
- [PRD](docs/03-product-requirements.md)
- [User Flows](docs/04-user-flows.md)
- [UI/UX Design](docs/05-ui-ux-design.md)
- [Software Architecture](docs/06-software-architecture.md)
- [Database Design (NoSQL)](docs/07-database-design.md)
- [API Spec (OpenAPI YAML)](docs/08-api-specification.yaml)
- [API Spec (Markdown)](docs/api-specification.md)
- [Development Roadmap](docs/09-development-roadmap.md)
- [Test Plan](docs/10-test-plan.md)
- [Deployment Plan](docs/11-deployment-plan.md)
- [Netlify Deployment (Frontend)](docs/12-netlify-deployment.md)
- [Backend + MongoDB Atlas (Render)](docs/13-backend-and-atlas-deployment.md)

## Implementation Guides (Phase-Based)

The build is organized into **8 sequential phases** (not calendar weeks). Each phase has clear tasks and exit criteria — see [docs/09-development-roadmap.md](docs/09-development-roadmap.md).

| Phase | Guide |
|---|---|
| 1 | [Foundation & Environment](implementation/phase-01-foundation-setup.md) |
| 2 | [Data Layer: Modeling & Seeding](implementation/phase-02-data-layer.md) |
| 3 | [Backend Core API](implementation/phase-03-backend-core-api.md) |
| 4 | [Frontend Core UI](implementation/phase-04-frontend-core.md) |
| 5 | [Auth](implementation/phase-05-auth.md) |
| 6 | [Cart, Wishlist & Compare](implementation/phase-06-cart-wishlist-compare.md) |
| 7 | [Reviews & Checkout](implementation/phase-07-reviews-checkout.md) |
| 8 | [Testing & Deployment](implementation/phase-08-testing-deployment.md) |

## Demo Credentials (Seed Data)
- Email: `demo@example.com`
- Username: `demo`
- Password: `demo12345`

## Testing

Backend tests use `pytest` (23 tests covering catalog, auth, cart, wishlist, reviews and orders):

```bash
cd backend
.venv\Scripts\activate
pytest
```

Frontend lint:

```bash
cd frontend
npm run lint
```

## License
Academic project - ABA Submission
