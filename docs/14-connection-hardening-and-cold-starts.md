# 14. Connection Hardening & Cold Starts

This document explains, for **ElectroHub**, how the MongoDB Atlas "connection drops
after a while" problem is handled, why, where the code lives, and how it relates to
free-host cold starts (Render). It is written so the same reasoning can be reused in
any other project — a reusable, stack-agnostic prompt lives in
[`../MASTER-PROMPT.md`](../MASTER-PROMPT.md).

---

## 14.1 The problem (symptom)

Typical report, across many stacks (FastAPI, Express, Flask, .NET, Go…):

> "Everything works. Then I come back after a few hours (or a day), and the app can't
> reach MongoDB. The first request hangs or errors, then it usually works again. Atlas
> shows the cluster as active (not paused), but it looks 'not connected'."

This is **almost never** MongoDB being down. It is the combination of three things:

1. **Idle TCP connections get silently closed** — by the cloud NAT/load balancer, by
   Atlas's front end, or by the host suspending the process.
2. **The database driver keeps those dead sockets** and thinks they're alive, so the
   first query after idle is sent into a socket nobody is listening on.
3. **The default "server selection" timeout is ~30 s**, so the first request *hangs*
   for up to 30 seconds before it errors — which feels like "the database went away".

### Why Atlas *looks* disconnected
The Atlas UI shows **active client connections**, not "is your app okay". Connections
are **lazy and pooled** (opened only when a query runs, released when idle). So a
healthy app with no traffic legitimately shows **0 connections**. The green "Active"
dot (cluster exists) and the connection count are two different things.

### What it is **not**
- Not the free-plan **connection limit** (Free/Flex = 500 connections per node). A
  well-written app with a cached client uses a handful.
- Not the **30-day auto-pause** (see §14.4) — that only triggers after *30 days with no
  connections at all*.

---

## 14.2 Root-cause detail

| Layer | What happens | Consequence |
|---|---|---|
| Network / NAT / LB | Closes idle TCP sockets (often after minutes) | Socket is dead but the client doesn't know |
| Atlas front end | Closes idle connections | Same |
| Host (Render free) | Suspends the process after 15 min idle (§14.5) | All sockets die with the process |
| **Driver pool** | Default `maxIdleTimeMS = None` → keeps idle sockets forever | Reuses a dead socket on the next query |
| **Driver timeout** | Default `serverSelectionTimeoutMS = 30000` | First request hangs ~30 s before failing |
| Driver auto-retry | Retries **retryable reads/writes** (if enabled) | Recovers the *second* attempt, not the first |

The fix targets the last three rows: **drop idle sockets proactively**, **fail fast**,
and **retry the first failed read**.

---

## 14.3 The fix in this project (where / what / why)

### Where
Everything lives in **one file**: [`backend/app/db/mongodb.py`](../backend/app/db/mongodb.py).
It is the single place all data access goes through (`get_db()`), so the settings apply
to **every** query in the app — products, cart, orders, auth — without touching the
repositories or routers.

### What — 1) connection-pool & timeout options
Applied as **client options** (not inside the URI), so they hold **no matter which
connection string** is pasted into `.env` / the host's env vars:

```python
CLIENT_OPTIONS = {
    "serverSelectionTimeoutMS": 5000,   # fail fast instead of hanging ~30s
    "connectTimeoutMS": 10000,          # cap the TCP/TLS handshake
    "socketTimeoutMS": 45000,           # cap a single socket read/write
    "maxPoolSize": 50,                  # plenty for a single instance (default 100)
    "minPoolSize": 0,                   # don't hold sockets when idle
    "maxIdleTimeMS": 45000,             # discard sockets idle > 45s  ← the key one
}
```

| Option | Why | Trade-off |
|---|---|---|
| `maxIdleTimeMS: 45000` | The core fix. Sockets idle > 45 s are closed and re-created on demand, so we never reuse one the server already dropped. | Slightly more connection churn; negligible for this traffic. |
| `serverSelectionTimeoutMS: 5000` | Turn a 30 s freeze into a 5 s error the retry can absorb. | If the DB is genuinely slow to reach, it errors sooner. |
| `connectTimeoutMS: 10000` | Bounds the initial handshake. | — |
| `socketTimeoutMS: 45000` | A query can never hang forever on a dead socket. | Very long legitimate queries (>45 s) would need a higher value. |
| `maxPoolSize: 50` | Caps sockets per instance. | Raise only if you add many concurrent workers. |
| `minPoolSize: 0` | No sockets held while idle. | First query after idle pays a few ms to connect. |

> Why **not** put these in the URI? A pasted Atlas URI already contains
> `retryWrites`, `w=majority`, `appName=…`. Passing the same key twice (URI + client
> option) can raise a configuration error. Client-only options avoid that entirely.

### What — 2) retry once on a dropped read
A tiny decorator absorbs the **first** failed attempt after an idle period:

```python
RETRYABLE_ERRORS = (AutoReconnect, ConnectionFailure, NetworkTimeout)

def retry_once(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RETRYABLE_ERRORS:
            time.sleep(0.4)      # let the topology monitor reconnect
            return func(*args, **kwargs)
    return wrapper
```

It is applied **automatically** by a base class, so no repository method needed editing:

```python
class BaseRepository:
    _READ_PREFIXES = ("get", "list", "featured", "related", "raw")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in list(vars(cls).items()):
            if callable(value) and not name.startswith("_") and name.startswith(cls._READ_PREFIXES):
                setattr(cls, name, retry_once(value))
```

All seven repositories inherit it:

```
ProductRepository, CartRepository, OrderRepository, UserRepository,
CategoryRepository, BrandRepository, WishlistRepository  →  class X(BaseRepository)
```

| Method name starts with | Retried? | Example |
|---|---|---|
| `get`, `list`, `featured`, `related`, `raw` | ✅ yes | `get_by_slug`, `list_all`, `get_cart` |
| `add`, `create`, `update`, `remove`, `clear`, `delete` | ❌ no | `add_item`, `create_from_cart` |
| `_private` helpers | ❌ no | `_load`, `_serialize` |

### Why reads only (the important design decision)
Retrying a **write** can double-apply it. Example: `create_from_cart` decrements stock
and inserts an order — if we blindly retried it, a client could be charged twice or
stock could drop twice. Writes are already covered by the driver's **`retryWrites`**
(which is idempotent at the driver level because it tracks the operation). Reads are
safe to repeat, so that's where we add an explicit retry.

### How to verify
```bash
curl https://<your-api>/health            # {"status":"ok","env":"atlas"}
curl https://<your-api>/api/v1/products/  # returns items -> DB link is healthy
```
Backend tests still pass (`pytest`, 23 tests) because the retry layer is transparent.

---

## 14.4 Atlas free-cluster auto-pause (separate issue)

- Atlas **automatically pauses idle Free (M0) clusters after 30 days with no
  connections.**
- Symptom: `mongodb+srv` DNS no longer resolves / "cluster not found".
- Fix: open Atlas → **Resume**; and if it must stay always-on without manual saves,
  use a **Flex / dedicated** tier (dedicated tiers don't auto-pause).
- This is **not** what causes the "few hours/days" failure; that's §14.3.

---

## 14.5 Render free-tier cold starts (why it stops after a while)

Independent of MongoDB. Render's **free** web service:

| Fact | Detail |
|---|---|
| Spin-down | After **15 minutes** with no inbound traffic (HTTP or WebSocket) |
| Spin-up | **~1 minute** on the next request (Render shows a loading page) |
| Free instance hours | **750 per workspace per calendar month** |
| A month | ~730–744 hours → 750 hrs is enough for **exactly one** service to run 24/7 (leaves ~6 spare hours) |
| If exhausted | **All free web services suspend until the next month**; hours reset monthly, no rollover |
| Spun-down time | **Does not** consume instance hours |
| Filesystem | Ephemeral — uploads/SQLite are wiped on restart |
| Paid (Starter, ~$7/mo) | No spin-down, no monthly hour cap |

So "it stops after a few hours/days" on the **host** side has two meanings:
1. **Every ~15 min of quiet**, the process sleeps → the next hit cold-starts (~1 min).
2. If your keep-alive is too aggressive **and** you run more than one free service, you
   can **burn the 750 hours** and hit "suspended until next month".

> Render's own docs say not to use the free tier for production.

### Fix (not implemented here — documented only)
The Atlas fix (§14.3) and the cold-start fix are **independent**:

| Goal | Fix | Cost |
|---|---|---|
| Keep the backend awake (no cold starts) | Ping `GET /health` every **≤14 min** from an external monitor (cron-job.org, UptimeRobot, Better Stack, or a GitHub Actions cron) | Free |
| Truly always-on, no hour cap | Upgrade the Render service to **Starter ($7/mo)** | Paid |
| Avoid spin-down entirely | Host on an always-on free alternative (e.g. Fly.io small machine, Koyeb) or a VPS | Varies |

**How it would be implemented for this project:**
1. The app already exposes `GET /health` (no auth) → ideal ping target.
2. Create an external monitor (e.g. cron-job.org) with URL
   `https://<your-api>/health`, interval **14 minutes**, method GET, expecting `200`.
3. Optional: also ping `https://electrohub.netlify.app` (static sites don't sleep, so
   only the API needs it).
4. Do **not** run more than one always-on free service from the same workspace, or you
   will exceed 750 hours/month.
5. If the ~1 min first-request delay is unacceptable, upgrade to Starter — no code change.

> Note: keeping the server awake means connections stay *available* longer, but
> `maxIdleTimeMS=45000` still closes sockets during quiet periods **by design** — so
> Atlas will still show 0 connections while idle even with a keep-alive. That is
> expected and correct.

---

## 14.6 Quick reference

| Symptom | Real cause | Fix | Where |
|---|---|---|---|
| 1st request after idle hangs ~30 s / times out | Stale pooled socket + 30 s server-selection timeout | `maxIdleTimeMS` + `serverSelectionTimeoutMS` + read retry | `backend/app/db/mongodb.py` |
| Atlas shows "not connected" while idle | Lazy/pooled connections; 0 active sockets is normal | None needed — verify via `/health` + `/api/v1/products/` | — |
| **Cluster** paused / DNS fails | Free cluster idle **30 days** | Resume in Atlas / use Flex | Atlas UI |
| First request after quiet takes ~1 min | Render free **15-min spin-down** | External `/health` ping every ≤14 min, or paid plan | Host config |
| Free services "suspended until next month" | **750 instance-hours** used up (multiple services / aggressive pinging) | One always-on free service, or paid | Render billing |

---

## 14.7 References
- Atlas auto-pause & connection troubleshooting — https://www.mongodb.com/docs/atlas/troubleshoot-connection
- Atlas connection limits — https://www.mongodb.com/docs/atlas/connection-limits/
- PyMongo `MongoClient` pool options (`maxIdleTimeMS`, `maxPoolSize`, timeouts) — https://pymongo.readthedocs.io/
- Render free tier (spin-down, 750 hrs, cold start) — https://render.com/docs/free
- Render FAQ (why free services are slow to respond) — https://render.com/docs/faq
