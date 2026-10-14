# Phase 5 — User Accounts & Authentication

## Goal
Registration/login with token-protected routes.

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Create user (hashed password) |
| POST | `/api/v1/auth/login` | Verify creds → return JWT |
| GET | `/api/v1/auth/me` | Current user (protected) |

## Backend Steps
1. `repositories/user.py` — find by email/username, insert user.
2. `schemas/auth.py` — `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserOut`.
3. Hash passwords with `passlib[bcrypt]` — **never store plaintext**.
4. Issue JWT (`python-jose` or equivalent) with `sub` (user id), expiry.
5. `core/security.py` — `create_access_token`, `decode_token`, `get_current_user` dependency (raises 401).
6. `api/v1/auth.py` router; mount in `main.py` with `API_V1_PREFIX`.

## Frontend Steps
1. `Login` / `Register` pages with form validation.
2. `AuthContext` — store token (localStorage), expose `user`, `login`, `logout`.
3. Attach `Authorization: Bearer <token>` in `services/api.js`.
4. Navbar shows avatar/logout when authed; protected actions prompt login.

## Security
- Hash on register AND login comparison.
- Short-lived token; 401 on missing/invalid/expired.
- Never log or commit secrets.

## Verification
- [ ] Register creates user; duplicate email rejected
- [ ] Login returns token; `/auth/me` works with token, 401 without
- [ ] Navbar reflects logged-in state; logout clears token
