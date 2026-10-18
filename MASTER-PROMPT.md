# MASTER PROMPT — MongoDB Atlas connection hardening + free-host cold starts

> **How to use:** copy everything between the `=== PROMPT START ===` and
> `=== PROMPT END ===` markers into a fresh AI coding session, after filling in the
> `PROJECT CONTEXT` block. It is **stack-agnostic** — it detects your language/driver
> and applies the right settings. Works for FastAPI/PyMongo, Motor, Node
> (mongodb / Mongoose), Express, Flask, Django, .NET, Go, Java, Rust, etc.

---

=== PROMPT START ===

You are a senior backend/database reliability engineer. Fix a recurring MongoDB Atlas
problem in this repository, and document it. Do the work directly in the codebase
unless I say otherwise; follow the repository's existing conventions and do not
introduce new dependencies unless required.

## PROJECT CONTEXT (I will fill this in)
- Repo / project: `<name>`
- Language / framework: `<e.g. Python + FastAPI / Node + Express>`
- MongoDB driver: `<e.g. PyMongo / Motor / mongodb / Mongoose / mongo-go-driver / official .NET driver>`
- Hosting (app): `<e.g. Render free / Railway / Fly.io / VPS / local>`
- Where the DB client is created: `<file/function, or "find it">`
- Anything I must not change: `<e.g. keep the connection string as-is, don't touch auth>`

## THE TWO PROBLEMS

### Problem 1 — "Atlas drops my connection after a few hours/days"
Symptoms across stacks:
- Everything works, then after an idle period the **first** request hangs (~30 s) or
  errors with `ServerSelectionTimeoutError` / `MongoNetworkTimeout` /
  `MongoServerSelectionError`, then usually works again.
- Atlas shows the cluster **Active** (not paused) but reports no/zero connections.

Root cause (not Atlas being down):
1. Idle TCP connections are silently closed by the network/NAT/load-balancer, Atlas's
   front end, or by the app being suspended by the host.
2. The driver's connection pool defaults keep idle sockets (`maxIdleTimeMS` default =
   none/never) and reuse a socket that is already dead.
3. The default server-selection timeout (~30 s) makes the first request hang before it
   errors.

This is **not** the free-plan connection limit (Atlas Free/Flex = 500 conns/node) and
**not** the 30-day auto-pause (that only happens after 30 days with zero connections).

### Problem 2 — Free-host cold starts (e.g. Render free tier)
- Render free web services **spin down after 15 minutes** of no inbound traffic and
  take **~1 minute** to spin back up on the next request.
- Render gives **750 free instance-hours per workspace per calendar month**; a month is
  ~730–744 h, so that is enough for **exactly one** always-on service. Exceed it and
  **all free services suspend until the next month** (hours reset monthly, no rollover).
- Spun-down time does not consume hours. The filesystem is ephemeral.
- Paid Starter (~$7/mo) removes spin-down and the hour cap.
- This is **separate** from Problem 1, but the two compound into "my site is broken
  after a while".

## TASK 1 — Harden the MongoDB connection (implement)

1. **Locate** where the MongoClient / connection is created in this repo and tell me the
   exact file and line before changing anything.
2. **Add pool + timeout options** at client creation (do NOT hard-code them into the
   URI — a pasted Atlas URI already carries `retryWrites`, `w`, `appName`, and passing
   the same key twice can raise a configuration error). Apply the equivalent of these
   values in the correct syntax for this driver:

   | Setting | Value | Purpose |
   |---|---|---|
   | server selection timeout | 5000 ms | fail fast instead of hanging ~30 s |
   | connect timeout | 10000 ms | bound the TCP/TLS handshake |
   | socket / operation timeout | 45000 ms | never hang forever on a dead socket |
   | maxPoolSize | 50 | cap sockets per instance |
   | minPoolSize | 0 | hold nothing while idle |
   | **maxIdleTimeMS** | **45000 ms** | **drop idle sockets so we never reuse a dead one (the key fix)** |

   Driver cheat-sheet (use the one matching this project):
   - **PyMongo / Motor**: `MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000, socketTimeoutMS=45000, maxPoolSize=50, minPoolSize=0, maxIdleTimeMS=45000)`. For Motor, pass the same kwargs to `AsyncIOMotorClient`.
   - **Node `mongodb`**: `new MongoClient(uri, { serverSelectionTimeoutMS: 5000, connectTimeoutMS: 10000, socketTimeoutMS: 45000, maxPoolSize: 50, minPoolSize: 0, maxIdleTimeMS: 45000 })`.
   - **Mongoose**: `mongoose.connect(uri, { serverSelectionTimeoutMS: 5000, connectTimeoutMS: 10000, socketTimeoutMS: 45000, maxPoolSize: 50, minPoolSize: 0, maxIdleTimeMS: 45000 })`.
   - **Java**: `MongoClientSettings.builder().applyToSocketSettings(b -> b.connectTimeout(10, SECONDS).readTimeout(45, SECONDS)).applyToConnectionPoolSettings(b -> b.maxSize(50).minSize(0).maxConnectionIdleTime(45, SECONDS)).applyToClusterSettings(b -> b.serverSelectionTimeout(5, SECONDS)).build()`.
   - **.NET**: `new MongoClientSettings { ServerSelectionTimeout = TimeSpan.FromSeconds(5), ConnectTimeout = TimeSpan.FromSeconds(10), MaxConnectionIdleTime = TimeSpan.FromSeconds(45), MaxConnectionPoolSize = 50, MinConnectionPoolSize = 0 }`.
   - **Go**: `options.Client().ApplyURI(uri).SetServerSelectionTimeout(5*time.Second).SetConnectTimeout(10*time.Second).SetSocketTimeout(45*time.Second).SetMaxPoolSize(50).SetMinPoolSize(0).SetMaxConnIdleTime(45*time.Second)`.
   - **Rust**: `.server_selection_timeout(Duration::from_secs(5)).connect_timeout(...).max_idle_time(Duration::from_secs(45))` on `ClientOptions`.

3. **Keep one shared client** for the process lifetime. Confirm the client is created
   once and reused (module-level singleton / DI singleton). If it is created per request,
   fix that — a client (and its pool) must be reused. Do not open/close per request.

4. **Add a single retry on dropped connections — for READS ONLY.**
   - Catch the driver's transient connection errors (PyMongo: `AutoReconnect`,
     `ConnectionFailure`, `NetworkTimeout`; Node: network/`ServerSelectionError` codes;
     equivalent elsewhere).
   - On failure: wait ~400 ms (let the topology monitor reconnect) and retry **once**.
   - Apply it so it requires minimal edits — e.g. a decorator + a base class/mixin that
     auto-wraps read-style methods, or a single wrapper around read queries.
   - **Do NOT retry writes** (insert/update/delete/stock changes/orders). The driver's
     retryable writes already handle dropped writes idempotently; an app-level retry on
     a non-idempotent write (e.g. "decrement stock") would double-apply it. If a write
     must be retried, it needs an idempotency key — say so instead of doing it blindly.

5. **Do not** add aggressive `Sleep`/reconnect loops, and do not open a new client per
   request. Do not swallow errors silently — log once at warn level when a retry fires.

6. **Ensure a cheap unauthenticated health endpoint exists** (e.g. `GET /health`
   returning `200 {"status":"ok"}`). It must NOT require DB access to succeed, but MAY
   include a shallow DB ping. This is the target for keep-alive (Task 3).

## TASK 2 — Document it (implement)

Create/append a document (e.g. `docs/connection-hardening.md`) covering, with the
project's own file paths:
- The symptom and the real root cause (idle sockets + pool/retry defaults).
- The exact options added, at the exact file/line, and **why** each value.
- Why retries are limited to reads (idempotency).
- How to verify (`/health`, a real read query).
- Tuning guidance if traffic changes.

Keep it factual and note that Atlas showing "0 connections" when idle is normal.

## TASK 3 — Handle free-host cold starts (implement the config, explain, don't over-engineer)

1. Explain in the document: Render free **spins down after 15 min idle**, **~1 min cold
   start**, **750 instance-hours/workspace/month** (enough for ~1 service 24/7; over
   that, free services suspend until next month). Confirm/adapt if the host is not
   Render (Railway/Fly/Koyeb have analogous sleep/cold-start limits — state the real
   numbers for the host in use).
2. Provide the fix and apply the parts that are code/config:
   - **Keep-alive:** an external monitor hitting `GET /health` every **≤14 minutes**
     (cron-job.org / UptimeRobot / Better Stack / a GitHub Actions scheduled workflow).
     If I ask you to, add the GitHub Actions workflow file to the repo; otherwise just
     document the setup.
   - **Or upgrade** the service to a paid tier (no spin-down, no hour cap) — document
     only, no code.
   - **Warn** that running multiple always-on free services or pinging too often can
     exhaust the 750 hours and suspend everything.
3. State clearly that this host fix and the Task 1 DB fix are **independent** — fixing
   one does not fix the other — and that with `maxIdleTimeMS` set, Atlas will still
   report 0 connections while idle (expected).

## CONSTRAINTS
- Do not commit secrets or print the connection string / credentials.
- Do not modify the connection string itself unless I explicitly ask.
- Preserve existing behaviour and public APIs; keep the change minimal and idiomatic.
- Run the project's tests/linters after the change and report results.
- If the stack differs from the cheat-sheet, use the driver's official pool/timeout
  option names and say which ones you used.

## DELIVERABLES (report back in this order)
1. **Findings** — where the client is created (file:line) and its current options.
2. **Changes** — files changed with a short diff-style summary per file.
3. **Options applied** — a table of option → value → reason.
4. **Retry policy** — exactly which methods/operations retry, and confirmation writes do not.
3. **Cold-start section:** host facts + the keep-alive/paid fix applied or documented.
4. **Verification:** commands I can run and their expected output; test/lint results.
5. **Doc path** of the written documentation.

## ACCEPTANCE CHECKLIST (tick each)
- [ ] One shared DB client, created once, with pool/timeout options applied.
- `maxIdleTimeMS` (or driver equivalent) set to ~45 s.
- Server-selection timeout ~5 s.
- Read operations retry once on a dropped connection; writes do not.
- `/health` endpoint exists and returns 200 without a DB dependency (ping optional).
- Document explains symptom → cause → fix → file paths + tuning.
- Cold-start behaviour of the host explained with correct numbers, and a keep-alive
  (or paid-tier) fix documented/applied.
- No secrets logged; no new client-per-request; tests/lint still pass.

If any instruction conflicts with the repo's actual stack or conventions, tell me the
conflict and your proposed alternative before proceeding.

=== PROMPT END ===

---

## Notes for the person using this prompt
- Fill in the `PROJECT CONTEXT` block; everything else can stay as-is.
- If your app has **no health endpoint**, the prompt tells the agent to add one — that
  is required for a clean keep-alive.
- If your host is **not Render**, the agent is instructed to state that host's real
  sleep/cold-start and quota numbers instead of assuming Render's.
- The fixed reference implementation for exactly this problem lives in
  [`backend/app/db/mongodb.py`](backend/app/db/mongodb.py) and is explained in
  [`docs/14-connection-hardening-and-cold-starts.md`](docs/14-connection-hardening-and-cold-starts.md).
