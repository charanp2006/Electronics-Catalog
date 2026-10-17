# 11. Deployment Plan

## 11.1 Deployment Strategy
For ABA demonstration, focus on local run + optional Atlas cloud.

## 11.2 Local Deployment (Development)

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- MongoDB Community (local) OR MongoDB Atlas account
- Git

### Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Configure MONGODB_URI_LOCAL or MONGODB_URI_ATLAS
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm i
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 11.3 MongoDB Setup Options

### Option A: Local MongoDB
- Install MongoDB Community Server
- Start `mongod` service
- URI: `mongodb://localhost:27017/electrohub_nosql`

### Option B: MongoDB Atlas (Cloud)
- Create free M0 cluster
- Create DB user + Network Access (whitelist IP)
- Get SRV connection string
- URI: `mongodb+srv://<user>:<pass>@cluster0.xxx.mongodb.net/electrohub_nosql`

## 11.4 Environment Variables

`.env.example` (backend):
```env
ENV=local
MONGODB_URI_LOCAL=mongodb://localhost:27017/electrohub_nosql
MONGODB_URI_ATLAS=mongodb+srv://username:password@cluster.mongodb.net/electrohub_nosql
MONGODB_DB_NAME=electrohub_nosql
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:5173"]
```

## 11.5 Runtime Switch Logic

Backend will choose URI based on `ENV`:
- `ENV=local` → use `MONGODB_URI_LOCAL`
- `ENV=atlas` → use `MONGODB_URI_ATLAS`

## 11.6 Cloud Deploy (Netlify + Backend Host)

For the live demo, the frontend is deployed to **Netlify** (static Vite build) and the FastAPI backend runs on a separate Python host backed by **MongoDB Atlas**.

- Frontend: **[12. Netlify Deployment](12-netlify-deployment.md)**
- Backend + Atlas + CORS: **[13. Backend + MongoDB Atlas](13-backend-and-atlas-deployment.md)**
- Backend host: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, with `ENV=atlas`, a real `MONGODB_URI_ATLAS`, a strong `SECRET_KEY`, and the Netlify domain added to `CORS_ORIGINS`.

## 11.7 Build & Run (Production Demo)

```mermaid
flowchart LR
    A[MongoDB] --> B[FastAPI - Uvicorn]
    B --> C[React Build/Vite Dev]
    C --> D[User Browser]
```

## 11.8 Troubleshooting
| Issue | Solution |
|---|---|
| CORS Error | Add frontend URL to CORS_ORIGINS |
| MongoDB Connection | Check mongod running / Atlas IP whitelist |
| Port Conflict | Change port in uvicorn/npm |
