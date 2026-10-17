# AGENTS.md

Stack: FastAPI + MongoDB + React.js (Vite).

## Project Overview
ElectroHub - full-stack consumer-electronics catalog (search, compare, price history).

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
npm run dev
```

### Seeding
```bash
cd backend
python seed.py
```

## Architecture
- Backend: FastAPI, PyMongo, Pydantic
- Frontend: React + Vite + Tailwind
- DB: MongoDB (local/Atlas)

## Environment
Use .env (see .env.example) with ENV=local|atlas to toggle MongoDB connection.

## Conventions
- Repository/DAL pattern for data access
- Pydantic schemas for validation
- RESTful API design
- Component-based React
