# 06 — Security Design

Admin surfaces expose destructive powers, so authorization is enforced **server-side on
every route**; the UI is never trusted for access control.

## 6.1 Threat model (concise)
| Threat | Mitigation |
|---|---|
| Anonymous access to admin API/pages | `require_admin` on every route; pages redirect to login |
| Normal user escalating to admin | admin check requires `is_admin`; user tokens have no admin scope |
| Stolen storefront token used on admin | admin token carries `scope:"admin"`; admin endpoints reject non-admin scope |
| CSRF on Option A forms | CSRF token (double-submit) on all mutating POSTs; `SameSite=Lax` cookie |
| XSS via product/review text | Jinja2 autoescaping (A); React escaping (B); no `dangerouslySetInnerHTML` |
| Brute-force login | per-IP + per-email rate limit on login (e.g. 10 / 15 min) |
| Credential stuffing | bcrypt verify (existing), generic error message, constant-time-ish |
| Malicious image URLs | validate `http(s)` scheme; storefront renders in `<img>` only (no HTML) |
| NoSQL injection | typed Pydantic inputs; never pass raw dicts from payload into queries |
| Secret leakage | secrets only in env; never logged; cookie `Secure` in prod |

## 6.2 Authentication
- **Credentials**: existing `users` collection + `verify_password` (bcrypt).
- **Admin check**: `user.get("is_admin") is True` (and/or `role == "admin"`).
- **Token**: `create_access_token(subject, scope="admin")` → JWT signed with
  `SECRET_KEY` (HS256), `sub=user_id`, `exp`, `scope`.
- **Login responses**: `401` invalid credentials; **`403` valid but not admin** — do not
  reveal which part failed beyond that.

### `require_admin` (shared core, both options)
```python
def get_admin_user(user=Depends(get_current_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(403, "Administrator access required")
    return user
```
Option A calls the same core after resolving identity from the cookie.

## 6.3 Session transport — cookies (A) vs tokens (B)
### Option A — signed HttpOnly cookie
| Attribute | Value | Why |
|---|---|---|
| name | `admin_session` | separate from storefront token |
| value | JWT (id, exp, scope=admin) | signed, tamper-proof |
| `HttpOnly` | true | not readable by JS → XSS can't exfiltrate |
| `Secure` | true in prod | HTTPS-only |
| `SameSite` | `Lax` | blocks cross-site POST CSRF; allows top-level nav |
| `Path` | `/admin` | not sent to storefront/API routes |
| `Max-Age` | `ACCESS_TOKEN_EXPIRE_MINUTES` | expires with token |

### Option B — bearer token in `localStorage`
- Key `electrohub_admin_token` (distinct from `electrohub_token`).
- Sent as `Authorization: Bearer …` via a dedicated axios instance.
- Trade-off: readable by JS (XSS risk) — acceptable given React escaping and no
  third-party scripts; documented. A future hardening path is an HttpOnly cookie + CSRF
  for Option B as well.

## 6.4 CSRF (Option A only)
- On `GET /admin/login` (and any page render) set a `csrf_token` cookie (random 32 bytes)
  and embed the same value in a hidden `<input name="csrf_token">`.
- On every mutating POST, compare the form field with the cookie (constant-time). Mismatch
  → `403`.
- `SameSite=Lax` is the second layer. Option B (Authorization header, no cookie) is **not**
  CSRF-susceptible and needs no CSRF token.

## 6.5 Rate limiting & lockout
- Login: sliding window per `(ip, email)` — e.g. max **10 attempts / 15 min**, then `429`
  for the window. Keep an in-process dict for a single instance; document that a shared
  store (Redis) is needed only if scaled horizontally.
- Optional soft lock: after N failures, require a short delay (avoid hard account lockout).

## 6.6 Password policy (admin)
- Minimum length 8 for admins (register allows 6 for customers; admins are provisioned).
- bcrypt with the existing `hash_password`.
- Admin creation is **out-of-band** (DB seed/env), not self-service.

## 6.7 Audit logging
- Every mutating admin action writes to `audit_logs` (see `03-data-model.md §1.21`):
  `actor_id`, `action`, `entity`, `entity_id`, optional `changes`, `at`, `ip`, `surface`.
- Best-effort: a logging failure must not roll back the business action (log a warning).
- Never store secrets/passwords; redact fields named like `password`/`token`.

## 6.8 Headers & transport
- HTTPS everywhere (Netlify + Render provide TLS).
- Set `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: same-origin` on admin responses (Option A middleware).
- Option A pages should send a tight `Content-Security-Policy` allowing only self-hosted
  CSS/images (`default-src 'self'; img-src https: data:; style-src 'self'`).

## 6.9 CORS
- The JSON admin API is same-origin with Option B's deployed site; ensure the site origin
  stays in `CORS_ORIGINS`. `allow_credentials=True` already set — fine because Option B
  uses headers (not cookies), and Option A is same-origin (no CORS needed).
- Do **not** add wildcard origins with credentials.

## 6.10 Secrets & configuration
| Setting | Env | Default | Notes |
|---|---|---|---|
| `SECRET_KEY` | yes | dev value | signs tokens + session cookie; must be strong in prod |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | yes | 1440 | admin session lifetime |
| `ADMIN_COOKIE_SECURE` | yes | true in prod | cookie `Secure` flag |
| `ADMIN_SESSION_COOKIE` | optional | `admin_session` | cookie name |
| `ADMIN_LOGIN_RATE_*` | optional | 10/15min | rate-limit knobs |

## 6.11 Authorization test matrix (must be automated)
Mirror `04-api-specification.md §4.10`: assert `401` (no token), `403` (user token),
`200` (admin token) for representative routes in every module; assert Option A pages
redirect non-admins to `/admin/login`. Also test CSRF rejection and rate-limit `429`.

## 6.12 Explicit non-goals
- No 2FA, SSO, or IP allow-listing in v1 (noted as future hardening).
- No field-level permissions (single admin role).
- No client-side-only guards — every route is server-enforced.
