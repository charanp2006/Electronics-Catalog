# ElectroHub - NoSQL Edition

Full-stack Electronics Catalog built with FastAPI, MongoDB, and React.js (Vite). This project demonstrates NoSQL database concepts, document modeling, and end-to-end integration for ABA submission.

## Tech Stack

- **Backend**: FastAPI (Python), PyMongo, Pydantic
- **Frontend**: React.js + Vite, Tailwind CSS, React Router
- **Database**: MongoDB (Local or Atlas)

## Features

- Product catalog with search, filtering, sorting & pagination
- Product details with specifications, reviews & price history
- Category & brand filtering
- RESTful API with Swagger documentation
- Document-based NoSQL data modeling
- Support for both Local MongoDB and MongoDB Atlas

## Project Structure

```text
Electronics catalog/
├── backend/           # FastAPI backend
├── frontend/          # React + Vite frontend
├── docs/              # Project documentation (11 docs + API specs)
├── implementation/    # Implementation plans (6 step-by-step)
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
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Update .env with MongoDB URI
python seed.py  # Seed demo data
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

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

## Implementation Guides

See [implementation/](implementation/) folder for step-by-step instructions.

## Demo Credentials (Seed Data)
- Username: `demo`
- Password: `demo12345`

## License
Academic project - ABA Submission
