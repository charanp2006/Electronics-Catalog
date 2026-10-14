# Phase 8 — Integration, Testing, Polish & Deployment

## Goal
Fully validated end-to-end application, complete documentation, demo-ready.

## 1. Backend Tests
Add `pytest` + `httpx` (`TestClient`) under `backend/tests/`:
- Repository tests: filters, search, sort, pagination.
- API tests mapping to `docs/10-test-plan.md` (TC-001…TC-010).
- Auth tests: register/login/401 on protected routes.
- Cart/order tests: add/update/remove, checkout stock decrement.

## 2. Manual Test Checklist (`docs/10-test-plan.md`)
- [ ] MongoDB running (local) OR Atlas connected
- [ ] Backend starts without errors; `/docs` accessible
- [ ] Seed data counts correct
- [ ] `GET /products` returns data
- [ ] Filters/search/sort work via API
- [ ] Frontend loads products; detail navigation works
- [ ] Auth, cart, wishlist, compare, reviews, checkout flows work
- [ ] CORS configured; no console errors
- [ ] Both `ENV=local` and `ENV=atlas` tested
- [ ] Screenshots captured

## 3. Polish
- Loading/error/empty states everywhere
- Responsive + accessibility pass
- Consistent palette (`#2563eb`, `#dc2626` accent) per `docs/05-ui-ux-design.md`

## 4. Documentation
- [ ] Update README quick-start (add tailwind/axios deps)
- [ ] Sync `docs/api-specification.md` + `.yaml` with final endpoints
- [ ] Update `docs/09-development-roadmap.md` checkboxes
- [ ] Capture screenshots for the report

## 5. Deployment Verification (`docs/11-deployment-plan.md`)
```bash
# backend
cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev
```
- [ ] Access :5173, :8000/api/v1, :8000/docs
- [ ] Local + Atlas toggles both verified

## Exit Criteria
All test cases pass, both environments verified, docs/screenshots complete, BRD success criteria met.
