# Python Ecommerce API — Project Plan & Progress Log

A production-oriented ecommerce REST API built as a **modular monolith** with FastAPI,
SQLAlchemy 2.0 and PostgreSQL.

This file is the single source of truth for *what has been built, why, and how it was
verified*. It is updated at the end of every completed step.

> **Scope note:** This is a progress/decision log, not API documentation. A README,
> generated API docs and a test suite are explicitly deferred until requested.

---

## 1. Project Overview

| | |
|---|---|
| **Project root** | `D:\python\python-ecommerce` |
| **Started** | 2026-10-15 |
| **Current step** | **Step 26 — Login** (Steps 1–25 complete) |
| **Phases complete** | 4 of 12 |
| **Steps complete** | 25 of 74 |

### Goals

Product management · Category management · User registration & authentication · JWT access
tokens · Role-based access control · Product search, filtering, sorting, pagination ·
Shopping cart · Inventory & stock management · Customer addresses · Orders & order items ·
Checkout · Payment integration · Payment status tracking · Payment webhooks · Order
cancellation & refunds · Centralized error handling · Secure configuration · Logging ·
Docker deployment · CI/CD with GitHub Actions

### Explicitly out of scope

Microservices, RabbitMQ/Kafka, inter-service communication, distributed transactions,
Redis, Celery, background workers, observability platforms, test suites, generated
documentation. Any of these may be added later only if a concrete requirement justifies it.

---

## 2. Technology Stack

| Concern | Choice | Introduced in |
|---|---|---|
| Language | Python 3.12.10 (PythonCore, system-installed) | Step 1, changed Step 3a |
| Package/env manager | `uv` 0.12.10 | Step 1 |
| Lint & format | Ruff 0.17.0 | Step 1 |
| Configuration | `pydantic-settings` 2.16.0 | Step 2 |
| Validation/serialization | Pydantic 2.14.1 | Step 2 |
| Web framework | FastAPI 0.143.1 (Starlette 1.8.0) | Step 3 |
| ASGI server | Uvicorn 0.54.0 (`[standard]`) | Step 3 |
| Database | PostgreSQL 18.6 (`postgres:18.6-alpine`, Docker) | Step 5 |
| Driver | Psycopg 3.3.6 (`psycopg[binary]`) | Step 6 |
| ORM | SQLAlchemy 2.1.5 (typed mappings, `select()` API) | Step 7 |
| Migrations | Alembic | Step 9 |
| JWT | PyJWT | Step 27 |
| Password hashing | `pwdlib` with Argon2 | Step 25 |
| Containerization | Docker / Docker Compose | Step 5, 66–68 |
| CI/CD | GitHub Actions | Step 71 |
| Reverse proxy | Nginx + HTTPS | Step 73 |

**Dependency policy:** no package is installed before the step that requires it.

---

## 3. Architecture

### Request flow

```
HTTP Request
    │
    ▼
API Router  ──  endpoints, path/query params, request & response schemas,
    │           HTTP status codes, dependency injection
    ▼
Service     ──  business rules, orchestration, state-dependent validation,
    │           transaction boundaries, application exceptions
    ▼
Repository  ──  database queries and persistence only
    │
    ▼
SQLAlchemy  ──  typed ORM models, constraints, indexes, relationships
    │
    ▼
PostgreSQL
```

### Layer rules

- **Routers** hold no business logic and no database queries.
- **Services** hold no HTTP concepts (no `HTTPException`, no status codes).
- **Repositories** hold no business workflows.
- **ORM models** are never returned directly as API responses; Pydantic schemas are.
- Separate schemas for create / update / response where they differ.
- Internal fields (e.g. password hashes) are never exposed in a response schema.

### Design constraints

- No interfaces, ABCs, factories or generic repository frameworks without a concrete problem.
- Money is never stored or calculated in floating point — decimal/integer with explicit currency.
- Schema changes are migration-controlled; `Base.metadata.create_all()` is never the
  production mechanism (the SQLAlchemy equivalent of NestJS `synchronize: false`).
- Transactions wrap operations that must succeed or fail together.

---

## 4. Target Project Structure

Built incrementally. Directories are created in the step that needs them, not up front.

```
python-ecommerce/
├── app/
│   ├── __init__.py              [done] Step 1
│   ├── main.py                  [done] Step 3
│   ├── api/
│   │   ├── __init__.py          [done] Step 3
│   │   ├── health.py            [done] Step 3
│   │   └── router.py            Step 16
│   ├── core/
│   │   ├── __init__.py          [done] Step 2
│   │   ├── config.py            [done] Step 2
│   │   ├── exceptions.py        Step 59
│   │   └── security.py          Step 25
│   ├── db/
│   │   ├── __init__.py          [done] Step 7
│   │   ├── base.py              [done] Step 7
│   │   └── session.py           [done] Step 7
│   ├── modules/
│   │   ├── products/            Steps 12-19
│   │   ├── categories/          Steps 20-23
│   │   ├── users/               Steps 24-31
│   │   ├── inventory/           Steps 32-35
│   │   ├── cart/                Steps 36-40
│   │   ├── addresses/           Steps 41-43
│   │   ├── orders/              Steps 45-52
│   │   └── payments/            Steps 53-58
│   └── common/                  as needed
├── alembic/                     Step 9
├── .env                         [done] Step 2  (never committed)
├── .env.example                 [done] Step 2
├── .gitignore                   [done] Step 1
├── .python-version              [done] Step 1
├── alembic.ini                  Step 9
├── docker-compose.yml           [done] Step 5
├── Dockerfile                   Step 66
├── PROJECT_PLAN.md              [done] this file
├── pyproject.toml               [done] Step 1
└── uv.lock                      [done] Step 1
```

---

## 5. Roadmap

Legend: ✅ complete · 🔵 current · ⬜ pending

### Phase 1 — Project Foundation

| # | Step | Status |
|---|---|---|
| 1 | Initialize project with `uv`, verify Python, create venv, initial directory structure, `.gitignore` | ✅ |
| 2 | `.env`, `.env.example`, Pydantic Settings, typed application configuration | ✅ |
| 3 | FastAPI entry point, Uvicorn, health endpoint | ✅ |
| 4 | Explain request lifecycle, ASGI, Uvicorn, routing, startup | ✅ |

### Phase 2 — PostgreSQL and SQLAlchemy

| # | Step | Status |
|---|---|---|
| 5 | PostgreSQL locally via Docker Compose | ✅ |
| 6 | Database connection configuration, PostgreSQL driver | ✅ |
| 7 | Engine, session factory, declarative base, DB dependency | ✅ |
| 8 | Explain sessions, connections, transactions, lifecycle, cleanup | ✅ |
| 9 | Configure Alembic | ✅ |
| 10 | First model and migration; apply and inspect | ✅ |
| 11 | Explain why `create_all()` must not replace migrations in production | ✅ |

### Phase 3 — Product Module

| # | Step | Status |
|---|---|---|
| 12 | Design product table and constraints | ✅ |
| 13 | Pydantic request/response schemas | ✅ |
| 14 | Product repository | ✅ |
| 15 | Product service and business rules | ✅ |
| 16 | FastAPI routes with dependency injection | ✅ |
| 17 | Create, list, get-by-ID, update, delete endpoints | ✅ |
| 18 | Pagination, filtering, sorting, search, validation | ✅ |
| 19 | Explain full request lifecycle with a real product request | ✅ |

### Phase 4 — Categories and Relationships

| # | Step | Status |
|---|---|---|
| 20 | Implement categories | ✅ |
| 21 | Product–category relationships | ✅ |
| 22 | Explain FKs, relationship loading, lazy vs eager, N+1 | ✅ |
| 23 | Constraints and indexes | ✅ |

### Phase 5 — Users and Authentication

| # | Step | Status |
|---|---|---|
| 24 | User model and migration | ✅ |
| 25 | Registration and password hashing | ✅ |
| 26 | Login | 🔵 |
| 27 | Generate and validate JWT access tokens | ⬜ |
| 28 | Current-user retrieval via FastAPI dependencies | ⬜ |
| 29 | Protect endpoints with authentication | ⬜ |
| 30 | Roles and permissions (customer / administrator) | ⬜ |
| 31 | Explain token expiration, password security, authN vs authZ, JWT mistakes | ⬜ |

### Phase 6 — Inventory

| # | Step | Status |
|---|---|---|
| 32 | Inventory and stock quantities | ⬜ |
| 33 | Stock adjustment and availability rules | ⬜ |
| 34 | Prevent negative inventory, handle concurrent stock changes | ⬜ |
| 35 | Explain transactions, row locking / conditional updates, race conditions | ⬜ |

### Phase 7 — Shopping Cart

| # | Step | Status |
|---|---|---|
| 36 | Cart and cart-item models | ⬜ |
| 37 | Cart retrieval and item management endpoints | ⬜ |
| 38 | Quantity changes and item removal | ⬜ |
| 39 | Price and availability handling in a cart | ⬜ |
| 40 | When to calculate prices and validate inventory (never trust client prices) | ⬜ |

### Phase 8 — Addresses and Checkout Preparation

| # | Step | Status |
|---|---|---|
| 41 | Customer addresses | ⬜ |
| 42 | Associate addresses with users | ⬜ |
| 43 | Shipping and checkout data contracts | ⬜ |
| 44 | Order creation design with transaction boundaries | ⬜ |

### Phase 9 — Orders and Checkout

| # | Step | Status |
|---|---|---|
| 45 | Order and order-item models | ⬜ |
| 46 | Immutable order-item snapshots (name, SKU, quantity, unit price) | ⬜ |
| 47 | Checkout and order creation | ⬜ |
| 48 | Validate inventory, atomic stock updates | ⬜ |
| 49 | Order statuses and valid state transitions | ⬜ |
| 50 | Clear/update cart only after successful order creation | ⬜ |
| 51 | Order history, order details, authorized cancellation | ⬜ |
| 52 | Explain idempotency, transaction failures, concurrent checkouts | ⬜ |

### Phase 10 — Payments

| # | Step | Status |
|---|---|---|
| 53 | Payment abstraction for the chosen provider | ⬜ |
| 54 | Integrate payment provider in test/sandbox mode | ⬜ |
| 55 | Payment status handling | ⬜ |
| 56 | Validate webhook signatures | ⬜ |
| 57 | Handle duplicate and out-of-order webhook events | ⬜ |
| 58 | Refund and cancellation workflows | ⬜ |

### Phase 11 — Application Hardening

| # | Step | Status |
|---|---|---|
| 59 | Centralized exception handling, consistent error responses | ⬜ |
| 60 | Structured logging and request correlation IDs | ⬜ |
| 61 | Configuration validation and secret handling review | ⬜ |
| 62 | CORS and security headers | ⬜ |
| 63 | Rate limiting where justified | ⬜ |
| 64 | Review indexes, query performance, transactions, connection pool | ⬜ |
| 65 | Review authorization, input validation, data exposure, API risks | ⬜ |

### Phase 12 — Containerization and Deployment

| # | Step | Status |
|---|---|---|
| 66 | Production-oriented Dockerfile | ⬜ |
| 67 | Finalize Docker Compose for local development | ⬜ |
| 68 | Environment variables and persistent PostgreSQL storage | ⬜ |
| 69 | Explain image builds, containers, volumes, networks, startup deps | ⬜ |
| 70 | Explain running migrations safely during deployment | ⬜ |
| 71 | GitHub Actions workflow for build and checks | ⬜ |
| 72 | Deployment options and deployment flow | ⬜ |
| 73 | Deployment behind Nginx with HTTPS | ⬜ |
| 74 | Explain secret management, rollback, backups, monitoring | ⬜ |

---

## 6. Step Log

### ✅ Step 1 — Project Initialization

**Completed:** 2026-10-15

#### Objective

Create a reproducible, isolated Python project: pinned interpreter, dependency manifest,
lockfile, virtual environment, root package, and a `.gitignore` that prevents secrets from
ever reaching Git.

#### Environment findings

| Check | Result |
|---|---|
| `D:\python` | Empty — clean slate |
| `python` on PATH | **Absent** — Microsoft Store alias stub only |
| Installed Python | 3.14.7 via Python install manager, reachable only through `py` |
| `uv` | 0.12.10 |
| `git` | 2.53.0 |

#### Decisions

**1. Pinned Python 3.12, not the installed 3.14.**
`psycopg[binary]`, `pydantic-core` and Argon2 bindings ship compiled extensions. 3.12 has
guaranteed prebuilt wheels everywhere; a newer interpreter risks a source build requiring a
C compiler and Rust toolchain on Windows. 3.12 also matches the `python:3.12-slim` Docker
base image planned for Phase 12, giving dev/prod parity. uv manages the interpreter, so the
system 3.14 is untouched.
*Alternative:* 3.13/3.14 are legitimate for greenfield work in 2026. Revisiting later is a
one-line change to `.python-version` plus a CI re-run.

**2. Project root is `D:\python\python-ecommerce`**, not `D:\python`, keeping the Git
repository scoped to the project.

**3. Added Ruff immediately; nothing else.**
Linting from the first line of code is cheaper than retrofitting. All runtime dependencies
remain deferred to their own steps.

**4. Only `app/` exists.** `app/core/`, `app/db/`, `app/modules/*` are created in the steps
that need them. Empty packages are architectural theater.

#### Deviations from the uv scaffold

| What uv generated | What was done | Why |
|---|---|---|
| `src/python_ecommerce/` packaged layout with `[project.scripts]` entry point | Deleted; replaced with `app/` package and `package = false` | uv 0.12 `--app` defaults to a CLI/library shape. The target layout is a web service run via `uv run uvicorn app.main:app` from the project root. |
| An `authors` entry containing a corporate email, auto-filled from Git config | Removed | It would have committed identifiable work contact details to a repository. A non-packaged application has no need to publish author metadata. Re-add deliberately if wanted. |
| Minimal `.gitignore` (9 lines) | Expanded to cover `.env*`, caches, editors, runtime artefacts | The generated file did **not** ignore `.env`. |
| No link-mode setting | `link-mode = "copy"` | uv cache on `C:`, project on `D:`. Windows cannot hardlink across volumes, producing a warning on every install. |

#### Files created

| File | Purpose |
|---|---|
| `pyproject.toml` | Project metadata, dependency groups, uv and Ruff configuration |
| `uv.lock` | Exact resolved versions with hashes — **committed** for reproducibility |
| `.python-version` | Pins `3.12` for uv (equivalent to `.nvmrc`) — **committed** |
| `.gitignore` | Excludes secrets, venv, caches, editor and runtime artefacts |
| `app/__init__.py` | Makes `app` an importable regular package |
| `.venv/` | Virtual environment — **not** committed |

#### Key configuration rationale

- **`requires-python = ">=3.12,<3.13"`** — the upper bound is deliberate. This field drives
  dependency *resolution*: uv must produce a lockfile valid for every interpreter in the
  declared range, so an open `>=3.12` can silently hold packages back. Result in `uv.lock`:
  `requires-python = "==3.12.*"`. A *library* would want the broad range; this is an
  application with a pinned base image.
- **`[dependency-groups] dev`** (PEP 735) — keeps Ruff out of `[project.dependencies]`, so
  `uv sync --no-dev` in the production image excludes it.
- **`package = false`** — this is an application, not a distribution. Visible in `uv.lock`
  as `source = { virtual = "." }`. Consequence: `app` is importable because the **project
  root is the working directory**, not because anything was installed into `site-packages`.
- **Ruff rules `E, W, F, I, B, C4, UP, SIM, RUF`** — `F` catches undefined names and unused
  imports; `I` enforces import ordering (eliminates import-block merge conflicts); `B`
  catches real bug patterns such as mutable default arguments, which matters because FastAPI
  route signatures are full of defaults; `UP` enforces modern idioms for the target version.

#### Verification performed

| Check | Result |
|---|---|
| `uv sync` | Clean, no hardlink warning |
| `uv run python -c "import sys; print(sys.version, sys.executable)"` | `3.12.14`, `D:\python\python-ecommerce\.venv\Scripts\python.exe` |
| `uv run python -c "import app"` | Succeeded |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check .` | 1 file already formatted |
| `git status --porcelain` | Exactly 5 entries; `.venv/` and `.ruff_cache/` correctly absent |
| `git check-ignore -v .env` | `.gitignore:3:.env` — **secret exclusion proven, not assumed** |

#### Risk & Controls Note

- **Regulatory/data protection:** No personal or financial data processed. Corporate email
  removed from `pyproject.toml` to avoid committing identifiable contact details.
- **Security:** `.gitignore` denies `.env`/`.env.*` with an explicit `!.env.example`
  allowance, verified empirically — secret leakage via Git is the most common credential
  compromise vector for this project type. `uv.lock` pins exact versions with hashes
  (supply-chain integrity, reproducible and auditable builds). Ruff is a local binary with
  no network or telemetry behaviour.
- **Data residency:** All artefacts local. Package downloads from PyPI (US-hosted) — standard
  open-source acquisition, no proprietary or customer data transmitted.
- **Controls required now:** None.
- **Residual risk: Low** — local scaffold only, no secrets, no data, no exposed services.

#### Not done (correctly deferred)

No initial Git commit yet · no `.env` or settings · no FastAPI · no database · no tests · no README.

---

### ✅ Step 2 — Environment Configuration

**Completed:** 2026-10-15

#### Objective

Establish typed, validated configuration loaded from environment variables, so every later
step (database URL, JWT secret, payment keys) plugs into one mechanism instead of scattered
`os.environ.get(...)` calls that fail silently.

#### Decisions

**1. `APP_` prefix on every application variable (`env_prefix="APP_"`).**
Unprefixed `DEBUG` is a genuine collision risk — Node's `debug` package uses `DEBUG=*`, and a
real environment variable outranks `.env`, so a stray value would break boolean parsing. The
prefix also cleanly separates application variables from the unprefixed `POSTGRES_*`
variables Docker Compose will read from the same `.env` file in Step 5.
*Cost:* field `name` reads from `APP_NAME`, accessed as `settings.name`.

**2. `extra="ignore"`.** Required, because `.env` becomes a shared file: Compose reads
variables from it that `Settings` does not declare. With the default `extra="forbid"` the
application would crash on Compose's own variables.

**3. `frozen=True`.** Settings are immutable after construction — no global mutable state,
and no module accidentally mutating configuration at runtime.

**4. `get_settings()` with `@lru_cache`, not a module-level `settings` object.**
Parses `.env` once per process, works directly as a FastAPI dependency
(`Depends(get_settings)`), and is overridable in tests via
`app.dependency_overrides` or `get_settings.cache_clear()`. A module-level instance would
validate at *import* time, making failures harder to attribute and tests harder to isolate.

**5. `StrEnum` for `Environment` and `LogLevel`** (Python 3.11+). Invalid values are rejected
at startup with a message listing the permitted options, rather than causing a confusing
failure later. The `StrEnum` base keeps the members usable as plain strings.

**6. No secrets introduced yet.** JWT and database settings arrive in their own steps
(27 and 6). The `production`/`debug` validator establishes the *fail-fast pattern* those
secrets will use, without inventing placeholder credentials now.

#### Files created

| File | Purpose | Committed |
|---|---|---|
| `app/core/__init__.py` | Marks `app.core` as a package | yes |
| `app/core/config.py` | `Environment`, `LogLevel`, `Settings`, `get_settings()` | yes |
| `.env.example` | Documented placeholder configuration | **yes** |
| `.env` | Local development values | **no — git-ignored** |

#### Configuration precedence

Highest priority first: `Settings(...)` arguments (tests) → real environment variables
(Docker, CI) → `.env` file (local only) → declared defaults.

This ordering is what makes the same image run locally and in production: the deployment
platform injects real environment variables that outrank anything in a file.

#### Validation implemented

| Rule | Mechanism | Effect |
|---|---|---|
| `APP_DEBUG` must be false in production | `@model_validator(mode="after")` | Startup fails — prevents leaking stack traces and internal paths to API clients |
| `APP_ENVIRONMENT` must be a known value | `StrEnum` | Startup fails listing valid options |
| `APP_LOG_LEVEL` must be a valid level | `StrEnum` | Startup fails listing valid options |
| `APP_API_V1_PREFIX` must start with `/`, no trailing `/` | `@field_validator` | Startup fails — prevents malformed route paths |
| `APP_NAME` must be non-empty | `Field(min_length=1)` | Startup fails |

#### Verification performed

| Check | Result |
|---|---|
| Settings load from `.env` | All five fields correct; `log_level=DEBUG`, `is_production=False` |
| `APP_LOG_LEVEL=WARNING` as a real env var | Overrode `.env`'s `DEBUG` — precedence confirmed |
| `get_settings() is get_settings()` | `True` — cache working |
| `settings.debug = True` | `ValidationError` — immutability confirmed |
| `APP_ENVIRONMENT=production APP_DEBUG=true` | **Rejected at startup** with the explicit message |
| `APP_ENVIRONMENT=production APP_DEBUG=false` | Accepted; `is_production=True` |
| `APP_ENVIRONMENT=prod` | Rejected: `Input should be 'local', 'staging' or 'production'` |
| `APP_API_V1_PREFIX=api/v1/` | Rejected: `Value error, must start with '/'` |
| `ruff check` / `ruff format --check` | Passed, 4 files |
| `git status` | `.env.example` tracked; **`.env` absent**; `git check-ignore` confirms |

#### Risk & Controls Note

- **Regulatory/data protection:** No personal or financial data. No secrets exist in the
  repository; `.env.example` contains only non-sensitive placeholders.
- **Security:** The production/debug validator is a preventive control against verbose error
  disclosure (OWASP API8 Security Misconfiguration) — it fails the application at startup
  rather than degrading silently. Typed enums eliminate a class of misconfiguration where an
  unrecognised value is silently coerced or ignored. `frozen=True` prevents runtime tampering
  with configuration. Precedence ordering ensures platform-injected secrets always outrank
  file-based values, which is the control that keeps secrets out of images.
- **Data residency:** None applicable — local configuration only, nothing transmitted.
- **Controls required now:** None. **Deferred:** real secret management at Step 61/74;
  database credentials at Step 6 must come from the platform, never from a committed file.
- **Residual risk: Low.**

#### Notes / observations

- Files were found **staged** in Git (by the editor, not by this session) with **no commits
  yet**; `.env` is correctly excluded from the staged set.
- The branch is `master`. Consider renaming to `main` before Step 71 introduces GitHub Actions.

#### Not done (correctly deferred)

No FastAPI application · no database settings · no JWT settings · no logging configuration
(Step 60 wires `log_level` into an actual logger) · no secrets.

---

### ✅ Step 3 — FastAPI Entry Point & Health Endpoint

**Completed:** 2026-10-15

#### Objective

Create the ASGI application, wire configuration into it, expose a health endpoint, and serve
it with Uvicorn — the first step producing a running HTTP server.

#### Decisions

**1. `create_app()` factory plus a module-level `app = create_app()`.**
Uvicorn needs an importable ASGI object (`app.main:app`), so the module-level instance is
required. The factory exists alongside it because it accepts an optional `Settings`,
allowing an application to be constructed with specific configuration instead of relying on
process-wide state. Trivial to add now; invasive to retrofit once routers, middleware and
exception handlers are registered.

**2. Response model inferred from the return type annotation, not `response_model=`.**
`def health() -> HealthResponse` is sufficient in modern FastAPI — it drives serialisation,
response filtering and the OpenAPI schema. Passing `response_model=` as well is redundant,
and the two can silently disagree. Verified: `HealthResponse` appears in
`components.schemas` with `status` constrained to the constant `"ok"`.

**3. `/health` is mounted at the root, outside `api_v1_prefix`.**
Health probes are consumed by load balancers and orchestrators, not API clients. Coupling
them to an API version would mean reconfiguring infrastructure on every version bump.

**4. The health response is deliberately minimal — `{"status": "ok"}` only.**
It is unauthenticated, so it discloses no environment name, version, hostname, or dependency
state. Tutorial health endpoints commonly return all of those; that is reconnaissance data
for an attacker. A richer, authenticated readiness endpoint arrives once there is a database
to check (Step 7+), where the liveness/readiness distinction becomes meaningful.

**5. Interactive documentation is disabled in production.**
`docs_url`, `redoc_url` and `openapi_url` are set to `None` when
`settings.is_production`, so the routes are never registered. This is a route-level control,
not a cosmetic hide — the schema describing every endpoint, parameter and model is simply
not served. **Verified: all three return 404 in production while `/health` returns 200.**

**6. No `lifespan` handler yet.** Nothing requires startup or shutdown work. It arrives in
Step 7 to own the database engine's lifecycle.

#### Files created / modified

| File | Change |
|---|---|
| `app/main.py` | **new** — `create_app()` factory and module-level `app` |
| `app/api/__init__.py` | **new** — API layer package |
| `app/api/health.py` | **new** — `HealthResponse` schema and `/health` route |
| `app/__init__.py` | modified — added `__version__ = "0.1.0"` for the OpenAPI document |
| `pyproject.toml`, `uv.lock` | modified — FastAPI, Uvicorn and 11 transitive packages |

#### Verification performed

| Check | Result |
|---|---|
| `app.title` / `app.version` / `app.debug` | `Python Ecommerce API` / `0.1.0` / `True` — settings reached the app |
| Generated OpenAPI document | `3.1.0`; one path `GET /health`; `HealthResponse` with `const: "ok"` |
| `GET /health` (local) | `200`, `content-type: application/json`, body `{"status":"ok"}` |
| `GET /docs`, `GET /openapi.json` (local) | `200` both |
| `GET /nope` | `404` with `{"detail":"Not Found"}` |
| `POST /health` | `405 Method Not Allowed` — routing is method-aware |
| `GET /health` (production) | `200` — probe still works |
| `GET /docs` (production) | **`404`** |
| `GET /redoc` (production) | **`404`** |
| `GET /openapi.json` (production) | **`404`** |
| `ruff check` / `ruff format --check` | Passed, 7 files |

#### Notes / observations

- `uvloop` is not installed — it is Linux/macOS only, so Windows uses the standard asyncio
  event loop. The Linux container in Phase 12 will pick it up automatically.
- Starlette 1.8 represents included routers as `_IncludedRouter` objects, so iterating
  `app.routes` for paths no longer works; inspect `app.openapi()["paths"]` instead.

#### Risk & Controls Note

- **Regulatory/data protection:** No personal or financial data processed. The health
  endpoint returns a single constant field and cannot leak data by construction.
- **Security:** Two preventive controls implemented and tested. (a) **Documentation exposure
  control** — OpenAPI/Swagger/ReDoc routes are not registered in production, mitigating
  reconnaissance (OWASP API8 Security Misconfiguration, API9 Improper Inventory Management).
  (b) **Minimal unauthenticated disclosure** — the probe reveals no environment, version or
  dependency state. Residual gap: `debug` is wired to FastAPI but is already prevented from
  being true in production by the Step 2 validator, so verbose tracebacks cannot reach
  clients. Uvicorn bound to `127.0.0.1` for local testing; no external exposure.
- **Data residency:** None applicable — local process only.
- **Required controls or approvals:** None now. **Deferred:** security headers and CORS
  (Step 62), rate limiting on public endpoints (Step 63), structured access logging with
  correlation IDs (Step 60), authenticated readiness endpoint (Step 7+).
- **Residual risk: Low.**

#### Not done (correctly deferred)

No database · no routers beyond health · no middleware · no CORS or security headers · no
exception handlers · no logging configuration · no lifespan management.

---

### ✅ Step 3a — Toolchain Repair: Replaced uv-Managed Python *(unplanned)*

**Completed:** 2026-10-18

#### Problem

`uv run <anything>` failed in the user's terminals with:

```
No Python at '"C:\Users\Rashid\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe'
```

Note the stray `"` inside the quoted path. The same commands succeeded in every shell
launched from the agent session, which made the fault appear intermittent for several
rounds of diagnosis.

#### Root cause

uv's **managed CPython 3.12.14 build** and the launcher shims it generates. The
`uv python install 3.12` run in Step 1 reported
`error: Missing expected target directory for Python minor version link` and left behind
broken artifacts. That error was **incorrectly dismissed as transient at the time** — it was
reproducible and was the origin of the whole failure.

Verbose output (`uv run -v`) was decisive: uv resolved the project, the lockfile and the
interpreter correctly, then failed in the process it spawned —

```
DEBUG Using Python 3.12.14 interpreter at: D:\...\.venv\Scripts\python.exe
DEBUG Running `python --version`
No Python at '"C:\...'
DEBUG Command exited with code: 103
```

— proving the error came from a launcher shim, not from uv itself. A broken shim at
`C:\Users\Rashid\.local\bin\python3.12.exe` (45 KB trampoline, same PATH directory as
`uv.exe`) failed directly with
`uv trampoline failed to spawn Python child process / entity not found (os error 3)`.

#### Resolution

Rather than patch individual artifacts, the managed-Python layer was removed entirely.

| Action | Detail |
|---|---|
| `py install 3.12` | Real CPython **3.12.10** from python.org via the Python install manager; installer signature verified |
| Rebuilt `.venv` | `uv venv --python ...\pythoncore-3.12-64\python.exe`; `pyvenv.cfg home` now points at the system install |
| `pyproject.toml` | Added `python-preference = "only-system"` and `python-downloads = "never"` |
| `uv python uninstall 3.12` | Deleted the broken managed build |
| Renamed broken shim | `~\.local\bin\python3.12.exe` → `.broken` (reversible) |
| VS Code setting | `"python.terminal.activateEnvironment": false` — `uv run` resolves `.venv` itself; auto-activation was a competing mechanism |

#### Verification

| Check | Result |
|---|---|
| `uv run python --version` (PowerShell and cmd) | `3.12.10` |
| `uv sync` | 21 packages from `uv.lock`, **no version drift** |
| `uv run uvicorn app.main:app --reload` | Started, reloader active |
| `GET /health` against it | `200 {"status":"ok"}` |
| `uv run ruff check .` | All checks passed |
| `pyvenv.cfg home` | `C:\Users\Rashid\AppData\Local\Python\pythoncore-3.12-64` |

#### Accepted risk

**3.12.10 is the final binary release of the 3.12 series** (3.12 is in security-fix-only
mode; later patches ship as source only). The replaced uv build was 3.12.14, so the local
interpreter now lacks CVE fixes from 3.12.11–3.12.14.

- **Impact confined to the development machine.** Production uses `python:3.12-slim`
  (Phase 12), which tracks current patches.
- **Mitigation if closure is required:** move the pin to 3.13, which has current binary
  releases — changes `.python-version`, `requires-python` and Ruff's `target-version`.
- **Accepted** for local development; **review point at Step 64**.

#### Lessons recorded

1. A toolchain error reported during setup must be treated as a defect until proven
   otherwise. "It still appears to work" is not verification.
2. When a failure cannot be reproduced across shells, get verbose output from the failing
   environment rather than inferring cause from working ones.
3. `python-downloads = "never"` is a supply-chain control, not only a convenience: the
   toolchain can no longer fetch and execute an interpreter mid-build. Relevant to CI
   determinism at Step 71.

---

### ✅ Step 4 — Request Lifecycle, ASGI, Uvicorn & Startup

**Completed:** 2026-10-18 · Explanation step — **no production code added**.

#### What was demonstrated

The real application was driven through the **raw ASGI interface** — no HTTP server, no
network — by hand-building the `scope` dict Uvicorn would normally construct and collecting
the messages the app sent back. Run from a throwaway script outside the repository.

```
GET /health   ->  http.response.start  status 200
                  headers: content-length: 15, content-type: application/json
                  http.response.body   b'{"status":"ok"}'

GET /nope     ->  status 404,  b'{"detail":"Not Found"}'
```

#### Key finding recorded: where handlers execute

| Endpoint style | Thread observed |
|---|---|
| `def` (synchronous) | `AnyIO worker thread` |
| `async def` | `MainThread` (the event loop) |

This empirically confirms the Step 3 decision to write endpoints as plain `def`. Because the
project uses **synchronous SQLAlchemy**, handlers perform blocking I/O; FastAPI offloads
`def` handlers to a worker thread so the event loop is never blocked. Writing those same
handlers as `async def` would block the loop and stall every concurrent request — the most
common FastAPI performance defect, and the one this architecture avoids by default.

#### Incidental confirmation of the Step 1 layout decision

Running the demo script by absolute path failed with `ModuleNotFoundError: No module named
'app'`, because Python puts the *script's* directory on `sys.path`, not the working
directory. This is the direct consequence of `package = false`: `app` is importable only
because the project root is the working directory. Resolved for the demo with `PYTHONPATH`.
Relevant to Step 66 — the Dockerfile must set `WORKDIR` accordingly.

#### Risk & Controls Note

- **Regulatory/data protection:** No data involved. No production code or configuration
  changed; the demonstration script lives outside the repository.
- **Security:** None applicable — an explanation step with no new surface. One
  forward-looking note: the ASGI `scope` carries client IP, headers and the raw path, and is
  the data that Step 60's structured logging will draw on. Logging it wholesale would capture
  `Authorization` headers and query-string values; the logging step must redact by
  allow-list, not by blocklist.
- **Residual risk: Low.**

---

### ✅ Step 5 — PostgreSQL via Docker Compose

**Completed:** 2026-10-18

#### Objective

Run PostgreSQL locally as a disposable, version-pinned container, with credentials supplied
from the git-ignored `.env` and the port exposed only to the loopback interface.

#### Environment findings

| Finding | Consequence |
|---|---|
| Docker 27.5.1, Compose v2.32.4 installed; daemon stopped | User started Docker Desktop |
| **Native `postgresql-x64-18` service already running on `0.0.0.0:5432`** | Container published on host port **5433** instead; the existing service was left untouched |

#### Decisions

**1. Host port 5433, container port 5432.** The native service owns 5432. Rather than stop a
service the user may rely on, the container publishes elsewhere. The *container's* internal
port stays 5432, so nothing inside the compose network is unusual.

**2. `127.0.0.1:5433:5432`, not `5433:5432`.** Omitting the host address makes Docker publish
on `0.0.0.0`, exposing the database to every machine on the local network. Verified: the
container is reachable on `127.0.0.1` and **not** on the host's LAN address.

**3. Exact image pin `postgres:18.6-alpine`.** `18-alpine` is a moving tag and would change
the engine under the project on a later pull. Digest observed:
`sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873`.

**4. `${VAR:?message}` interpolation for all three credentials.** Compose refuses to start
if a variable is missing, instead of silently creating a database with defaults.

**5. `POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256`.** Forces
SCRAM rather than relying on the image default, and requires a password even over the local
socket. Verified: `rolpassword` begins `SCRAM-SHA-256`, and an unauthenticated local `psql`
is rejected.

**6. Generated 24-character random password**, not `postgres`/`postgres`. Default
credentials are the most common cause of exposed development databases.

**7. Named volume, not a bind mount.** Avoids Windows host filesystem permission problems and
keeps the data managed by Docker.

#### Problem encountered and fixed

The first `up` left the container restarting and unhealthy:

```
Error: in 18+, these Docker images are configured to store database data in a
       format which is compatible with "pg_ctlcluster" ...
       The suggested container configuration for 18+ is to place a single mount
       at /var/lib/postgresql
```

**PostgreSQL 18 changed the Docker data directory convention.** Data now lives in a
major-version subdirectory (`/var/lib/postgresql/18/docker`) so `pg_upgrade --link` works
across versions. The volume must mount at `/var/lib/postgresql`; the pre-18 path
`/var/lib/postgresql/data` is ignored and the container refuses to start. Fixed, volume
recreated.

#### Files created / modified

| File | Change |
|---|---|
| `docker-compose.yml` | **new** — pinned `db` service, healthcheck, loopback binding, named volume |
| `.env` | modified — added `POSTGRES_USER/PASSWORD/DB/PORT` (unprefixed) |
| `.env.example` | modified — same keys with `CHANGE_ME` password and a generator command |

#### Verification performed

| Check | Result |
|---|---|
| `docker compose config` | Valid; resolved `host_ip: 127.0.0.1, published: 5433, target: 5432` |
| Container health | `Up (healthy)` via `pg_isready` |
| `select version()` | `PostgreSQL 18.6 on x86_64-pc-linux-musl` |
| `current_user @ current_database()` | `ecommerce @ ecommerce` |
| `rolpassword` prefix | `SCRAM-SHA-256` |
| `show data_directory` | `/var/lib/postgresql/18/docker` (PG18 layout) |
| Write/read round trip | `CREATE TABLE`, `INSERT 0 1`, row read back |
| **Persistence across container replacement** | Row survived recreate onto the pinned image |
| Unauthenticated local `psql` | **Rejected** — `no password supplied` |
| App settings after adding `POSTGRES_*` | Still exactly 5 fields — unprefixed vars correctly ignored |
| Native `postgresql-x64-18` | Still `Running` / `Automatic` — untouched |
| Container on host LAN address `172.22.208.1:5433` | **Not reachable** — isolation confirmed |
| `git status` | `.env` still absent; `docker-compose.yml` and `.env.example` tracked |

#### Risk & Controls Note

- **Regulatory/data protection:** No personal, customer or financial data stored. The
  database is empty apart from a smoke-test table that was created and dropped. All future
  data in this instance will be **synthetic** per the standing commitments.
- **Security controls implemented and tested:** loopback-only port binding (verified
  unreachable from the LAN); SCRAM-SHA-256 enforced for host and local auth; a generated
  24-character password rather than defaults; fail-closed credential interpolation; exact
  image pin for reproducible, auditable builds.
- **Open finding (pre-existing, not introduced):** the user's **native** PostgreSQL 18
  service listens on `0.0.0.0:5432` — reachable from the local network. Outside this
  project's scope but worth remediating by binding it to `localhost` in its
  `postgresql.conf`. **Residual risk: Medium** until addressed.
- **Data residency:** Container and volume are local. Image pulled from Docker Hub
  (US-hosted) — standard acquisition, no data transmitted.
- **Required controls:** None for this step. **Deferred:** least-privilege application role
  separate from the owner role (Step 64/65) — `ecommerce` is currently the database owner,
  which is acceptable for local development but not a production pattern; TLS for database
  connections (Phase 12).
- **Residual risk: Low** for the containerised database as configured.

#### Not done (correctly deferred)

No driver installed · no `DATABASE_URL` in application settings · no SQLAlchemy engine ·
no models · no migrations. All Steps 6–10.

---

### ✅ Step 6 — Database Connection Configuration & Driver

**Completed:** 2026-10-18

#### Objective

Install the PostgreSQL driver and teach the application how to reach the database, treating
the password as a credential rather than an ordinary string.

#### Decisions

**1. Psycopg 3 (`psycopg[binary]` 3.3.6), not psycopg2.**
Psycopg 3 is the actively developed successor: server-side binding by default (no
client-side string interpolation), native `async` support should it ever be needed, and
first-class SQLAlchemy 2.0 integration. The `[binary]` extra ships prebuilt wheels so no C
compiler is required on Windows.
*Production note:* `[binary]` is discouraged for production Linux images, where
`psycopg[c]` built against the system libpq is preferred. Revisit at Step 66.

**2. Separate credential fields, not a single `DATABASE_URL`.**
A single URL bundles the password into a string that gets logged, echoed in tracebacks and
copied into error reports. Separate fields keep the password isolated in one typed field
that can be masked. The URL is assembled from the parts.
*Alternative:* platforms such as Heroku and Render inject `DATABASE_URL` directly. If one is
ever targeted, accept it as an optional override field rather than replacing this structure.

**3. `db_password: SecretStr` with no default.**
`SecretStr` masks the value in `repr()`, `model_dump()` and `model_dump_json()`. No default,
because a default password is worse than none — defaults get deployed.

**4. `database_url` is a plain `@property`, deliberately NOT a `@computed_field`.**
A computed field would be included in `model_dump()`, writing the password into anything
that serialises settings. Verified absent from the dump.

**5. A separate `database_url_safe` property** with the password replaced by `***`, for
logging and diagnostics. Gives Step 60 a correct value to log instead of hand-rolling
redaction at each call site.

**6. `.env` is now the single source of truth for database credentials.**
`docker-compose.yml` was changed to read `APP_DB_USER` / `APP_DB_PASSWORD` / `APP_DB_NAME`
and map them onto the container's `POSTGRES_*` variables, and to publish on `APP_DB_PORT`.
Previously the same credentials appeared twice under two names, which would drift the first
time someone rotated one of them.

#### Files created / modified

| File | Change |
|---|---|
| `app/core/config.py` | Added 5 database fields, `database_url`, `database_url_safe` |
| `docker-compose.yml` | Sources credentials and host port from `APP_DB_*` |
| `.env` | Replaced `POSTGRES_*` with `APP_DB_*` (single definition each) |
| `.env.example` | Same, with `CHANGE_ME` password and a generator command |
| `pyproject.toml`, `uv.lock` | `psycopg[binary]` + `psycopg-binary` + `tzdata` |

#### Verification performed

| Check | Result |
|---|---|
| `repr(settings.db_password)` | `**********` |
| `model_dump()['db_password']` | `SecretStr('**********')` |
| Plaintext password in `model_dump()` | **False** |
| Plaintext password in `model_dump_json()` | **False** |
| Plaintext password in `repr(settings)` | **False** |
| `'database_url'` key in `model_dump()` | **False** — property, not computed field |
| `database_url_safe` | `postgresql+psycopg://ecommerce:***@127.0.0.1:5433/ecommerce` |
| Real `psycopg.connect()` | `PostgreSQL 18.6`; session `ecommerce / ecommerce / container port 5432` |
| Public tables present | `0` — schema empty, as expected before Step 10 |
| Connection with a wrong password | **Rejected** — `connection failed` |
| `Settings()` with no `.env` reachable | **3 validation errors** (`db_user`, `db_name`, `db_password`) — fail-fast confirmed |
| `docker compose config` after rename | Credentials resolve; `host_ip 127.0.0.1`, `published 5433` |
| `ruff check` / `format --check` | Passed, 7 files |
| App still boots | `ok: Python Ecommerce API` |

#### Risk & Controls Note

- **Regulatory/data protection:** No personal or financial data. Database schema is empty.
- **Security controls implemented and tested:** credential isolated in `SecretStr` and
  proven absent from all three serialisation paths — the control that prevents credentials
  reaching logs, error trackers and crash reports, which is a common breach vector;
  `database_url` kept out of `model_dump()` by design; a masked URL provided so Step 60 has
  no reason to log the real one; no default password, with startup failing closed when the
  credential is absent; one definition per credential, removing rotation drift between the
  app and the container.
- **Known residual exposure:** the plaintext password necessarily exists in memory and in
  the `.env` file (git-ignored). Unavoidable for local development. In production the value
  must come from a managed secret store via environment injection — never a file in the
  image. Reviewed at Steps 61 and 74.
- **Data residency:** Connections are to `127.0.0.1:5433` only; nothing leaves the machine.
- **Required controls:** None now. **Deferred:** TLS/`sslmode=require` for non-local
  connections (Phase 12); least-privilege application role distinct from the owner
  (Steps 64/65); credential rotation procedure (Step 74).
- **Residual risk: Low.**

#### Not done (correctly deferred)

No SQLAlchemy · no engine or connection pool · no session factory · no declarative base ·
no `get_db` dependency · no models · no migrations. Steps 7–10.

---

### ✅ Step 7 — Engine, Session Factory, Declarative Base & DB Dependency

**Completed:** 2026-10-18 · SQLAlchemy 2.1.5

#### Objective

Create the three objects every later module depends on — engine (connection pool), session
factory (unit of work), `Base` (ORM root) — plus the FastAPI dependency that scopes a
session to a request.

#### Decisions

**1. `Base` lives in `app/db/base.py`, separate from the engine.**
Models import `Base` only. If `Base` lived beside the engine, importing any model would
construct a connection pool — including under Alembic offline mode, which needs no database
at all — and would invite circular imports.

**2. Explicit constraint naming convention on `MetaData`.**
Without it PostgreSQL invents constraint names that cannot be predicted from the models, so
Alembic cannot write a reliable `downgrade()` — you cannot `DROP` a constraint whose name you
do not know. Set before the first model exists, because retrofitting means renaming
constraints across every environment. Verified: `['ck', 'fk', 'ix', 'pk', 'uq']`.

**3. `class Base(DeclarativeBase)`, not `declarative_base()`.**
SQLAlchemy 2.0 style. Subclassing gives real typing support so `Mapped[int]` is understood by
type checkers; the legacy factory returns an untyped `Any`.

**4. One engine per process, created at import.**
The engine owns the pool. A per-request engine would open a new pool each time and exhaust
PostgreSQL's `max_connections`. Engine construction does **not** connect — the first
connection is lazy — so importing it is cheap and a database outage never blocks startup.

**5. `pool_pre_ping=True`** — validates a pooled connection with `SELECT 1` before use.
Without it, a connection killed by a database restart or idle timeout is only discovered
when a real query fails mid-request.

**6. `pool_recycle=1800`** — discard connections older than 30 minutes, ahead of the idle
timeouts imposed by proxies and managed database services.

**7. `autoflush=False`.** SQLAlchemy will not silently emit INSERT/UPDATE before a query;
flushes happen where written. Cost: a pending object is invisible to a later query in the
same session until `flush()`. Chosen for predictable SQL under the repository pattern.

**8. `expire_on_commit=False`.** With the default `True`, reading any attribute after commit
triggers a refresh query; once the request's session is closed that raises
`DetachedInstanceError` *while FastAPI is serialising the response*. This is among the most
common FastAPI + SQLAlchemy bugs.

**9. `get_db` owns session lifetime, NOT transaction boundaries.**
It yields, rolls back on an unhandled exception, and always closes. It does **not** commit —
the service layer decides what a complete unit of work is, per the project's layer rules.
*Alternative considered:* committing in the dependency. Rejected — it makes every request a
single implicit transaction and removes the service layer's ability to commit in stages or
deliberately abandon work.

**10. `DbSession = Annotated[Session, Depends(get_db)]`** so routers read `db: DbSession`.

**11. Readiness probe added at `GET /health/ready`.** The liveness/readiness split promised
in Step 3 is now meaningful. Liveness failure means "restart me"; readiness failure means
"stop routing to me". The body stays minimal and the error detail is generic — database
errors expose host names, drivers and schema details.

**12. `lifespan` handler disposes the engine on shutdown.** Replaces the deprecated
`@app.on_event`. Deliberately does **not** test connectivity at startup: an outage should not
prevent the process from starting, that is what readiness is for.

**13. `APP_DB_ECHO` added, with a production guard.** Echoed SQL includes bound parameter
values, so enabling it in production would write customer and payment data into logs. A
`model_validator` now refuses `db_echo=true` when `APP_ENVIRONMENT=production`, matching the
existing `APP_DEBUG` guard.

#### Defect found by verification and fixed

The first implementation had **no connect timeout**. With the database container stopped,
Docker's port proxy accepts the TCP connection but never completes it, so the readiness
probe **hung for 60 seconds** (`curl` status `000`) instead of failing.

A hanging readiness probe is worse than a failing one: the orchestrator's own probe times
out, and in a real outage every request blocks a worker thread until the thread pool is
exhausted — turning a database outage into a total process hang.

Fixed with `connect_args={"connect_timeout": 5}`. Re-verified: **503 in 5.1 s**.

#### Files created / modified

| File | Change |
|---|---|
| `app/db/__init__.py` | **new** |
| `app/db/base.py` | **new** — `Base`, `NAMING_CONVENTION` |
| `app/db/session.py` | **new** — `engine`, `SessionFactory`, `get_db`, `DbSession` |
| `app/api/health.py` | Added `ReadinessResponse` and `GET /health/ready` |
| `app/main.py` | Added `lifespan` disposing the engine |
| `app/core/config.py` | Added `db_echo` + production guard |
| `pyproject.toml`, `uv.lock` | `sqlalchemy==2.1.5` |

#### Verification performed

| Check | Result |
|---|---|
| Engine URL | `postgresql+psycopg://ecommerce:***@127.0.0.1:5433/ecommerce` — password masked |
| Pool | `QueuePool`, size 5, `pre_ping=True` |
| `Base.metadata.tables` | `[]` — no models yet, as expected |
| Naming convention keys | `['ck', 'fk', 'ix', 'pk', 'uq']` |
| `GET /health` | `200 {"status":"ok"}` |
| `GET /health/ready`, database up | `200 {"status":"ready"}` |
| **`GET /health/ready`, database stopped** | **`503 {"detail":"Service is not ready"}` in 5.1 s** |
| `GET /health` during the outage | `200` — correctly unaffected |
| `GET /health/ready` after restart | `200` — pool recovered with no process restart |
| `ruff check` / `format --check` | Passed, 10 files |

#### Incidental finding

`Set-Content -Encoding utf8` in Windows PowerShell 5.1 writes **UTF-8 with BOM**, which Ruff
flagged in `app/db/__init__.py`. Python source files must be BOM-free. Use the editor tooling
or `ruff format` rather than `Set-Content` for source files.

#### Risk & Controls Note

- **Regulatory/data protection:** No personal or financial data; schema still empty.
- **Security controls implemented:** generic readiness error detail — status code carries the
  decision, the body discloses nothing about which dependency failed, denying an
  unauthenticated caller a degradation signal; `APP_DB_ECHO` blocked in production, preventing
  bound parameter values (which will include customer and payment data) from reaching logs;
  **connect timeout** preventing an outage from escalating into thread-pool exhaustion — a
  genuine availability control, not only a bug fix; engine disposal on shutdown so pooled
  connections close cleanly rather than lingering until the server times them out.
- **Deferred and tracked:** server-side `statement_timeout` so a pathological query cannot
  hold a connection indefinitely (Step 64, with pool sizing); `sslmode=require` for non-local
  connections (Phase 12); least-privilege role distinct from the owner (Steps 64/65);
  operator-side logging of the suppressed readiness cause (Step 60).
- **Residual risk: Low.**

#### Not done (correctly deferred)

No Alembic · no models · no migrations · no repositories or services. Steps 9–15.

---

### ✅ Step 7a — Simplification Pass *(unplanned)*

**Completed:** 2026-10-19

The user reported the code had become hard to follow. Reviewed and removed anything not
earning its place yet. **No behaviour changed** — all endpoints verified identical afterwards.

| Removed | Why it was unnecessary |
|---|---|
| `create_app()` factory and its unused `settings` parameter | Nothing called it with an argument. A module-level `app` is enough until tests exist. |
| `lifespan` handler (`engine.dispose()`) | The OS closes connections on exit. Add back only if shutdown behaviour becomes a real problem. |
| `Environment` and `LogLevel` `StrEnum` classes | `Literal["local","staging","production"]` validates the same way in one line and needs no new class. |
| `log_level` setting | Nothing reads it. Returns in Step 60 with actual logging. |
| `database_url_safe` property | Nothing logs the URL yet. Returns in Step 60. |
| `PostgresDsn.build()` | Replaced with an f-string plus `quote_plus`, which reads far more plainly. |
| `api_v1_prefix` field validator | Guarded against a typo nothing depends on yet. |
| `__version__` | Unused. |
| Two separate production validators | Merged into one 4-line check. |
| `autoflush=False` | SQLAlchemy's default (`True`) is more forgiving: a query sees objects added earlier in the same session. |
| Explicit `rollback()` in `get_db` | Redundant — `close()` already rolls back an open transaction. |
| `pool_recycle=1800` | Guards against proxy idle timeouts that do not exist locally. Returns in Step 64. |
| Long comment blocks | Trimmed to one or two lines each. |

**Kept deliberately** — each is one line and prevents a real problem:
`SecretStr` (keeps the password out of logs) · `connect_timeout` (proven to stop a 60-second
hang) · `pool_pre_ping` (survives database restarts) · `expire_on_commit=False` (prevents
`DetachedInstanceError` during JSON serialisation) · the constraint naming convention
(migrations cannot be undone reliably without it) · the production safety validator.

**Result:** 153 lines of application code across 9 files, largest file 53 lines.

**Re-verified after simplification:** `/health` 200 · `/health/ready` 200 · database stopped
→ 503 in 5.1 s · after restart → 200 · `ruff check` and `format --check` clean.

**Process note:** future steps favour the simplest version that is correct, and introduce
advanced patterns only when a concrete problem calls for them.

---

### ✅ Step 8 — Sessions, Connections, Transactions & Lifecycle

**Completed:** 2026-10-20 · Explanation step — **no code added**.

Demonstrated live against the running database with a throwaway script.

**The connection pool is lazy and self-returning:**

```
connections in use at start : 0
after creating a Session    : 0   (still none - it is lazy)
after running a query       : 1   (borrowed one)
after close()               : 0   (given back to the pool)
```

Creating a `Session` costs nothing. A connection is borrowed on the first query and returned
by `close()` — which is why the `finally: db.close()` in `get_db` matters: skip it and the
pool leaks until it is exhausted and every request hangs.

**Transactions:**

| Action | Result observed |
|---|---|
| INSERT, then `rollback()` | `[]` — work discarded |
| INSERT, then `commit()` | `['from commit']` — permanent |
| INSERT, then `close()` with no commit | `['from commit']` — the new row vanished |

The last line is the important one: **closing without committing discards the work**. This
is why `get_db` needs no explicit `rollback()`, and why a service that forgets `commit()`
silently loses data rather than erroring.

Also shown: uncommitted work is invisible to other sessions (isolation) — the `[]` before
`rollback()` was read by a second session while the first still held the row in its
transaction.

**Where this lands in the architecture:** `get_db` owns the session's *lifetime*; the
service layer owns *transaction boundaries* and calls `commit()`. Relevant to Step 47, where
checkout must write an order, its items and a stock decrement as one unit.

---

### ✅ Step 9 — Configure Alembic

**Completed:** 2026-10-21 · Alembic 1.20.0

`uv run alembic init alembic` generated `alembic.ini`, `alembic/env.py`,
`alembic/script.py.mako` and `alembic/versions/`. Three edits were made to the generated
files; everything else was left as produced.

| Edit | Why |
|---|---|
| `alembic.ini`: removed `sqlalchemy.url = driver://user:pass@...` | `alembic.ini` **is committed to git**. A URL here would commit the database password. |
| `alembic/env.py`: URL read from `get_settings().database_url` | One source of credentials — the same `.env` the app and Compose already use. |
| `alembic/env.py`: `target_metadata = Base.metadata` | Lets `--autogenerate` compare the models against the live database. Without it autogenerate produces empty migrations. |

Also enabled `file_template` in `alembic.ini` so migration files are named
`2026_10_21_1430-ab12cd34_create_products.py` and the `versions/` folder reads in date order
instead of by random revision id.

`run_migrations_online()` was simplified to use `create_engine(...)` directly rather than
`engine_from_config(...)`, since the URL no longer comes from the ini file. It uses
`NullPool` — a migration command is short-lived, so connection pooling gains nothing.

#### Verification

| Check | Result |
|---|---|
| `uv run alembic current` | `Context impl PostgresqlImpl` — connected successfully |
| `uv run alembic heads` | Empty — no migrations exist yet, as expected |
| `public` tables | None — `alembic_version` is created on the first `upgrade` |
| Password present in `alembic.ini` or `env.py` | **No** — searched explicitly |
| `ruff check` | Clean (one import-order fix applied) |

#### Risk & Controls Note

The one control that matters here: **no database credential in a committed file**. Alembic's
generated `alembic.ini` ships a `sqlalchemy.url` placeholder that invites exactly that
mistake; it was removed and the URL moved into `env.py`, which reads the git-ignored `.env`.
Verified by searching both committed files for the password. Offline mode
(`alembic upgrade --sql`) is available for environments where a DBA reviews SQL before it
runs — relevant to Step 70. **Residual risk: Low.**

---

### ✅ Step 10 — First Model and Migration

**Completed:** 2026-10-21

#### What was built

`app/modules/categories/models.py` — a deliberately small first model: `id`, `name`
(`VARCHAR(100)`, unique), `created_at` (`timestamptz`, `server_default=now()`).

**Category rather than Product**, because Product needs prices, SKUs and several constraints
that Step 12 designs properly. Category is the simplest real table in the system, is needed
regardless (Step 20), and keeps this step about migration mechanics rather than schema design.

| File | |
|---|---|
| `app/modules/__init__.py`, `app/modules/categories/__init__.py` | new |
| `app/modules/categories/models.py` | new — the `Category` model |
| `alembic/env.py` | imports `Category` so autogenerate can see it |
| `alembic/versions/2026_10_21_1438-050533dc4a24_create_categories_table.py` | generated |

#### The naming convention paid off

The generated migration contains explicit constraint names rather than PostgreSQL's invented
ones:

```python
sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
sa.UniqueConstraint('name', name=op.f('uq_categories_name'))
```

This is why `downgrade()` is reliable, and why the convention had to be set in Step 7 before
any model existed.

#### Verification

| Check | Result |
|---|---|
| `alembic revision --autogenerate` | `Detected added table 'categories'` |
| Generated migration reviewed before running | Correct — named constraints, matching types |
| `alembic upgrade head` | Applied |
| `\d categories` | `pk_categories` PRIMARY KEY, `uq_categories_name` UNIQUE, `created_at` default `now()` |
| INSERT `'Books'` | `1\|Books\|2026-10-21 09:38:32.68561+00` — server filled `created_at` |
| INSERT `'Books'` again | **Rejected**: `duplicate key value violates unique constraint "uq_categories_name"` |
| `alembic current` | `050533dc4a24 (head)` |
| `alembic downgrade -1` | Table dropped; only `alembic_version` remained |
| `alembic upgrade head` again | Table recreated; `count = 0` — downgrade took the data with it |
| `ruff check app` | Clean |

#### Points recorded

1. **A model Alembic never imports does not exist to it.** `env.py` must import every model
   module or autogenerate silently emits an empty migration. The most common Alembic mistake.
2. **Generated migrations are a draft.** Alembic itself writes `please adjust!` in the output.
   Read every one before running it.
3. **`downgrade()` destroys data.** Dropping the table took the `Books` row with it. Fine in
   development; in production a downgrade is a data-loss event, which is why Step 70 covers
   backup-before-migrate.

#### Risk & Controls Note

- **Data:** synthetic test row only, removed by the downgrade test.
- **Controls:** the unique constraint is enforced **by the database**, not only by application
  code — the integrity safeguard that still holds when a bug, a background job or a manual
  query bypasses the service layer. `created_at` uses `timestamptz` with a server default, so
  the timestamp comes from the database clock rather than an application server's, which
  matters for audit trails across regions.
- **Deferred:** backup-before-migrate and a forward-only migration policy for production
  (Step 70); `id` is a sequential integer — fine internally, but predictable if ever exposed
  in a public URL, reviewed at Step 65.
- **Residual risk: Low.**

---

### ✅ Step 11 — Why `create_all()` Must Not Replace Migrations

**Completed:** 2026-10-21 · Explanation step — **no code added**. Phase 2 complete.

Demonstrated with throwaway in-memory SQLite (nothing real touched): a table was created
with two columns, a third column was added to the model, and `create_all()` was called again.

```
after first create_all() : ['id', 'name']
after second create_all(): ['id', 'name']
```

**`create_all()` creates missing tables. It never alters an existing one — and it reports no
error when it skips.** The application then fails at runtime with
`column "price" does not exist`, far from the cause.

What it cannot do at all: rename a column without data loss, add a `NOT NULL` column with a
backfill, change a type with a `USING` clause, add a constraint after cleaning violating
rows, or reverse any of it. Every one of those is ordinary production work.

It also has no record of what has been applied — no `alembic_version` equivalent — so there
is no way to tell which environment is at which schema, and no rollback path.

**This is the SQLAlchemy equivalent of `synchronize: false` in NestJS/TypeORM.** The project
uses Alembic exclusively; `create_all()` appears nowhere in the codebase and should not be
added, including "just for tests" — a test suite that builds its schema differently from
production stops testing production's schema.

Deferred: backup-before-migrate and forward-only production policy (Step 70).

---

### ✅ Step 12 — Product Table Design

**Completed:** 2026-10-21 · Phase 3 begins.

`app/modules/products/models.py`:

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` PK | |
| `sku` | `VARCHAR(50)` unique | Unique also creates an index, so lookups by SKU are fast |
| `name` | `VARCHAR(200)` | |
| `description` | `TEXT` nullable | `str \| None` makes it nullable |
| `price` | `NUMERIC(12,2)` | **Never `Float`** — see below |
| `is_active` | `BOOLEAN` default `true` | Hide a product without deleting it, so past orders stay meaningful |
| `created_at` / `updated_at` | `TIMESTAMPTZ` default `now()` | `updated_at` also uses `onupdate` |

**Money uses `Numeric`, not `Float`.** Demonstrated: `0.1 + 0.2` is `0.30000000000000004` in
floating point but exactly `0.3` as `Decimal`. Those errors compound across order totals,
tax and refunds, and produce reconciliation failures that are very hard to trace. SQLAlchemy
returns `Numeric` columns to Python as `Decimal`.

**Database-level constraints** (verified present on the model):

```
ck_products_price_not_negative     CheckConstraint
pk_products                        PrimaryKeyConstraint
uq_products_sku                    UniqueConstraint
```

The check constraint means PostgreSQL refuses a negative price even if application code
somehow permits one — a safety net beneath the service layer, consistent with the Step 10
decision to enforce integrity in the database as well as in code.

**Deliberately excluded for now:** `category_id` (Step 21 adds the relationship via its own
migration), stock quantity (Phase 6 — inventory is its own concern with its own concurrency
rules), and currency (single-currency for now; multi-currency would need an explicit
currency column beside every monetary amount).

**Tooling change:** `extend-exclude = ["alembic/versions"]` added to the Ruff config.
Generated migration files are a historical record and should not be reformatted; Ruff was
otherwise flagging Alembic's own generated style.

**Migration:** generated and applied by the user, not by the assistant (see
[[user-runs-db-commands]] working agreement).

#### Risk & Controls Note

- **Data:** no data; schema definition only.
- **Controls:** exact decimal arithmetic for monetary values — a correctness and audit
  requirement for financial records, not a preference; a database-level check constraint on
  price; unique SKU enforced by the database; `is_active` enables soft withdrawal so order
  history remains intact rather than being destroyed by a delete; `timestamptz` from the
  database clock for audit trails.
- **Deferred:** currency handling if the shop ever becomes multi-currency; `id` is a
  sequential integer and predictable if exposed publicly (Step 65); price-change history is
  not retained — order items will snapshot the price at purchase time (Step 46).
- **Residual risk: Low.**

---

### ✅ Step 13 — Product Pydantic Schemas

**Completed:** 2026-10-21

`app/modules/products/schemas.py` — three schemas, kept separate from the ORM model because
the database row and the API contract change for different reasons.

| Schema | Purpose |
|---|---|
| `ProductCreate` | POST body. All required fields present, validated. |
| `ProductUpdate` | PATCH body. Every field optional. **`sku` deliberately absent** — it identifies the product for the business, so changing it would silently break invoices, reports and integrations. |
| `ProductRead` | Response. `ConfigDict(from_attributes=True)` lets Pydantic build it straight from a SQLAlchemy object. |

#### Verification (read-only, no database)

| Input | Result |
|---|---|
| Valid product | accepted |
| `price = -1` | rejected — `Input should be greater than or equal to 0` |
| `price = 9.999` | rejected — `Decimal input should have no more than 2 decimal places` |
| `sku = ""` | rejected — `String should have at least 1 character` |
| `name` over 200 chars | rejected — `String should have at most 200 characters` |
| `price` missing | rejected — `Field required` |
| Parsed price type | `Decimal`, value `29.99` — not float |
| `ProductUpdate(price=...)` with `exclude_unset=True` | `{'price': Decimal('19.99')}` only |
| `ProductRead.model_validate(orm_object)` | `{"id":1,"sku":"BOOK-001",...,"price":"29.99",...}` |

Note `price` serialises to JSON as the **string** `"29.99"`, not a number. That is correct
and deliberate: JSON numbers are IEEE floats, so emitting `29.99` as a number would reintroduce
the precision problem at the API boundary. Clients should parse it as a decimal type.

#### Two layers of validation, on purpose

`decimal_places=2` and `ge=0` in the schema give the client a clear 422 at the API boundary.
The `ck_products_price_not_negative` check constraint from Step 12 remains as the last line of
defence for anything that reaches the database another way. Neither replaces the other.

#### Risk & Controls Note

- **Controls:** input validated at the API boundary before it reaches business logic or the
  database — bounded string lengths prevent oversized payloads being stored, and
  `decimal_places=2` prevents silent rounding of monetary values. `ProductRead` is an
  allow-list: only the fields named there are ever serialised, so a column added to the model
  later cannot leak into a response by accident. That same mechanism protects the password
  hash at Step 25.
- **Deferred:** rejecting unknown fields in request bodies (`extra="forbid"`) — worth a
  decision at Step 65; authorisation, so that only administrators may create or update
  products (Step 30).
- **Residual risk: Low.**

---

### ✅ Step 14 — Product Repository

**Completed:** 2026-10-21

`app/modules/products/repository.py` — plain functions, each taking the `Session` as its
first argument.

| Function | |
|---|---|
| `get_by_id` | `db.get()` — primary-key lookup, checks the session before querying |
| `get_by_sku` | `select().where()` |
| `list_products` | `limit`/`offset` always applied |
| `add` | `db.add()` + `db.flush()` to obtain the generated id |
| `remove` | `db.delete()` |

#### Decisions

**Functions, not a class.** There is no state to hold between calls, so a class with
`__init__(self, db)` would add instantiation boilerplate and nothing else.

**No `update()` function.** SQLAlchemy tracks changes to an object loaded in a session, so
the service assigns new values and the UPDATE is emitted on the next flush. Verified: setting
`created.name` and calling `flush()` produced the new value with no repository call.

**`flush()`, never `commit()`.** The repository stages work; the service decides whether the
whole unit of work succeeds. This keeps the Step 7 split intact — `get_db` owns the session's
lifetime, the service owns the transaction.

**`limit`/`offset` from the start**, defaulting to 20. An unbounded query works on ten rows
and takes the server down on ten million. Step 18 adds filtering, sorting and search on top.

#### Verification — run against the real database, then rolled back

| Check | Result |
|---|---|
| `add()` then `flush()` | id `1` assigned by PostgreSQL; `created_at` set by the server |
| `get_by_id(1)` / `get_by_sku('BOOK-001')` | both returned `Clean Code` |
| `get_by_id(99999)` / `get_by_sku('NOPE')` | both `None` — no exception |
| Assign `name` + `flush()` | `Clean Code (2nd ed)` — dirty tracking confirmed |
| `list_products(limit=2, offset=0)` | `['BOOK-001', 'BOOK-002']` |
| `list_products(limit=2, offset=2)` | `['BOOK-003']` |
| `ProductRead.model_validate(model)` | correct JSON, price as `"29.99"` |
| `remove()` + `flush()` | `get_by_id` returned `None` |
| **After `rollback()`** | **0 products — database unchanged** |

The final line matters: the whole exercise ran inside one transaction and was rolled back,
which is the same mechanism that will make checkout atomic in Step 47.

#### Risk & Controls Note

- **Data:** synthetic rows only, never committed.
- **Controls:** every query is built with SQLAlchemy's `select()` and bound parameters, so
  values are sent to PostgreSQL separately from the SQL text — no string interpolation
  anywhere, closing the injection path by construction. `list_products` always applies a
  limit, preventing an unbounded result set being used as a denial-of-service vector or
  exhausting memory. Returning `None` rather than raising for a missing row keeps "not
  found" a normal outcome for the service to handle, rather than an exception that could
  surface internals to a client.
- **Deferred:** filtering, sorting and search (Step 18); keyset pagination if `offset` on
  large tables becomes slow (Step 64); soft-delete policy — `remove()` currently deletes the
  row, which Step 51 should revisit once orders reference products.
- **Residual risk: Low.**

---

### ✅ Step 15 — Product Service and Business Rules

**Completed:** 2026-10-21

Two new files.

`app/core/exceptions.py` — `AppError` base with `NotFoundError` and `AlreadyExistsError`.
Services raise these; the router maps them to status codes, so business rules never need to
know what a 404 is. Step 59 moves that mapping into one place.

`app/modules/products/service.py` — `get_product`, `list_products`, `create_product`,
`update_product`, `delete_product`. **The service is the only layer that calls `commit()`**,
completing the split established in Step 7: `get_db` owns the session's lifetime, the
repository stages work, the service decides when a unit of work is finished.

#### Key decision: no check-then-insert for SKU uniqueness

The obvious implementation asks "does this SKU exist?" then inserts. That leaves a gap
between the check and the insert, and two requests arriving together can both pass it. The
service instead attempts the insert and converts `IntegrityError` into
`AlreadyExistsError`:

```python
try:
    repo.add(db, product)
    db.commit()
except IntegrityError as exc:
    db.rollback()
    raise AlreadyExistsError(f"SKU {data.sku} is already in use") from exc
```

Shorter than the check-first version *and* race-free, because the unique constraint cannot
be raced. The `rollback()` is required: a failed statement leaves the session unusable until
the transaction is cleared. Verified — `get_product` worked immediately after the failed
insert.

Noted limitation: this assumes any `IntegrityError` on `products` is a SKU conflict, which
holds while `uq_products_sku` is the only unique constraint on the table. Revisit when a
second one is added.

#### Verification — ran against the real database, committing

| Check | Result |
|---|---|
| `create_product` | `id=4 sku=SVC-001 price=29.99` |
| Duplicate SKU | `AlreadyExistsError: SKU SVC-001 is already in use` |
| Session usable after the failed insert | `get_product` returned `Clean Code` |
| `get_product(999999)` | `NotFoundError: Product 999999 does not exist` |
| Partial update `{price}` only | price `29.99 → 24.99`; name, description, is_active **unchanged** |
| `update_product(999999, ...)` | `NotFoundError` |
| Read from a **second session** | `24.99` — the commit was real, not session-local |
| `delete_product` | gone |
| Cleanup | 0 products left |

The second-session read matters: it proves `commit()` made the change visible outside the
session, rather than it merely looking right inside one.

#### Risk & Controls Note

- **Data:** synthetic rows, created and deleted within the check.
- **Controls:** uniqueness enforced by the database constraint rather than an application
  check, removing a time-of-check/time-of-use race — the same class of flaw that causes
  double-spend and duplicate-order defects, so the pattern matters well beyond SKUs.
  `exclude_unset` prevents a partial update silently nulling fields the client never sent, a
  common cause of unintended data loss. Application errors carry no internal detail —
  messages name the resource and id only, no SQL, driver or schema information. `rollback()`
  on failure prevents a broken transaction holding locks.
- **Deferred:** authorisation, so only administrators may create, update or delete products
  (Step 30); mapping `AppError` subclasses to HTTP status codes centrally (Step 59);
  distinguishing which unique constraint an `IntegrityError` came from, once products has
  more than one.
- **Residual risk: Low.**

---

### ✅ Step 16 — Product Routes and Dependency Injection

**Completed:** 2026-10-22 · Read endpoints only; writes follow in Step 17.

| File | |
|---|---|
| `app/modules/products/router.py` | **new** — `GET /products`, `GET /products/{id}` |
| `app/api/router.py` | **new** — aggregates module routers |
| `app/main.py` | mounts `api_router` under `settings.api_v1_prefix` |

#### Decisions

**An aggregate router in `app/api/router.py`.** `main.py` mounts it once, so adding a module
later is one line there rather than another change to the application entry point.

**The version prefix is applied at mount time**, not written into each module's router. The
module declares `prefix="/products"`; `main.py` supplies `/api/v1`. A v2 becomes a mounting
change, not an edit to every router.

**Health probes stay at the root**, outside the version prefix — infrastructure should not
need reconfiguring when the API version changes.

**`db: DbSession` as the only dependency so far.** The `Annotated[Session, Depends(get_db)]`
alias from Step 7 keeps the signature readable. FastAPI opens the session, passes it in, and
closes it when the response is sent.

**Errors are mapped in the route for now.** `NotFoundError` → 404 via `HTTPException`. Step
59 replaces this with one handler for every endpoint; until then the mapping is explicit and
visible.

#### Verification — live server

| Request | Response |
|---|---|
| Routes in the OpenAPI document | `/health`, `/health/ready`, `/api/v1/products`, `/api/v1/products/{product_id}` |
| `GET /api/v1/products` | `[]` · **200** |
| `GET /api/v1/products/999` | `{"detail":"Product 999 does not exist"}` · **404** |
| `GET /api/v1/products/abc` | `int_parsing` error · **422** |
| `GET /api/v1/products?limit=500` | `Input should be less than or equal to 100` · **422** |

The last two never reached application code — FastAPI rejected them from the type annotation
and the `Query` bounds alone.

#### Tooling

Ruff began reformatting Python samples inside `PROJECT_PLAN.md`; `*.md` added to
`extend-exclude` alongside `alembic/versions`.

#### Risk & Controls Note

- **Controls:** `limit` is bounded at 100 by `Query(le=100)`, so a client cannot request an
  unbounded result set — rejected at the boundary with a 422 before any query runs, which
  matters as a denial-of-service control once the table is large. Path and query parameters
  are type-validated before application code executes. The 404 body carries only the
  resource and id, with no SQL, driver or schema detail. `ProductRead` continues to act as
  an allow-list on the response.
- **Open gap:** these endpoints are **unauthenticated**. Acceptable for read-only product
  data, but `POST`/`PATCH`/`DELETE` in Step 17 must not ship without the admin-only
  authorisation from Step 30. Recorded so it is not forgotten.
- **Deferred:** rate limiting (Step 63), centralised error handling (Step 59), pagination
  metadata and filtering (Step 18).
- **Residual risk: Low** for reads; **Medium** once writes exist without authorisation.

---

### ✅ Step 17 — Create, Update and Delete Endpoints

**Completed:** 2026-10-22 · Product CRUD complete.

| Endpoint | Status | Notes |
|---|---|---|
| `GET /products` | 200 | |
| `GET /products/{id}` | 200 / 404 | |
| `POST /products` | **201** | `status_code` set explicitly; FastAPI defaults to 200 |
| `PATCH /products/{id}` | 200 / 404 | PATCH, not PUT — partial update |
| `DELETE /products/{id}` | **204** / 404 | No body on success |

#### Status code decisions

- **201 Created** for POST. The default 200 would be wrong for a request that creates a
  resource.
- **409 Conflict**, not 400, for a duplicate SKU. The request is well formed; it clashes with
  existing state. 400 would tell the client to fix its syntax, which is misleading.
- **PATCH, not PUT.** The client sends only the fields it wants to change. PUT means "replace
  the whole product with this", which would require every field on every edit.
- **204 No Content** for DELETE. It worked, and there is nothing to return.

#### Verification — live server, full cycle

| Request | Response |
|---|---|
| `POST` valid product | `{"id":6,...,"price":"29.99"}` · **201** |
| `POST` same SKU again | `{"detail":"SKU API-001 is already in use"}` · **409** |
| `POST` price `-5.00` | `greater_than_equal` error · **422** — never reached the service |
| `GET` list | the created product · 200 |
| `PATCH` price only | price `29.99 → 24.99`, other fields unchanged · 200 |
| `PATCH` missing id | `{"detail":"Product 999 does not exist"}` · 404 |
| `DELETE` | empty body · **204** |
| `GET` after delete | 404 |
| `DELETE` again | 404 — not an error, it is simply gone |
| Final list | `[]` · 200 — nothing left behind |

**`updated_at` moved on the PATCH** (`07:42:27 → 07:42:49`) while `created_at` stayed put,
confirming the `onupdate=func.now()` from Step 12 works through the whole stack.

#### Observation for Step 59

Every write endpoint now repeats the same `try/except … raise HTTPException` block. Five
endpoints, four of those blocks. This is exactly the duplication centralised exception
handling removes, and it is the concrete problem that justifies Step 59 rather than adding
the abstraction speculatively.

#### Risk & Controls Note

- **Data:** synthetic product, created and deleted within the check; table left empty.
- **Controls:** a negative price was rejected with a 422 **before reaching the service**,
  demonstrating the layered defence — schema validation at the boundary, business rules in
  the service, check constraint in the database. Duplicate SKU returns a clean 409 rather
  than a 500, because the service converts `IntegrityError` rather than letting it escape.
  Error bodies carry only the resource and id.
- **Open gap, now material:** `POST`, `PATCH` and `DELETE` are **unauthenticated**. Anyone
  who can reach the service can create, alter or delete products, including changing prices.
  Acceptable only because the application is bound to loopback on a development machine.
  **These endpoints must not reach any shared or deployed environment before Step 30 adds
  admin-only authorisation.**
- **Deferred:** authorisation (Step 30); audit logging of who changed a price and when
  (Step 60) — price changes are exactly the kind of event that needs an audit trail in a
  regulated context; rate limiting (Step 63); centralised error handling (Step 59).
- **Residual risk: Medium** — unauthenticated write access to product and pricing data,
  mitigated for now only by local-only network exposure.

---

### ✅ Step 18 — Pagination, Filtering, Sorting and Search

**Completed:** 2026-10-22

`GET /api/v1/products` now accepts `limit`, `offset`, `search`, `is_active`, `min_price`,
`max_price`, `sort` and `order`, and returns a `ProductPage` envelope rather than a bare list.

#### Decisions

**A response envelope, not a bare list.** `{items, total, limit, offset}` — a bare list
cannot say how many results exist, so a client cannot render "page 2 of 7" or know when to
stop.

**Sortable columns come from a dict, never from the request.** A column name cannot be a
bound parameter, so interpolating one from user input would be a genuine injection hole.
`SORTABLE_COLUMNS` maps the four permitted names to columns, and `Literal[...]` on the query
parameter means FastAPI rejects anything else with a 422 before the lookup is reached.

**Filters are returned as a list of conditions, not a finished query.** `_filters()` is used
by both the page query and the count query, so the two cannot drift apart and report a total
that does not match the page.

**`id` is added as a secondary sort key.** Without a tiebreaker, rows with equal prices can
swap positions between pages, so a product appears twice or is skipped entirely.

**`Annotated[...]` form for query parameters** rather than `= Query(...)` defaults. It is the
current FastAPI style and avoids Ruff's B008 (a function call in an argument default).

**A concrete `ProductPage`, not a generic `Page[T]`.** There is one list endpoint. When
categories gets one, the duplication will be real and generalising will be justified.

#### Verification — live server, 5 seeded products

| Request | Result |
|---|---|
| `limit=2&offset=0` / `2` / `4` | 2, 2 then 1 item; `total=5` throughout |
| `search=mug` | 2 — matched **name** (`Coffee Mug`, `Travel Mug`) |
| `search=BK` | 3 — matched **SKU** |
| `search=clean` | 1 — case-insensitive (`Clean Code`) |
| `min_price=30` | 2 (`45.50`, `39.00`) |
| `max_price=20` | 2 (`8.75`, `15.00`) |
| `min_price=20&max_price=40` | 2 (`29.99`, `39.00`) |
| `sort=price&order=asc` | `8.75, 15.00, 29.99, 39.00, 45.50` |
| `sort=price&order=desc` | exact reverse |
| `search=mug&max_price=10&sort=price` | 1 — filters combine |
| `sort=password` | **422** — `Input should be 'id', 'name', 'price' or 'created_at'` |
| `sort=id;DROP TABLE products` | **422** — same |
| `min_price=-5` | **422** |
| `search=' ; DROP TABLE products;--` | **200**, `total=0` — treated as literal text |

All seeded products deleted afterwards; table left empty.

#### Risk & Controls Note

- **Data:** synthetic products, created and removed within the check.
- **Controls — injection surface closed two ways.** Values travel as bound parameters, so
  `search=' ; DROP TABLE products;--` was matched as literal text and returned an empty
  result rather than executing. Column names, which *cannot* be bound parameters and are the
  usual injection route in sort features, come from a server-side allow-list and are
  additionally rejected at the boundary by `Literal`. `limit` stays capped at 100 and
  `search` at 100 characters, bounding both result size and pattern cost.
- **Known limitation:** `%` and `_` in `search` are LIKE wildcards and are not escaped, so a
  user can broaden their own search. Not an injection or disclosure issue — the result set is
  the same public product list either way — but worth escaping when search is revisited at
  Step 64.
- **Performance note for Step 64:** `search` uses a leading-wildcard `ILIKE`, which cannot
  use a normal B-tree index and will scan the table as it grows. `OFFSET` also gets more
  expensive on deep pages. Both are fine at current scale; a trigram index and keyset
  pagination are the answers.
- **Still open:** write endpoints remain unauthenticated (Step 30).
- **Residual risk: Low** for the read path; **Medium** overall, unchanged, because of
  unauthenticated writes.

---

### ✅ Step 19 — Full Request Lifecycle

**Completed:** 2026-10-22 · Explanation step — **no code added**. **Phase 3 complete.**

Traced `GET /api/v1/products?search=traced&max_price=10&sort=price` against a live server
with `APP_DB_ECHO=true`.

**Response:** one item (`TRACE-2`, `7.50`), `total=1`, `limit=20`, `offset=0`.

**SQL actually emitted:**

```
BEGIN (implicit)

SELECT products.id, products.sku, ... FROM products
WHERE (products.name ILIKE %(name_1)s::VARCHAR OR products.sku ILIKE %(sku_1)s::VARCHAR)
  AND products.price <= %(price_1)s
ORDER BY products.price ASC, products.id
LIMIT %(param_1)s::INTEGER OFFSET %(param_2)s::INTEGER
[generated in 0.00033s] {'name_1': '%traced%', 'sku_1': '%traced%',
                         'price_1': Decimal('10'), 'param_1': 20, 'param_2': 0}

SELECT count(*) AS count_1 FROM products
WHERE (products.name ILIKE %(name_1)s::VARCHAR OR products.sku ILIKE %(sku_1)s::VARCHAR)
  AND products.price <= %(price_1)s

ROLLBACK
```

#### What the trace confirms

1. **Parameters are bound, not interpolated.** The SQL text contains `%(name_1)s`
   placeholders and the values arrive as a separate dict. This is the injection control from
   Step 18, visible in the wire protocol rather than asserted.
2. **Only the requested filters appear.** `is_active` and `min_price` were not sent, so no
   condition for them was generated — `_filters()` builds conditions only for values that
   are present.
3. **Both queries share the same WHERE clause**, so `total` describes exactly the set the
   page came from.
4. **`ORDER BY products.price ASC, products.id`** — the secondary sort key is present, which
   is what keeps paging stable when prices tie.
5. **A read runs inside a transaction too.** PostgreSQL opens one implicitly; `BEGIN` appears
   even though nothing is written.
6. **`ROLLBACK`, not `COMMIT`.** The GET never called `commit()`, so `get_db`'s
   `db.close()` rolled the (empty) read transaction back. Correct and harmless — and the
   same mechanism that discards partial work when a write fails.

#### The path a request takes

```
Uvicorn parses HTTP
  -> FastAPI matches the route and validates query parameters (422 if invalid)
  -> get_db opens a Session           [app/db/session.py]
  -> router reads the request         [products/router.py]
  -> service orchestrates             [products/service.py]
  -> repository builds the query      [products/repository.py]
  -> SQLAlchemy emits parameterised SQL
  -> PostgreSQL executes
  -> ProductRead filters the response fields
  -> ProductPage wraps items + total
  -> get_db closes the session (rollback on an uncommitted read)
```

Validation never reaches application code: `sort=password` and `min_price=-5` are rejected by
FastAPI from the `Literal` and `ge=0` annotations before the router body runs.

#### Risk & Controls Note

Explanation step; no code or configuration changed. Two trace products were created and
deleted, leaving the table empty. The trace provides **evidence** for a control previously
only asserted: query values travel to PostgreSQL as bound parameters, separate from the SQL
text. Worth noting for Step 60: `APP_DB_ECHO=true` printed the bound parameter values in
plain text — harmless here, but once the database holds customer and payment data this
output would be sensitive, which is why the Step 7 validator blocks it in production.
**Residual risk: Low.**

---

### ✅ Step 20 — Categories Module

**Completed:** 2026-10-22 · Phase 4 begins.

The same five layers as products, built against the `Category` model from Step 10. No
migration needed — the table already exists.

| File | |
|---|---|
| `app/common/__init__.py`, `app/common/schemas.py` | **new** — shared `Page[T]` |
| `app/modules/categories/schemas.py` | **new** |
| `app/modules/categories/repository.py` | **new** |
| `app/modules/categories/service.py` | **new** |
| `app/modules/categories/router.py` | **new** — 5 endpoints |
| `app/api/router.py` | includes the categories router |
| `app/modules/products/{schemas,router}.py` | `ProductPage` replaced by `Page[ProductRead]` |

#### The generic page envelope, now earned

Step 18 deliberately used a concrete `ProductPage` and recorded that generalising would be
justified once a second list endpoint existed. It now does, so the duplication was removed
rather than copied:

```python
class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
```

Used as `Page[ProductRead]` and `Page[CategoryRead]`. This uses Python 3.12's inline type
parameter syntax, so no `TypeVar` declaration is needed.

#### Differences from products, and why

- **No price filters or sort options.** Categories have a name and a date; sorting is fixed
  to name then id. Adding filters nothing asks for would be speculative.
- **`update_category` also catches `IntegrityError`.** Renaming a category can collide with
  an existing name, whereas products cannot change their SKU — so products only needed the
  guard on create.

#### Verification — live server

| Request | Result |
|---|---|
| Routes registered | products and categories, both under `/api/v1` |
| `POST` Books / Mugs / Electronics | 201 each |
| `POST` Books again | **409** `Category Books already exists` |
| `GET` list | 3 items, `total=3`, ordered by name |
| `GET ?search=mug` | `total=1` `[Mugs]` |
| `PATCH` id 2 → `Drinkware` | 200 |
| `PATCH` id 2 → `Books` (taken) | **409** |
| `GET` id 999 | **404** |
| `DELETE` id 3 | **204** |
| `GET /products` after the `Page` refactor | unchanged envelope — regression check passed |

Test products deleted. **Two categories left in place (`Books`, `Drinkware`) as seed data for
Step 21.**

#### Risk & Controls Note

- **Data:** synthetic categories only; no personal or financial data.
- **Controls:** same as products — bound parameters throughout, `limit` capped at 100,
  `search` capped at 100 characters, uniqueness enforced by the database constraint rather
  than a check-then-insert, and `CategoryRead` acting as a response allow-list.
- **Open gap, unchanged:** category write endpoints are **unauthenticated**, like products'.
  Both must be behind admin-only authorisation (Step 30) before any shared environment.
- **Noted for Step 21:** deleting a category currently removes the row outright. Once
  products reference categories, the foreign key needs an explicit `ON DELETE` behaviour —
  otherwise a delete either fails or silently orphans products.
- **Residual risk: Medium**, unchanged — unauthenticated writes, mitigated only by
  loopback-only exposure.

---

### ✅ Step 21 — Product–Category Relationship

**Completed:** 2026-10-22 · Migration generated and applied by the user.

`products.category_id` references `categories.id`. One category per product; a product may
have none.

#### The ON DELETE decision

What happens when someone deletes a category that products still use? Three options, only
one acceptable:

| Option | Effect | Verdict |
|---|---|---|
| `CASCADE` | Deleting a category **deletes its products** | Never. Silent, large data loss from a small action. |
| `SET NULL` | Products quietly become uncategorised | Safe but silent — the change is invisible until someone notices. |
| **`RESTRICT`** | PostgreSQL refuses the delete | **Chosen.** Fails loudly; someone must deliberately move or uncategorise the products first. |

`delete_category` converts the resulting `IntegrityError` into `InUseError`, which the
router returns as **409** with a message naming the reason.

#### Other decisions

- **Nullable `category_id`.** A product can exist before anyone decides where it belongs,
  and requiring it would have meant backfilling if rows already existed.
- **`index=True` on the foreign key.** PostgreSQL does *not* index foreign keys
  automatically, and "products in this category" filters on it constantly.
- **The service checks the category exists** before insert, producing a clear 404. The
  foreign key would also reject it, but a raw constraint violation tells a client nothing.
- **`TYPE_CHECKING` imports** on both models. Each refers to the other, so real imports
  would be circular; SQLAlchemy resolves `"Category"` and `"Product"` by name at mapper
  configuration time.
- **`InUseError` added** to `app/core/exceptions.py`, mapping to 409 like
  `AlreadyExistsError` — the request is valid, it conflicts with current data.
- **`category_id` filter** added to the product list endpoint, threaded through router,
  service and repository.

#### Bug found by testing: the ORM bypassed the constraint

The first implementation looked correct and was not. `DELETE /categories/{id}` on a category
with products returned **204** — the category was deleted and the product's `category_id`
became `NULL`.

PostgreSQL was configured correctly (`confdeltype = 'r'`). The ORM was the problem: on
`db.delete(category)`, SQLAlchemy's default behaviour is to **load the related products and
set their foreign key to NULL before issuing the DELETE**, so the database never saw a
violation. The result was exactly the silent `SET NULL` behaviour that was rejected above,
produced by the ORM rather than the schema.

Fixed with `passive_deletes="all"` on `Category.products`, which tells SQLAlchemy to leave
the children untouched and let the database decide.

**Lesson recorded:** a correct schema does not guarantee correct behaviour. The constraint
has to be tested through the application, not confirmed in `psql`. Verifying
`confdeltype = 'r'` alone would have passed this step with the protection disabled.

#### Verification — after the fix

| Check | Result |
|---|---|
| `Product.category` / foreign key | resolves to `Category`, `ForeignKey('categories.id')` |
| `POST` product with valid `category_id` | **201**, `category_id` set |
| `POST` product with `category_id=9999` | **404** `Category 9999 does not exist` |
| `GET /products?category_id=2` | `total=1` |
| Migration contents | `nullable=True`, `ix_products_category_id`, `ondelete='RESTRICT'` |
| **`DELETE` a category with products** | **409** `Category 2 still has products and cannot be deleted` |
| Category after the failed delete | still exists |
| Product after the failed delete | still linked, `category_id=2` |

#### Risk & Controls Note

- **Controls:** `RESTRICT` is a data-integrity control chosen deliberately over the
  convenient options — referential actions that silently delete or null out rows are a
  recognised cause of unexplained data loss, and in a regulated context an unexplained
  change to records is worse than a failed request. The service's existence check means a
  bad `category_id` produces a 404 rather than leaking a constraint-violation message.
- **Deferred:** `ON DELETE` behaviour will need revisiting at Step 45 when order items
  reference products — order history must survive a product being withdrawn, which is why
  `is_active` exists and why deleting products outright becomes questionable then.
- **Unchanged:** write endpoints remain unauthenticated until Step 30.
- **Residual risk: Medium**, unchanged.

---

### ✅ Step 22 — Relationship Loading and N+1

**Completed:** 2026-10-22 · Explanation step — **no production code changed**.

Measured with a `before_cursor_execute` event listener counting real queries, inside a
transaction that was rolled back. Five products, **each in its own category**.

| Approach | Queries |
|---|---|
| Load 5 products | 1 |
| …then read `p.category.name` on each (**default, lazy**) | **6** |
| `selectinload(Product.category)` | **2** |
| `joinedload(Product.category)` | **1** |

The first run of this demo put all five products in **one** category and showed only 2
queries, because SQLAlchemy found the already-loaded category in the session's identity map.
That is genuinely useful behaviour, and it also means **a careless N+1 test can pass**.
Distinct related rows are required to see the real cost.

#### What each does

- **Lazy (default).** The relationship is a placeholder; touching `p.category` fires a query
  right then. Fine for one object, quadratic-feeling for a list: 100 products become 101
  queries.
- **`selectinload`.** Loads the parents, then issues one `SELECT ... WHERE id IN (...)` for
  all related rows. Always 2 queries regardless of page size. The right default.
- **`joinedload`.** One query with a `LEFT OUTER JOIN`. Best for many-to-one; for
  one-to-many it multiplies rows (10 products × 5 items each = 50 rows to deduplicate) and
  interacts badly with `LIMIT`.

#### Guidance recorded for this project

Use `selectinload` for collections and for any list endpoint. Use `joinedload` for a
single many-to-one on a single object. Never rely on lazy loading inside a loop.

Also relevant: `expire_on_commit=False` (Step 7) means attributes stay readable after
commit. Without it, serialising a response after commit would trigger a refresh query per
object — an N+1 that appears only in production under load.

#### Not changed

`ProductRead` still returns `category_id` only, so the API currently issues no extra
queries. When a nested category object is added to the response, the list endpoint **must**
add `selectinload(Product.category)` in the same change, or it becomes an N+1 the moment it
ships.

#### Risk & Controls Note

No code or data changed; demo rows rolled back, verified 0 left. N+1 is an availability
concern rather than a confidentiality one: a list endpoint issuing one query per row turns a
normal request into a database load amplifier, which is a cheap denial-of-service lever when
the endpoint is unauthenticated — as the product list currently is. The `limit` cap of 100
bounds the damage to 101 queries per request rather than unbounded. Re-check at Step 64
alongside index and connection-pool review. **Residual risk: Low** at current scale.

---

### ✅ Step 23 — Constraints and Indexes

**Completed:** 2026-10-25 · **Phase 4 complete.** Migration to be run by the user.

#### What already existed

| Index | Source |
|---|---|
| `pk_categories`, `pk_products` | primary keys |
| `uq_categories_name`, `uq_products_sku` | unique constraints |
| `ix_products_category_id` | added explicitly in Step 21 |

Every index so far came free from a constraint, except the foreign-key index — PostgreSQL
does not create those automatically. Nothing was missing for *performance* at this scale,
so no speculative indexes were added.

#### The gap: uniqueness was case-sensitive

Demonstrated against the live API, not assumed:

```
POST /categories {"name":"DRINKWARE"} -> 201
POST /categories {"name":"drinkware"} -> 201
list -> Drinkware, DRINKWARE, drinkware

POST /products {"sku":"rel-1"} -> 201   (REL-1 already existed)
```

Three categories that are the same word, and two SKUs that are the same code. `unique=True`
compares byte for byte, so these are distinct rows to PostgreSQL and duplicates to every
human and every downstream system.

#### The fix

`unique=True` replaced with a **unique index on the lowercased column** on both tables:

```python
Index("uq_categories_lower_name", func.lower(name), unique=True)
Index("uq_products_lower_sku", func.lower(sku), unique=True)
```

Explicit names, because the naming convention cannot build one for an index on an
expression rather than a plain column.

`get_by_sku` and `get_by_name` were changed to compare with `func.lower(...)` as well. Had
they stayed case-sensitive, a lookup would report "not found" for a value the database
considers taken — the lookup and the constraint must agree, and using `func.lower` on the
column lets the new index serve the query.

#### Risk & Controls Note

- **Controls:** uniqueness that matches human meaning rather than byte equality. Duplicate
  SKUs are a data-integrity problem with real downstream effects — two rows for one product
  split stock, split reporting and make reconciliation ambiguous. Enforced in the database,
  so it holds for imports, scripts and manual queries, not only the API.
- **Operational note for Step 70:** this migration **adds a unique constraint to an existing
  table**. If duplicates exist, the migration fails and the deployment stops. That is the
  correct behaviour, and it is also why such a change needs the data checked first. The
  duplicates created during the demonstration were removed before the model change.
- **Deferred to Step 64:** trigram index for `search` (leading-wildcard `ILIKE` cannot use a
  B-tree); indexes for sorting by `name`, `price` or `created_at` once query patterns are
  known from real use rather than guessed.
- **Residual risk: Low.**

---

### ✅ Step 24 — User Model

**Completed:** 2026-10-25 · Phase 5 begins. Migration run by the user.

`app/modules/users/models.py`:

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` PK | |
| `email` | `VARCHAR(320)` | 320 is the maximum length an email address can be |
| `password_hash` | `VARCHAR(255)` | The Argon2 hash. **Never** a plaintext password |
| `is_active` | `BOOLEAN` default `true` | Disable an account without deleting it, so past orders stay meaningful |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | |

Index: `uq_users_lower_email`, unique on `lower(email)`.

#### Decisions

**Case-insensitive email**, using the same pattern established in Step 23. Nobody expects
`Rashid@x.com` and `rashid@x.com` to be separate accounts, and permitting both invites
sign-in confusion and impersonation through a lookalike address.

**The column is named `password_hash`, not `password`.** The name states what is stored. A
column called `password` invites someone to put a password in it.

**No `role` column yet.** Step 30 adds roles with its own migration. Keeping each step to
one change also exercises normal schema evolution.

**No relationship to orders or addresses yet** — those tables do not exist until Phases 8
and 9.

#### Verified before the migration

Six columns with correct types and nullability, and one unique index on `lower(email)`.

#### Risk & Controls Note

- **This is the first table holding personal data.** An email address is personal data under
  PDPL and the UAE/Bahrain equivalents, so from here the standing commitments apply in
  practice rather than in principle: synthetic addresses only in development, and no real
  customer data copied into this environment.
- **Controls in place by design:** the password hash column is isolated and will never
  appear in a response schema — `UserRead` in Step 25 simply will not list it, which is the
  allow-list behaviour already proven on `ProductRead`. `is_active` allows deactivation
  instead of deletion, preserving the audit trail that order history depends on. Email
  uniqueness is enforced by the database, case-insensitively, so duplicate accounts cannot
  be created by an import or a script that bypasses the API.
- **Required next, not optional:** Step 25 must hash with Argon2 before any user row is
  written. No endpoint accepts a user until then.
- **Deferred and tracked:** password reset tokens and their expiry; account lockout after
  repeated failures (Step 63 rate limiting); audit logging of authentication events
  (Step 60) — in a regulated context, failed sign-ins are a required trail; encryption at
  rest for the database volume (Phase 12); a retention and deletion policy for user records,
  which PDPL requires and which Step 74 should cover.
- **Residual risk: Low** today, since the table is empty and no endpoint writes to it.

---

### ✅ Step 25 — Registration and Password Hashing

**Completed:** 2026-10-25

`POST /api/v1/users` registers an account. Dependencies added: `pwdlib[argon2]` 0.3.1 and
`pydantic[email]` (brings `email-validator` 2.3.0).

| File | |
|---|---|
| `app/core/security.py` | **new** — `hash_password`, `verify_password` |
| `app/modules/users/{schemas,repository,service,router}.py` | **new** |
| `app/api/router.py` | includes the users router |

#### Decisions

**Argon2id via `PasswordHash.recommended()`.** Argon2 won the Password Hashing Competition
and is deliberately slow and memory-hard, so guessing passwords from a stolen database is
expensive. A general-purpose hash such as SHA-256 is far too fast to be safe here.

**`max_length=128` on the password, not only `min_length`.** Argon2 cost rises with input
size, so without a cap a very large password body is a cheap way to burn server CPU.

**`EmailStr`** rejects malformed addresses before any code runs.

**Uniqueness by `IntegrityError`, not check-then-insert** — consistent with products and
categories, and race-free.

**`UserRead` does not list `password_hash`.** That absence *is* the control. The field sits
next to the others on the model and cannot reach a response because it was never named.

#### Verification

| Check | Result |
|---|---|
| `POST` valid registration | `{"id":1,"email":"test.user@example.com","is_active":true,...}` · **201** |
| Response contains `password_hash` | **No** — four fields only |
| Same email, different case | **409** — case-insensitive index works |
| `email: "not-an-email"` | **422** before any code ran |
| 5-character password | **422** |
| **Stored value** | `$argon2id$v=19$m=65536,t=3,p=4$NxbXA1dJ...` |
| Plaintext present in the row | **0 rows match** — not stored anywhere |
| Same password hashed twice | **Different hashes** — each is independently salted |
| Both verify correctly | `True True` |
| Wrong password | `False` |

The stored string carries the algorithm (`argon2id`), version, and cost parameters
(`m=65536,t=3,p=4`) alongside the salt and digest. That is what makes cost settings
upgradable later without invalidating existing hashes.

#### Known trade-off, accepted deliberately

Returning **409** on a duplicate email **confirms that an address is registered**, which
allows user enumeration — someone can test whether a given person has an account here. The
privacy-preserving alternative is to always return 201 and send a message to the address
instead, which needs email delivery this project does not yet have.

Accepted for now and recorded. Partial mitigation is rate limiting at Step 63. Revisit at
Step 65 — under PDPL, confirming that a named individual holds an account is itself a
disclosure of personal data.

#### Risk & Controls Note

- **Data:** one synthetic account (`test.user@example.com`). No real personal data.
- **Controls implemented and tested:** Argon2id hashing with per-password salts, proven by
  two identical passwords producing different hashes; plaintext confirmed absent from
  storage; constant-time verification via the library, so timing does not reveal how much of
  a password was correct; the plaintext exists only inside `register_user` and is never
  logged; response allow-list proven to exclude the hash; bounded password length to limit
  CPU cost.
- **Open:** user enumeration via the 409, as above. No password-strength rule beyond length
  — a deliberate choice, since length matters far more than composition rules, but a
  breached-password check (for example a k-anonymity lookup) would be the stronger control
  and is worth considering at Step 65.
- **Deferred:** rate limiting and lockout (Step 63); authentication event logging (Step 60);
  password reset; retention and deletion policy (Step 74).
- **Residual risk: Low–Medium** — the hashing is sound; enumeration is the open item.

---

## 7. Standing Security & Compliance Commitments

These apply to every step and are re-verified at Steps 61, 65 and 74.

1. **No real secrets in the repository.** `.env` is local-only and git-ignored; only
   `.env.example` with placeholder values is tracked. Production secrets live in a managed
   secret store, never in environment files baked into images.
2. **Synthetic data only.** All seeded products, users, addresses and orders are generated.
   No production-derived customer, payment or identity data enters this project at any stage.
3. **Sensitive by default.** Financial, customer, identity and access data are treated as
   highly sensitive: hashed credentials (Argon2), least-privilege database roles, no internal
   exception detail in API responses, no sensitive values in logs or URLs.
4. **No plaintext passwords, ever.** Hashing only; no reversible storage.
5. **Payments stay in sandbox.** No real payment credentials; no payment is treated as
   complete without provider confirmation via a signature-validated webhook.
6. **Migration-controlled schema.** Production schema changes go through Alembic only.
7. **Repository visibility** must be confirmed (and branch protection enabled) before
   Step 71 pushes anything to GitHub.
8. **Auditability.** Every step records its decisions, verification evidence and residual
   risk in this file.

---

## 8. How This File Is Maintained

At the end of each completed step:

1. Flip the step's row in section 5 from 🔵 to ✅ and mark the next step 🔵.
2. Update the counters and *Current step* in section 1.
3. Tick the relevant entries in section 4.
4. Append a full entry to section 6 — objective, decisions, deviations, files, rationale,
   verification evidence, Risk & Controls Note, and what was deferred.
5. Add any new dependency to the section 2 table with the step that introduced it.
