# Phase 1 — Foundation & Environment Setup

## Goal
A reproducible toolchain with working backend, frontend, and MongoDB connectivity (local + Atlas).

## Steps

### A. Backend Environment
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```
- Confirm `uvicorn` and `pymongo` import cleanly.

### B. Frontend Dependencies
```bash
cd frontend
npm i
npm i axios react-router-dom lucide-react
npm i -D tailwindcss @tailwindcss/vite
```

### C. MongoDB
1. **Local:** start `mongod`, test `mongosh "mongodb://localhost:27017"`.
2. **Atlas:** create free M0 cluster, DB user, network access (IP or `0.0.0.0/0` for dev), grab SRV URI.
3. Create DB `electrohub_nosql`.

### D. Environment Config
- Keep `backend/.env.example` (ENV, both URIs, DB name, prefix, CORS).
- **Replace stale root `.env.example`** (old MySQL/SMTP) with the MongoDB stack.
- Verify `ENV=local|atlas` switch in `app/core/config.py` selects the right URI.

### E. CORS / Vite
- Backend CORS allows `http://localhost:5173`.
- Add Vite dev proxy to `http://localhost:8000` (optional; CORS alone works).

## Verification
- [ ] `uvicorn app.main:app --reload --port 8000` starts, `GET /health` → 200
- [ ] `mongosh` connects locally; Atlas connects
- [ ] Both URIs selected correctly by `ENV`
- [ ] `npm run dev` serves the starter at :5173
