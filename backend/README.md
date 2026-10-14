# ElectroHub Backend (FastAPI + MongoDB)

FastAPI backend for ElectroHub NoSQL e-commerce catalog.

## Tech Stack
- FastAPI
- PyMongo (MongoDB driver)
- Pydantic v2
- Uvicorn (ASGI server)

## Setup

1. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
cp .env.example .env
# Edit .env with your MongoDB URI (local or Atlas)
```

4. Seed database
```bash
python seed.py
```

5. Run development server
```bash
uvicorn app.main:app --reload --port 8000
```

## API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## Project Structure
```
app/
├── api/v1/         # API routes
├── core/           # Config, settings
├── db/             # Database connection
├── models/         # Data models/schemas
├── repositories/   # Data access layer (DAL)
├── schemas/        # Pydantic request/response schemas
├── services/       # Business logic
└── main.py         # App entry point
```
