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
| **Current step** | **Step 47 — Checkout and order creation** (Steps 1–46 complete) |
| **Phases complete** | 8 of 12 |
| **Steps complete** | 46 of 74 |

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
| 26 | Login | ✅ |
| 27 | Generate and validate JWT access tokens | ✅ |
| 28 | Current-user retrieval via FastAPI dependencies | ✅ |
| 29 | Protect endpoints with authentication | ✅ |
| 30 | Roles and permissions (customer / administrator) | ✅ |
| 31 | Explain token expiration, password security, authN vs authZ, JWT mistakes | ✅ |

### Phase 6 — Inventory

| # | Step | Status |
|---|---|---|
| 32 | Inventory and stock quantities | ✅ |
| 33 | Stock adjustment and availability rules | ✅ |
| 34 | Prevent negative inventory, handle concurrent stock changes | ✅ |
| 35 | Explain transactions, row locking / conditional updates, race conditions | ✅ |

### Phase 7 — Shopping Cart

| # | Step | Status |
|---|---|---|
| 36 | Cart and cart-item models | ✅ |
| 37 | Cart retrieval and item management endpoints | ✅ |
| 38 | Quantity changes and item removal | ✅ |
| 39 | Price and availability handling in a cart | ✅ |
| 40 | When to calculate prices and validate inventory (never trust client prices) | ✅ |

### Phase 8 — Addresses and Checkout Preparation

| # | Step | Status |
|---|---|---|
| 41 | Customer addresses | ✅ |
| 42 | Associate addresses with users | ✅ |
| 43 | Shipping and checkout data contracts | ✅ |
| 44 | Order creation design with transaction boundaries | ✅ |

### Phase 9 — Orders and Checkout

| # | Step | Status |
|---|---|---|
| 45 | Order and order-item models | ✅ |
| 46 | Immutable order-item snapshots (name, SKU, quantity, unit price) | ✅ |
| 47 | Checkout and order creation | 🔵 |
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

### ✅ Step 26 — Login

**Completed:** 2026-10-27

`POST /api/v1/auth/login` verifies credentials. The response is a `UserRead` for now;
Step 27 replaces it with an access token, keeping this step to one idea — verifying a
password safely.

| File | |
|---|---|
| `app/core/exceptions.py` | `AuthenticationError` added (→ 401) |
| `app/modules/users/service.py` | `authenticate_user` |
| `app/modules/users/schemas.py` | `LoginRequest` |
| `app/modules/users/auth_router.py` | **new** — `POST /auth/login` |

#### Decisions

**One message for every failure.** Unknown email, wrong password and disabled account all
raise `AuthenticationError("Incorrect email or password")`. Distinguishing them would confirm
which addresses have accounts — the same enumeration problem as the registration 409, in a
more sensitive place.

**No length rules on `LoginRequest.password`.** Rejecting a short attempt with 422 instead
of 401 would leak that the real password is longer than that.

**A dummy hash for the unknown-email path.** Argon2 is deliberately slow (~68 ms here). If
an unknown email returned without hashing, it would answer in ~1 ms and the response time
alone would reveal which addresses are registered. `authenticate_user` verifies against
`_DUMMY_HASH` before failing, so both paths do the same work.

**A separate `auth_router`**, because signing in is an action on credentials rather than
creating or reading a user resource.

#### Verification

| Request | Result |
|---|---|
| Correct credentials | `{"id":1,"email":"test.user@example.com",...}` · **200** |
| Right email, wrong password | `{"detail":"Incorrect email or password"}` · **401** |
| Unknown email | **identical** body and status · **401** |
| Email in different case | **200** — case-insensitive lookup matches the index |

**Timing, 15 interleaved samples each after warm-up:**

| Path | Median |
|---|---|
| Existing email, wrong password | 67.6 ms |
| Unknown email | 68.4 ms |
| **Difference** | **0.7 ms** |

A first attempt measured 68.7 ms vs 94.5 ms and looked like a leak. That run tested the two
groups sequentially with no warm-up, so the second absorbed start-up costs. Interleaving and
discarding warm-up requests removed the artefact. **Worth recording as method:** a timing
measurement without interleaving and warm-up produces confident nonsense in either
direction.

#### Risk & Controls Note

- **Data:** one synthetic account.
- **Controls implemented and tested:** uniform failure response across all three causes,
  verified byte-identical; uniform response *time*, verified to 0.7 ms; constant-time hash
  comparison from the library; disabled accounts rejected without being distinguishable.
  Together these close the credential-side enumeration channel — though the registration
  409 from Step 25 still leaks the same information by a different route, so the pair should
  be resolved together at Step 65.
- **Open and material:** there is **no rate limiting**, so this endpoint currently permits
  unlimited password guessing. Argon2's ~68 ms cost is a weak throttle, not a control. This
  must be closed before any shared environment — Step 63, and worth pulling earlier.
  Account lockout or progressive delay should be considered alongside it.
- **Deferred:** authentication event logging, successes and failures with source IP
  (Step 60) — required as an audit trail in a regulated context; refresh tokens and session
  revocation (Step 27+); MFA, not currently in the roadmap but expected for administrative
  accounts in this sector.
- **Residual risk: Medium** — the verification logic is sound; unlimited guessing is not.

---

### ✅ Step 27 — JWT Access Tokens

**Completed:** 2026-10-28 · PyJWT 2.15.1.

`POST /auth/login` now returns `{access_token, token_type}`. Token creation and validation
live in `app/core/security.py`; three settings were added.

| Setting | |
|---|---|
| `APP_JWT_SECRET` | `SecretStr`, **no default** |
| `APP_JWT_ALGORITHM` | `HS256` |
| `APP_JWT_EXPIRE_MINUTES` | 30, bounded 1–1440 |

#### Decisions

**No default for the secret**, for the same reason as the database password. Anyone holding
it can mint a token for any account, so a default is a key an attacker already has, and
defaults get deployed. A 56-character random value was generated for `.env`;
`.env.example` carries `CHANGE_ME` and a generator command.

**The payload carries only `sub`, `iat` and `exp`.** A JWT is **signed, not encrypted** —
the payload is base64, readable by anyone holding the token. No email, no name, nothing
private.

**`algorithms=[...]` is a list we choose**, never the `alg` named inside the token. Trusting
the token's own header is the classic JWT flaw: an attacker sets `alg` to `none` and the
signature stops being checked.

**30-minute expiry.** A stolen token works until it expires and nothing here can revoke one
early — that is what refresh tokens and a revocation list would add.

**Every decode failure raises one `AuthenticationError`**, so a client cannot learn whether
a token was expired, forged, or malformed.

#### Verification

| Check | Result |
|---|---|
| Login | `token_type: bearer`, `eyJhbGciOiJIUzI1NiIs...` |
| Wrong password | still **401**, no token |
| **Payload read without the secret** | `{'sub': '1', 'iat': ..., 'exp': ...}` — readable, as expected |
| Valid token decodes | `1` |
| Signature altered | rejected |
| `sub` changed to `999`, old signature | rejected |
| **`alg=none` unsigned token** | **rejected** |
| Expired token | rejected |
| Token signed with a different secret | rejected |
| `create_access_token(42)` → decode | `42` |

The forged-subject case is the one that matters: changing `sub` from `1` to `999` is
trivial, and the signature is the only reason it fails.

#### Risk & Controls Note

- **Controls implemented and tested:** signing secret held as `SecretStr` with no default
  and excluded from serialisation, like the database password; a fixed server-side algorithm
  list, with `alg=none` proven rejected; expiry enforced and bounded; no personal data in
  the payload, which matters because the token is readable by anyone who obtains it and may
  sit in browser storage or proxy logs; uniform decode failure.
- **Accepted limitations, recorded:** tokens **cannot be revoked** before expiry — sign-out
  is client-side only, and a disabled account keeps working until its token lapses. For
  administrative accounts in this sector that gap needs closing, via short expiry plus a
  revocation check or server-side sessions. No refresh token, so users re-authenticate every
  30 minutes.
- **Open and material, unchanged:** no rate limiting on login (Step 63), so tokens can be
  pursued by unlimited password guessing.
- **Deferred:** key rotation procedure (Step 74) — HS256 with a single shared secret means
  rotating it invalidates every live token, which needs a planned overlap; authentication
  event logging (Step 60).
- **Residual risk: Medium** — token handling is correct; revocation and rate limiting are
  the open items.

---

### ✅ Step 28 — Current-User Dependency

**Completed:** 2026-10-28

`app/modules/users/dependencies.py` turns `Authorization: Bearer <token>` into a `User`.
Any module needing a signed-in user imports `CurrentUser` from there. `GET /users/me` added
to demonstrate it.

```python
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.get("/me")
def read_me(user: CurrentUser) -> UserRead:
    return user
```

#### Decisions

**`HTTPBearer(auto_error=False)`.** With `auto_error=True`, a missing header produces
FastAPI's built-in **403**, and "you did not sign in" is a **401**. Handling it ourselves
also keeps the message uniform.

**One message for every cause.** Missing header, malformed token, expired token, wrong
scheme, deleted or disabled account all return `401 {"detail":"Not authenticated"}`. A
caller should not be able to tell an expired token from a disabled account.

**`WWW-Authenticate: Bearer` on every 401**, which is what the HTTP spec requires of a 401
and tells a client which scheme to retry with.

**The user is looked up on every request**, rather than trusting the token alone. This is
the important one: the token proves *who signed in*, the database decides *whether that
account may still act*.

#### The revocation gap, partly closed

Step 27 recorded that tokens cannot be revoked. The database lookup narrows that
considerably — demonstrated end to end:

| Step | Result |
|---|---|
| `GET /users/me` with a valid token | **200** |
| `UPDATE users SET is_active = false WHERE id = 1` | `UPDATE 1` |
| **The same token, immediately after** | **401** |
| Signing in again | **401**, generic message |
| Re-enabled, same token | **200** again |

So disabling an account takes effect on the **next request**, not when the token expires.
What remains unrevocable is a token for an account that is still active — logging out
elsewhere, or invalidating one device, would still need a token blacklist or server-side
sessions.

#### Verification

| Request | Result |
|---|---|
| Valid token | `{"id":1,...}` · **200** |
| No `Authorization` header | `Not authenticated` · **401** |
| `Bearer not-a-real-token` | identical · **401** |
| `Basic <valid token>` | identical · **401** — wrong scheme, not accepted |
| 401 headers | `www-authenticate: Bearer` present |

#### Risk & Controls Note

- **Controls implemented and tested:** per-request authorisation check against the database,
  giving near-immediate effect to account deactivation — the practical answer to the
  stateless-token revocation problem at this scale, and an important one in a regulated
  context where disabling access must be prompt; uniform 401 across all causes; correct
  status code and `WWW-Authenticate` header; the bearer scheme enforced rather than any
  credential being accepted.
- **Cost accepted:** one extra database query per authenticated request. Correct trade —
  the query is a primary-key lookup, and the alternative is accepting requests from accounts
  that have been disabled.
- **Still open:** individual token revocation while an account stays active; no rate
  limiting (Step 63); no authentication event logging (Step 60).
- **Residual risk: Medium**, unchanged — the remaining items are rate limiting and
  fine-grained revocation. Note that product and category writes are **still unauthenticated**
  until Step 29 applies this dependency to them.

---

### ✅ Step 29 — Protect the Write Endpoints

**Completed:** 2026-10-28 · **Closes the gap open since Step 17.**

Write endpoints on products and categories now require a signed-in user. Reads stay public,
because a shop catalogue is public.

```python
requires_auth = [Depends(get_current_user)]

@router.post("", status_code=201, dependencies=requires_auth)
```

`dependencies=[...]` rather than a `user: CurrentUser` parameter: the endpoint needs the
request to be authenticated but does not use *who* it was, so an unused parameter would be
noise. The dependency still runs and still rejects.

#### Authorisation map, read from the generated OpenAPI document

| Endpoint | |
|---|---|
| `GET /products`, `/products/{id}` | public |
| `POST`, `PATCH`, `DELETE /products` | **AUTH** |
| `GET /categories`, `/categories/{id}` | public |
| `POST`, `PATCH`, `DELETE /categories` | **AUTH** |
| `GET /users/me` | **AUTH** |
| `POST /users` (register), `POST /auth/login` | public — necessarily |
| `/health`, `/health/ready` | public |

Reading it from the OpenAPI document rather than from the source is deliberate: it reflects
what the running application actually enforces, so an endpoint accidentally left open shows
up in the list.

#### Verification

| Request | Result |
|---|---|
| `GET /products`, `/products/16`, `/categories` without a token | **200** — still public |
| `POST /products` without a token | **401** |
| `PATCH /products/16` without a token | **401** |
| `DELETE /products/16` without a token | **401** |
| `POST /categories` without a token | **401** |
| `DELETE /categories/2` without a token | **401** |
| `POST /products` **with** a valid token | **201** |
| `POST /categories` **with** a valid token | **201** |

Test rows removed afterwards.

#### Risk & Controls Note

- **The material gap recorded at Steps 16, 17, 20 and 21 is now closed.** Product and
  category data, including prices, can no longer be created, altered or deleted by an
  unauthenticated caller.
- **Residual risk drops from Medium to Low–Medium**, and the remaining concern changes
  character: writes are now limited to *authenticated* users, but **any** registered user can
  still change prices and delete products, because registration is open and there are no
  roles yet. That is a privilege problem, not an authentication one, and **Step 30 is
  required before this is deployable**.
- **Controls:** fail-closed by default — the dependency rejects before the handler runs, so
  a bug in the handler cannot expose the operation; authorisation state verified from the
  running application's OpenAPI document rather than from source.
- **Deferred, unchanged:** rate limiting (Step 63); authentication and write-event audit
  logging (Step 60) — once roles exist, "who changed this price" becomes a question the logs
  must answer.

---

### ✅ Step 30 — Roles and Permissions

**Completed:** 2026-10-28 · Migration run by the user.

`users.role` holds `customer` or `admin`. Product and category writes now require `admin`,
not merely a signed-in user.

#### The rule that matters

**A role a client can choose is not a role.** `UserCreate` has exactly two fields — verified:

```
UserCreate fields: ['email', 'password']
UserRead fields  : ['id', 'email', 'is_active', 'role', 'created_at']
```

There is no `role` field on the request schema to attack. `register_user` sets
`role=ROLE_CUSTOMER` in code. Had the role been read from the request body, anyone could
register as an administrator — a complete privilege escalation from an unauthenticated
request, and a common real-world defect.

`role` is readable on `UserRead` so a client knows what it may do, and settable nowhere.

#### 401 versus 403

| Code | Meaning | Retry? |
|---|---|---|
| **401** | I do not know who you are | Sign in and try again |
| **403** | I know who you are, and you still may not | Pointless with the same account |

`require_admin` returns **403**. Returning 401 would tell an administrator to sign in again
when they already had.

#### Other decisions

**A `String(20)` with a check constraint, not a PostgreSQL `ENUM` type.** Adding a third
role later is then an ordinary constraint change rather than `ALTER TYPE`, which is awkward
inside a transaction. The constraint means a typo in a manual `UPDATE` cannot leave an
account in a state the code does not understand.

**`server_default="customer"`**, so existing rows get the least-privileged value when the
migration runs. Defaulting to `admin` would have promoted every existing account.

**No API to change a role.** Promotion is a deliberate database action by an administrator.
An endpoint for it would need careful authorisation of its own and is not needed yet.

#### Defect found: autogenerate silently dropped the check constraint

The generated migration contained only `op.add_column`. **Alembic's autogenerate compares
tables, columns, indexes and foreign keys, but not `CheckConstraint`s** — a documented
limitation, not a bug. The model declared the constraint, the migration omitted it with no
warning, and the database accepted `role='superuser'`.

Caught by attempting an invalid write rather than by reading the model. Same lesson as
Step 21 in a different disguise: a correct model does not mean a correct database.

Fixed with a hand-written migration `b7c41d9e2a38`, which repairs any offending row **before**
adding the constraint — adding a constraint to data that violates it simply fails.

**Rule recorded:** when a model gains a `CheckConstraint`, check the generated migration for
it and add it by hand if absent. Same list as expression indexes.

#### Verification — after the fix

| Check | Result |
|---|---|
| `ck_users_role_is_known` present | yes |
| `UPDATE users SET role='superuser'` | **rejected** by the constraint |
| New registration's role | `customer` |
| Promoted account's role | `admin` |
| **Customer token** on `POST`/`PATCH`/`DELETE /products`, `POST /categories` | **403** on all four |
| Customer token on `GET /products`, `GET /users/me` | **200** |
| **Admin token** on `POST /products`, `POST /categories` | **201** |
| **No token** on `POST /products` | **401**, not 403 — the distinction holds |

#### Risk & Controls Note

- **This closes the privilege gap left open by Step 29.** Writes are no longer available to
  any registered user; open registration no longer grants catalogue write access.
- **Controls:** role settable only server-side, verified by the absence of the field on the
  request schema rather than by validation that could be bypassed; least-privilege default
  on both new and existing rows; database-level constraint on permitted values; correct
  status-code semantics.
- **Operational note:** the first administrator must be created with a direct `UPDATE`.
  That is appropriate — bootstrapping an administrator through an API is how bootstrap
  endpoints get left enabled in production.
- **Deferred:** audit logging of role changes and of catalogue writes (Step 60) — in a
  regulated context, who promoted an account and who changed a price are both questions the
  logs must answer; MFA for administrative accounts, expected in this sector and not
  currently in the roadmap; rate limiting (Step 63).
- **Residual risk: Low** for the catalogue; the open items are rate limiting and audit
  logging.

---

### ✅ Step 31 — Authentication Concepts

**Completed:** 2026-10-28 · Explanation step — **no code added**. **Phase 5 complete.**

#### Token expiry, watched in real time

```
token issued, valid for 4 seconds
  t+0s  accepted (user 1)
  t+3s  accepted (user 1)
  t+4s  REJECTED - Invalid or expired token
```

Nothing was revoked and the server did not change its mind. The token stopped being valid at
the time written inside it, which every holder of the token can read. **Expiry is the only
limit a stateless token carries**, which is why 30 minutes rather than 30 days.

#### Authentication versus authorisation

| | Question | Status | Where |
|---|---|---|---|
| **Authentication** | Who are you? | 401 | `get_current_user` |
| **Authorisation** | May you do this? | 403 | `require_admin` |

Verified distinct in Step 30: no token → 401, customer token on a write → 403, admin token →
201. Collapsing the two into one status is common and wrong — it tells a signed-in user to
sign in again.

#### Password security, as built

| Control | Where |
|---|---|
| Argon2id, memory-hard, per-password salt | `app/core/security.py` |
| Plaintext never stored or logged | `register_user` only |
| Constant-time verification | library |
| Length bounded 8–128 | `UserCreate` |
| Hash absent from every response | `UserRead` field list |
| Uniform failure message and timing | `authenticate_user` |

#### JWT mistakes, and which were avoided

| Mistake | Status |
|---|---|
| Trusting the token's own `alg` header (`alg=none`) | **avoided** — `algorithms=[...]` is server-chosen; proven rejected |
| Personal data in the payload | **avoided** — `sub`, `iat`, `exp` only; payload is readable by anyone |
| No expiry, or very long expiry | **avoided** — 30 minutes, bounded 1–1440 |
| Default or weak signing secret | **avoided** — `SecretStr`, no default, 56 random characters |
| Trusting the token alone for authorisation | **avoided** — user re-loaded from the database every request |
| Different errors for different failures | **avoided** — one message everywhere |
| Assuming a token can be revoked | **not avoided — accepted** |

#### Honest gaps at the end of Phase 5

1. **No rate limiting.** Login permits unlimited guessing; Argon2's ~68 ms is a speed bump,
   not a control. Step 63, and worth pulling earlier.
2. **No individual token revocation.** Disabling an *account* takes effect immediately
   (Step 28), but one device cannot be signed out while the account stays active.
3. **No refresh token.** Users re-authenticate every 30 minutes.
4. **No authentication audit log.** Step 60. In a regulated context, failed sign-ins and
   role changes are a required trail.
5. **No MFA for administrators.** Not in the roadmap; expected in this sector.
6. **User enumeration via the registration 409** (Step 25), still open.

#### Risk & Controls Note

No code or data changed. Phase 5 took the catalogue from fully open to admin-only with
sound credential handling. The honest summary: **authentication and authorisation are
correct; the operational controls around them are not yet built.** Items 1 and 4 above are
the ones that would block a production review in this sector, and both have roadmap homes.
**Residual risk: Medium** overall, driven by the absence of rate limiting and audit logging
rather than by any defect in what exists.

---

### ✅ Step 32 — Stock Quantities

**Completed:** 2026-10-28 · Phase 6 begins. Migration run by the user.

`products.stock_quantity`, an integer defaulting to 0, with a check constraint
`stock_quantity >= 0`.

#### Decision: a column on products, not a separate inventory table

There is one warehouse, no stock history to keep and no reservations. A separate table would
add a join on every product read and a second row to lock during checkout, for no benefit
today. **Deviation from the target structure's `modules/inventory/`, recorded deliberately** —
it becomes justified the moment stock needs batches, locations, reservations or an audit
trail of movements, and that is a schema change rather than a rewrite.

#### Decision: `stock_quantity` is NOT on `ProductUpdate`

Verified:

```
Create: [..., 'category_id', 'stock_quantity']
Update: ['name', 'description', 'price', 'is_active', 'category_id']     <- absent
Read  : [..., 'category_id', 'stock_quantity', ...]
```

Stock moves *because something happened* — a delivery arrived, a sale shipped, a count was
corrected. A generic `PATCH {"stock_quantity": 5}` sets an absolute value, which silently
overwrites whatever a concurrent sale just did: read 5, sell 1 elsewhere, write 5, and the
sale has vanished. Explicit adjustment operations (Step 33) can be made atomic and recorded;
an absolute setter cannot.

Settable at creation as opening stock, readable always.

#### Risk & Controls Note

- **Controls:** a database-level floor at zero, which holds even if application arithmetic is
  wrong — Step 34 is about ensuring it never has to. Stock deliberately excluded from the
  generic update path, removing a lost-update race before it can be written.
- **Migration note carried forward from Step 30:** Alembic autogenerate does **not** emit
  `CheckConstraint`s. `ck_products_stock_not_negative` must be added to the migration by
  hand if absent.
- **Deferred:** stock movement history, which is what would answer "why is this figure
  wrong" — worth considering at Step 64 if inventory disputes matter; audit logging of
  adjustments (Step 60).
- **Residual risk: Low** — no concurrency protection yet beyond the constraint, which is
  exactly Step 34's subject.

---

### ✅ Step 33 — Stock Adjustment and Availability Rules

**Completed:** 2026-10-28 · No migration. No new dependency.

An admin endpoint that changes stock by a *difference*, plus the rules and filters that tell
a customer what can actually be bought.

#### Decision: `POST /products/{id}/stock-adjustments`, not `PATCH /products/{id}`

An absolute value (`stock_quantity = 5`) is calculated from a value read earlier, so sending
one overwrites whatever happened in between — the classic lost update:

```
admin reads 5  →  customer buys 1 (stock 4)  →  admin PATCHes 5  →  the sale is gone
```

A difference (`quantity_change = -1`) carries no assumption about the current value, so two
adjustments commute: `+10` then `-3` equals `-3` then `+10`. That property is what lets
Step 34 push the arithmetic into the database as a single statement.

`POST` to a sub-resource reads as *create an adjustment for this product*, which is what is
happening, and leaves the right name in place for when adjustments must be stored and
audited.

#### Decision: `ProductUpdate` now sets `extra="forbid"`

Found during verification, not by design review. Pydantic drops unknown keys by default, so
`PATCH {"stock_quantity": 500}` returned **200 OK** and silently discarded the field — a
client would reasonably believe stock was now 500. It now returns 422 naming the offending
key, which points the caller at the adjustment endpoint.

Applied to `ProductUpdate` only, where there is a concrete field whose silent loss is
dangerous. Not spread across every schema for symmetry.

#### Decision: `is_available` is a `computed_field`, not a column

`is_active and stock_quantity > 0`, derived on every response. Storing it would create a
third value to keep in step with the two it depends on, and it would be stale the moment
either changed.

`@computed_field` appears in `model_dump()`; a plain `@property` does not. That distinction is
load-bearing in both directions — `Settings.database_url` is deliberately a plain property so
the password can never land in a dump.

#### Known gap, deliberately carried into Step 34

`adjust_stock()` reads the quantity, adds to it in Python, and writes the result back. Two
requests arriving together can both read 5 and both write 4, losing one sale. This is
recorded in the function's docstring rather than hidden.

`ck_products_stock_not_negative` still prevents the total going **negative**, so the data
cannot become nonsense — but it can become **wrong**. Step 34 closes this by moving the
arithmetic into the database; Step 35 explains the mechanism.

#### Files changed

| File | Change |
|---|---|
| `app/core/exceptions.py` | `InsufficientStockError` → 409 |
| `app/modules/products/schemas.py` | `StockAdjustment`; `is_available`; `extra="forbid"` on `ProductUpdate` |
| `app/modules/products/repository.py` | `in_stock` condition in `_filters`, threaded through list and count |
| `app/modules/products/service.py` | `adjust_stock()`; `in_stock` passed through `list_products` |
| `app/modules/products/router.py` | `POST /{id}/stock-adjustments`; `?in_stock=` query parameter |

#### Verification

Live requests against a running server, admin and customer tokens.

| Case | Expected | Got |
|---|---|---|
| admin `+10` | 200, stock 10, available true | ✅ |
| admin `-3` | 200, stock 7 | ✅ |
| admin `-99` with 7 in stock | 409, no change | ✅ `Product 16 has 7 in stock, so 99 cannot be removed` |
| admin `0` | 422 | ✅ `quantity_change must not be zero` |
| unknown product | 404 | ✅ |
| customer token | 403 | ✅ `Administrator access required` |
| no token | 401 | ✅ |
| `PATCH {"stock_quantity": 500}` | 422, not silent 200 | ✅ `extra_forbidden` |
| `PATCH {"name": ...}` | 200, still works | ✅ |
| `?in_stock=true` | only the stocked product | ✅ |
| `?in_stock=false` | only the zero-stock product | ✅ |
| no filter | both | ✅ |

The `in_stock` filter was tested against a temporary zero-stock product rather than against a
single-row table, because a filter cannot be shown to discriminate when there is nothing to
discriminate between. The temporary product was deleted afterwards.

Ruff clean across 35 files.

#### Risk & Controls Note

- **Regulatory / data protection:** None. Inventory quantities only; no customer, identity,
  payment or financial-account data is read or written by this endpoint.
- **Security:** Positive on balance. The endpoint is admin-only (403 for customers, 401
  unauthenticated, both proven). `extra="forbid"` removes a silent-failure mode in which a
  client believed a write had succeeded. Error messages disclose the current stock level to an
  authenticated administrator only, which is information they already have by `GET`.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`.
- **Required controls / approvals:** Stock movements are currently **not attributable** — no
  record of who adjusted what, when, or why. Acceptable for a development build; **not
  acceptable for production**, where inventory affects revenue recognition and is auditable.
  Step 60 (audit logging) must cover this endpoint, and the `stock-adjustments` resource name
  was chosen so that storing the adjustments is an additive change.
- **Residual risk:** **Medium**, and deliberately so. Two causes: (1) the read-modify-write
  race described above can under-count stock under concurrency — the integrity floor holds but
  the figure can be wrong, closed in Step 34; (2) no audit trail of adjustments, closed in
  Step 60. Both are recorded in code, not only here.

---

### ✅ Step 34 — Prevent Negative Inventory, Handle Concurrent Stock Changes

**Completed:** 2026-10-29 · No migration. No new dependency.

`adjust_stock()` now locks the product row before reading it, closing the lost-update race
left open in Step 33.

#### The bug, measured before it was fixed

50 concurrent `POST /products/16/stock-adjustments` with `quantity_change: -1`, against the
Step 33 code, over real HTTP:

```
started with      100
sales accepted    50 (of 50 requests)
stock should be   50
stock actually is 75
LOST SALES        25
```

Half the sales vanished. No error was raised anywhere; every request returned 200.

The second test is the one that matters commercially — 10 items on the shelf, 50 buyers:

| | Step 33 (unfixed) | Step 34 (fixed) |
|---|---|---|
| HTTP 200 "sold" | **21** | 10 |
| HTTP 409 refused | 29 | 40 |
| stock at end | 0 | 0 |

**The unfixed code sold 21 items from a shelf of 10.** Eleven customers were told their order
succeeded for goods that do not exist.

`ck_products_stock_not_negative` never fired, because every individual write was non-negative.
Lost updates meant stock fell more slowly than sales occurred. **A check constraint cannot
detect this.** It protects the shape of the data, not the correctness of a sequence of
operations.

#### Why it happens

PostgreSQL's default isolation level is `READ COMMITTED`. It guarantees a transaction never
reads *uncommitted* data. It does **not** guarantee that a value read is still true when it
is written. The gap between `SELECT` and `UPDATE` is where the application does its
arithmetic, and anything may happen in it.

#### Decision: `SELECT ... FOR UPDATE`, not a conditional UPDATE

`repository.get_by_id_for_update()` issues `SELECT ... FOR UPDATE`, verified in the compiled
SQL. A second transaction reaching the same row waits for the first to commit, then reads the
value the first wrote. The lock is per **row**, so a sale of one product never blocks a sale
of another.

The alternative considered was a single conditional statement:

```sql
UPDATE products SET stock_quantity = stock_quantity + :change
WHERE id = :id AND stock_quantity + :change >= 0
```

That is also correct, holds no lock across application code, and is the better choice for a
pure counter. It was **not** chosen because it returns only a row count: distinguishing *"no
such product"* (404) from *"not enough stock"* (409) needs a second query, and the error
message could no longer state how much stock there actually is. The locking read keeps one
clear code path and keeps the useful message. It also extends directly to checkout, where an
order must lock several products at once — which a per-statement conditional update cannot
express.

`db.get()` is deliberately not used for the locking fetch: it can be answered from the session
cache without reaching the database, and a lock must be taken by the database.

#### Decision: explicit `db.rollback()` before raising `InsufficientStockError`

Otherwise the row lock is held until the request finishes and the session closes, needlessly
blocking every other sale of that product. Verified: an adjustment immediately after a run of
409s succeeds rather than hanging.

#### Files changed

| File | Change |
|---|---|
| `app/modules/products/repository.py` | `get_by_id_for_update()` |
| `app/modules/products/service.py` | `adjust_stock()` uses the locking fetch; rollback before 409 |

#### Verification

| Case | Expected | Got |
|---|---|---|
| 50 concurrent sales from 100 | end at 50, none lost | ✅ 50, none lost |
| 50 buyers, 10 in stock | exactly 10 × 200, 40 × 409, end 0 | ✅ |
| same test, unfixed server | demonstrates the bug | ✅ 21 sold from 10 |
| compiled SQL contains `FOR UPDATE` | yes | ✅ |
| admin `+25` / `-5` | 200 | ✅ |
| admin `-999` | 409 | ✅ |
| admin `0` | 422 | ✅ |
| unknown product | 404 | ✅ |
| customer / no token | 403 / 401 | ✅ |
| `PATCH` with `stock_quantity` / `name` | 422 / 200 | ✅ |
| adjustment after a burst of 409s | 200, no hang | ✅ lock released |

Ruff clean. The concurrency tests drive the running server over HTTP and change no application
code; a `threading.Barrier` synchronises the callers, which widens the window rather than
creating it.

#### Risk & Controls Note

- **Regulatory / data protection:** None directly. Indirectly material: overselling creates
  obligations to customers that cannot be met, and inventory figures feed revenue recognition.
  Correctness here is a financial-reporting concern, not only a technical one.
- **Security:** Positive. A lost-update race is exploitable — a buyer who fires concurrent
  requests could previously obtain more units than exist. That is now closed at the data layer
  rather than relying on client behaviour.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`.
- **Required controls / approvals:** Row locks serialise sales **of the same product**. Under
  sustained contention on one popular item, requests queue, and a slow transaction holds its
  lock for its full duration. Two controls are now required before production and are **not yet
  in place**: a statement or lock timeout, so a stuck transaction cannot block a product
  indefinitely; and monitoring of lock waits. Recorded as open items below. Stock movements
  remain unattributable until Step 60.
- **Residual risk:** **Low–Medium.** The correctness defect is closed and demonstrated closed.
  What remains is availability under contention (no lock timeout) and the absence of an audit
  trail, both tracked.

#### Open items added

- No `lock_timeout` / `statement_timeout` configured; a stuck transaction can block sales of
  one product indefinitely. Should be set before Step 71 (deployment).
- No monitoring of lock waits or long-running transactions.

---

### ✅ Step 35 — Transactions, Row Locking, Conditional Updates and Race Conditions

**Completed:** 2026-10-29 · No code change. No migration. Explanation step, with every claim
demonstrated against the real database.

#### 1. A transaction is a boundary, not a keyword

Everything between `BEGIN` and `COMMIT` lands completely or not at all. In this codebase the
boundary is owned by **one layer only**: the service calls `commit()`, the repository never
does, and `get_db()` closes the session afterwards — which rolls back anything uncommitted.

That is why `create_product` calls `db.rollback()` before raising, and why Step 34 added a
rollback before `InsufficientStockError`: leaving a transaction open holds its locks.

#### 2. `READ COMMITTED` promises less than people assume

PostgreSQL's default isolation level. Demonstrated:

```
0.00s  A   UPDATE sent to the database, NOT committed
0.01s  B   sees 100 - not 42. A's change does not exist yet for anyone else
0.01s  A   rolled back; the 42 never existed
```

It guarantees you never read **uncommitted** data. It does **not** guarantee that a value you
read is still true when you write. Every statement sees a fresh snapshot, so two statements in
one transaction can see different worlds. That gap is the whole of Step 34's bug.

#### 3. What `FOR UPDATE` actually does

```
0.01s  A        locked the row, read 100
0.30s  B        asks for the same row ... waiting
1.02s  reader   plain SELECT returned 100 immediately, never blocked
2.02s  A        wrote 99 and committed, lock released
2.02s  B        got the lock, read 99  <- A's value, not the stale 100
```

Three things worth keeping:

- B **waits**, then reads the value A wrote. It does not get a stale copy.
- A plain `SELECT` is **never blocked** by a writer. In PostgreSQL readers and writers do not
  block each other; only `FOR UPDATE` queues behind `FOR UPDATE`.
- The lock lives until commit **or rollback**, not until the end of the statement.

#### 4. Pessimistic versus optimistic versus conditional

| Approach | How | Cost | Suits |
|---|---|---|---|
| Pessimistic (`FOR UPDATE`) | take the lock, then think | holds a lock across application code | several rows at once; needs the current value to decide — **what this project uses** |
| Conditional `UPDATE` | `SET x = x + :d WHERE ... AND x + :d >= 0` | returns only a row count | a single counter |
| Optimistic (`version` column) | write with `WHERE version = :seen`, retry on 0 rows | needs retry logic and a column | long think-time, rare conflicts |

None is more "correct". The project uses the locking read because checkout must hold several
products at once and because the error message needs the current quantity.

#### 5. Deadlock, and the rule that prevents it

Two orders, two products, locks taken in whatever order the cart happened to be in:

```
0.01s  order-1  locked product 32
0.02s  order-2  locked product 33
1.52s  order-1  FAILED - OperationalError      <- PostgreSQL killed one to break the cycle
1.52s  order-2  locked product 32
1.53s  order-2  committed
```

The same two orders, both locking in **id order**:

```
-> 0 transaction(s) killed: none
```

**Rule for Phase 7:** when an operation locks more than one row, sort the ids first and lock in
that order, always. A deadlock is not a database fault; it is two transactions disagreeing
about sequence. PostgreSQL detects the cycle and kills one — correct, but one customer sees a
failure for no reason they could have caused.

#### 6. `lock_timeout` — the control Step 34 recorded as missing

```
0.00s  holder     holds the lock for 3s
0.31s  impatient  lock_timeout = 500ms, asking for the row
0.82s  impatient  gave up after 0.51s with OperationalError
```

Without it a request waits indefinitely for a row another transaction is holding. One stuck
transaction can then block every sale of a popular product, and the waiting requests consume
connections from a finite pool while they wait — so one slow row can exhaust the pool and take
down endpoints that have nothing to do with stock.

Still **not configured**. Carried as an open item to the configuration-hardening step; it is a
connection-level setting, not a code change at the call site.

#### Verification

All four demonstrations were run against the live database and the live schema. Stock was
restored to its prior value afterwards, and the two temporary products created for the
deadlock demonstration were deleted.

#### Risk & Controls Note

- **Regulatory / data protection:** None. No schema, code or data change persists from this
  step; two temporary product rows were created and removed.
- **Security:** Neutral to positive. No new surface. Documents a known availability failure
  mode (unbounded lock waits exhausting the connection pool) and the deadlock-ordering rule
  that prevents spurious transaction failures in checkout.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`.
- **Required controls / approvals:** Unchanged from Step 34. `lock_timeout` and
  `statement_timeout` remain required before production, and lock-wait monitoring remains
  absent. The deadlock-ordering rule must be applied when Phase 7 locks several products in
  one transaction.
- **Residual risk:** **Low.** This step adds no attack surface and changes no behaviour. The
  risks it describes are inherited from Step 34 and already tracked.

---

### ✅ Step 36 — Cart and Cart-Item Models

**Completed:** 2026-10-31 · Phase 7 begins. Migration generated and run by the user.

`app/modules/cart/` with two tables: `carts` (one per user) and `cart_items` (one row per
product per cart). Module named `cart`, singular, following the target structure in section 4
rather than the plural used by `products` and `categories`.

#### Decision: no price column on `cart_items`

The most consequential decision in this step. A cart is working state, not a quote. Copying
the price in when an item is added would show the customer a stale number for as long as the
cart sits there, and would create a second place where prices live — one that silently drifts
from `products`.

The cart reads today's price from `products` on every request. The price is frozen **exactly
once**, when the order is created (Phase 9). The standing rule, carried into Steps 39–40: the
client never sends a price, and the cart never remembers one.

#### Decision: one row per product per cart

`uq_cart_items_cart_id_product_id`. Adding the same product again increases the quantity
rather than creating a second line. Enforced by the database, not by trusting the service to
remember — the same reasoning as the SKU uniqueness index.

#### Decision: `quantity > 0`, not `>= 0`

A line holding zero of something is not a line. Removing an item is a `DELETE`, not an update
to zero. `ck_cart_items_quantity_is_positive`.

#### Decision: three foreign keys, three different delete rules

| Link | Rule | Reasoning |
|---|---|---|
| `carts.user_id` → `users` | `CASCADE` | a cart has no meaning without its owner and no value as a record, so there is nothing to decide |
| `cart_items.cart_id` → `carts` | `CASCADE` | a line has no meaning without its cart |
| `cart_items.product_id` → `products` | `RESTRICT` | deleting a product a customer is about to buy should require a decision; `is_active=false` is how a product is retired |

Orders in Phase 9 are the opposite case and must never cascade: an order is a financial record
and survives the deletion of everything it refers to.

#### Decision: no reverse relationship on `Product`

`CartItem.product` is one-directional. `Category.products` needed `passive_deletes="all"`
because the ORM would otherwise load the children and clear their foreign key before issuing
the `DELETE`, bypassing `ON DELETE RESTRICT` entirely — a bug found by testing the behaviour
in Step 27. With no collection on `Product` to load, there is nothing to bypass.

This is an assumption about ORM behaviour, so it is listed below as something to verify by
attempting the delete, not by reading the model.

#### Indexing

`cart_items` has no standalone index on `cart_id` and does not need one: the unique index on
`(cart_id, product_id)` serves any query filtering on `cart_id`, which is its leftmost column.
`ix_cart_items_product_id` does exist, because PostgreSQL does not index foreign keys
automatically and `ON DELETE RESTRICT` checks it on every product delete.

#### Files added

| File | Purpose |
|---|---|
| `app/modules/cart/__init__.py` | module marker |
| `app/modules/cart/models.py` | `Cart`, `CartItem` |
| `alembic/env.py` | imports `Cart`, `CartItem` so autogenerate sees them |

#### Verification

Compiled DDL inspected before the migration was generated: both tables, the composite unique
index, the FK delete rules and the check constraint all present and correct. Ruff clean.

Migration `f83d74c67aef` reviewed before it was run and needed no hand edit — autogenerate
renders a `CheckConstraint` inside `create_table`, unlike the `add_column` cases in Steps 30
and 32. `alembic check` then reported no difference between the models and the database.
`alembic check` uses the same comparison as autogenerate, so it shares that blind spot and
would not have caught either earlier omission; it is a safety net with a known hole.

Behaviour verified against the migrated database, through the ORM rather than hand-written
SQL where the ORM is what the service will use:

| Case | Result |
|---|---|
| second line for the same `(cart_id, product_id)` | refused, `uq_cart_items_cart_id_product_id` |
| `quantity = 0` | refused, `ck_cart_items_quantity_is_positive` |
| deleting a product that sits in a cart | refused, `fk_cart_items_product_id_products` |
| deleting a cart | its lines are removed |
| deleting a user | their cart is removed |

The third case confirms the assumption recorded above: with no reverse collection on `Product`,
the ORM issues the `DELETE` directly and `ON DELETE RESTRICT` fires, rather than clearing the
children's foreign key first as it did for `Category.products` in Step 27. Verified by
attempting the delete, not by reading the model.

Temporary user, product and cart created for these tests were removed; `carts` and
`cart_items` are empty.

#### Risk & Controls Note

- **Regulatory / data protection:** Low but non-zero. A cart links a **customer identity** to
  purchasing intent, which is personal data under PDPL and the UAE/Bahrain equivalents. It is
  behavioural rather than financial, and carries no payment or identity document data. Carts
  are working state with no record-keeping value, so they are a candidate for a retention
  policy — abandoned carts should not accumulate indefinitely. No retention rule exists yet;
  recorded as an open item.
- **Security:** Neutral at this step — models only, no endpoints. The access-control rule is
  established now and must hold in Step 37: a cart is readable and writable **only by its
  owner**, derived from the authenticated token, never from a cart id or user id in the
  request. A cart id in a path parameter would be an IDOR waiting to happen.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`.
- **Required controls / approvals:** Cart endpoints (Step 37) must scope every query by the
  authenticated user. Retention policy for abandoned carts required before production. The
  no-stored-price rule must survive Steps 39–40.
- **Residual risk:** **Low.** No endpoint is exposed yet and no data is collected. The risk
  arrives with Step 37, where ownership scoping becomes the control that matters.

#### Open items added

- No retention policy for abandoned carts; personal data would accumulate indefinitely.

---

### ✅ Step 37 — Cart Retrieval and Item Management Endpoints

**Completed:** 2026-10-31 · No migration. No new dependency.

`GET /cart` and `POST /cart/items`, plus the schemas, repository and service behind them.
Quantity changes and removal are Step 38.

#### Decision: no cart id in any URL

```
GET  /cart          not  GET  /carts/{cart_id}
POST /cart/items    not  POST /carts/{cart_id}/items
```

The cart is always the caller's own, taken from the authenticated token. The moment a cart id
is a path parameter, a client can type a different number — **IDOR**, one of the most common
real-world API breaches. The bug cannot exist if the identifier is not in the request.

The same reasoning applies inside: lines are addressed by `product_id`, never by
`cart_items.id`. The row id is an internal detail, and a client that never sees it can never
ask for someone else's.

#### Decision: the cart is created lazily, and an empty cart is not a 404

Every signed-in customer conceptually has a cart. It is created on first use rather than at
registration, so customers who never shop leave no row behind. `GET /cart` for a new customer
returns an empty cart with `total` of `0`, which is the true answer.

Two simultaneous first requests both find no cart and both try to create one.
`uq_carts_user_id` lets exactly one win; the loser catches `IntegrityError`, rolls back and
reads the winner's cart. Same pattern as `create_product` — let the constraint decide rather
than checking first, because a check-then-insert can be raced.

#### Decision: totals in, availability out

`unit_price`, `line_total` and `total` are included — a cart endpoint without a total is not a
cart, and the arithmetic is three lines. `Decimal` throughout, summed from `Decimal("0")` so
an empty cart totals a `Decimal` rather than an `int`.

Deliberately **not** included: whether the product is still active, whether its price has
moved since the item was added, whether there is enough stock. Those are decisions about what
to tell the customer, and they are Steps 39 and 40.

#### Two bugs found during verification, both the identity map

Neither was found by review. Both were found by a test asserting on behaviour.

**1. The first add to a new cart returned an empty cart.** The predecessor of `_ensure_cart_id`
created the `Cart` object, so `cart.items` was already a loaded (empty) collection in the
session. Re-querying at the end of `add_item` returned that same object, and SQLAlchemy does
**not** overwrite attributes it already holds — the `selectinload` ran and its result was
discarded. Fixed with `execution_options(populate_existing=True)` on `get_by_user_id`, whose
job is to produce the current truth for a response and which must therefore win over the cache.

**2. The row lock protected nothing.** 20 simultaneous adds of the same product all returned
200 and the quantity reached **4**, losing 16. The cart and its lines were loaded *before*
`lock_cart` ran, so the later `get_item` was answered from that pre-lock copy. **Locking a row
and then trusting a copy read beforehand protects nothing.**

Fixed by restructuring rather than by another flag: `repository.get_cart_id` loads only the id,
the lock is taken, and the line is read for the first time afterwards. The rule is now written
into both functions — *do not read what you are about to lock, before you lock it*.

This is the same hazard noted in the `get_by_id_for_update` docstring in Step 34, which is why
`db.get()` was avoided there. It was avoided in one place and walked into in two others.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/cart/schemas.py` | `CartItemAdd`, `CartItemRead`, `CartRead`, `MAX_QUANTITY` |
| `app/modules/cart/repository.py` | `get_by_user_id`, `get_cart_id`, `lock_cart`, `get_item`, `add` |
| `app/modules/cart/service.py` | `_ensure_cart_id`, `get_cart`, `add_item` |
| `app/modules/cart/router.py` | `GET /cart`, `POST /cart/items`, `_to_read` |
| `app/modules/cart/models.py` | `order_by` on `Cart.items` so lines have a stable order |
| `app/core/exceptions.py` | `ValidationError` → 422 for a broken business rule |
| `app/api/router.py` | registers the cart router |

#### Verification

20 of 20 functional assertions, over HTTP, against a running server:

| Group | Cases |
|---|---|
| access control | `GET` and `POST` with no token → 401 |
| retrieval | new customer gets an empty cart, total `0` |
| adding | 2 then 3 of the same product → **one** line, quantity 5; a second product → 2 lines; total `78.00` = 5×12.00 + 4×4.50; `total_items` 9 |
| rejections | unknown product 404; quantity 0 and 1000 → 422; unknown field → 422; exceeding the 999 cap → 422 |
| ownership | admin's cart is separate and empty; adding to it leaves the shopper's cart and total untouched |

Plus two measured properties:

- **Query count:** reading a cart of 5 lines costs **3 queries**, not 11. `selectinload` issues
  one extra `SELECT` per relationship regardless of row count.
- **Concurrency:** 20 simultaneous adds of the same product → 20 × 200, **one** line,
  quantity **20**. Nothing lost, no duplicate line, no 500.

Ruff clean. All test data — temporary products and every cart — was removed afterwards and the
removal confirmed by count: `carts` 0, `cart_items` 0, `products` 1, `users` 2.

#### Risk & Controls Note

- **Regulatory / data protection:** A cart links a **customer identity** to purchasing intent,
  which is personal data under PDPL and the UAE/Bahrain equivalents. No payment or identity
  document data is involved. Carts remain working state with **no retention policy**, so
  abandoned carts would accumulate indefinitely — still an open item.
- **Security:** This is the step where cart access control exists, and it is structural rather
  than procedural: no cart id or user id is accepted from the request, so there is no parameter
  to tamper with. Ownership isolation was proven by driving two authenticated users against
  each other's carts. Unknown request fields are rejected rather than ignored. `MAX_QUANTITY`
  bounds a single line so repeated adds cannot overflow a PostgreSQL integer.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`. All
  test data synthetic.
- **Required controls / approvals:** Cart mutations are not rate limited, so a customer can
  issue unbounded adds against their own cart — bounded in effect by `MAX_QUANTITY` but not in
  request volume. Folds into the rate-limiting work at Step 63. Retention policy for abandoned
  carts still required before production. Steps 39–40 must preserve the no-stored-price rule.
- **Residual risk:** **Low.** Access control is structural and proven, the concurrency defect
  found here is closed and demonstrated closed, and no financial or payment data is handled.

---

### ✅ Step 38 — Quantity Changes and Item Removal

**Completed:** 2026-10-31 · No migration. No new dependency.

`PUT /cart/items/{product_id}`, `DELETE /cart/items/{product_id}` and `DELETE /cart`.

#### Decision: absolute quantities here, after arguing against them in Step 33

Step 33 refused an absolute `stock_quantity` and required a difference. This step does the
opposite, deliberately.

| | Stock | Cart line |
|---|---|---|
| Who changes it | many customers and admins, concurrently | **one person — the owner** |
| "set to 3" means | "I believe it is 4, make it 3" — an assumption that can already be wrong | "I want 3" — a fact about intent |
| A lost update | erases someone else's sale | impossible; there is no one else |

The Step 33 rule was never *absolute values are bad*. It was *do not compute a value from
shared state you no longer hold*. A cart is not shared state, and a customer typing `3` into a
quantity box is stating intent, not inferring a total.

`PUT` rather than `PATCH`: the line has one mutable field, so sending the quantity replaces
the whole of it, and the request is idempotent — a retrying client gets the same result.

#### Decision: `quantity = 0` is rejected, not treated as removal

422, with removal given its own endpoint. Conflating two operations in one field means a
client that sends `0` by accident silently destroys a line. `quantity > 0` is also what the
database enforces, so the schema and the constraint agree.

#### Decision: different success codes for the two deletes

`DELETE /cart/items/{product_id}` returns **200 with the cart**, because removing a line
changes the total and the client needs the new one; a bare 204 would force an immediate `GET`.
`DELETE /cart` returns **204**, because the result of emptying a cart is known in advance and
there is nothing worth sending.

#### Decision: emptying a cart keeps the cart row

The row carries no state beyond its owner, so deleting it would only mean creating it again on
the next request. `clear_items` is a single `DELETE` statement rather than loading the lines to
remove them one by one — the rows are not needed for anything, so fetching them would be work
done only to throw away.

#### The Step 37 lesson, applied rather than relearned

`_locked_item` exists so that both change operations take the lock **before** the line is read
for the first time. Reading it beforehand would let the session answer the later read from the
copy it already held, and the lock would protect nothing — the defect found in Step 37. The
lock is also released with an explicit `rollback()` before raising `NotFoundError`, as in
`adjust_stock`.

#### Files changed

| File | Change |
|---|---|
| `app/modules/cart/schemas.py` | `CartItemSetQuantity` |
| `app/modules/cart/repository.py` | `remove_item`, `clear_items` |
| `app/modules/cart/service.py` | `_locked_item`, `set_item_quantity`, `remove_item`, `clear_cart` |
| `app/modules/cart/router.py` | `PUT /items/{product_id}`, `DELETE /items/{product_id}`, `DELETE ""` |

#### Verification

24 of 24 assertions over HTTP against a running server:

| Group | Cases |
|---|---|
| access control | `PUT`, `DELETE` item and `DELETE` cart with no token → 401 |
| setting | 2 → 7 gives quantity exactly 7 and total `102.00` = 7×12.00 + 4×4.50, still two lines; the same request again is idempotent; lowering to 1 works |
| rejections | quantity 0 → 422; 1000 → 422; unknown field → 422; product not in the cart → 404 |
| removal | removing a line gives 200 with the new total `18.00`; removing it again → 404; emptying gives 204 and an empty cart; emptying an already-empty cart → 204 |
| ownership | the shopper's `PUT`, `DELETE` item and `DELETE` cart all leave the admin's identical line untouched |

Two concurrency runs:

- **20 interleaved `PUT`/`DELETE` on one line** → `{200: 1, 404: 19}`, no 500s. Recorded
  honestly: this sequence **degenerates** once the first `DELETE` wins, so it mostly exercises
  the 404 path and is weak evidence on its own.
- **20 concurrent `PUT`s with 20 different quantities** → 20 × 200, **one** line, final
  quantity **14** — a value that was actually sent rather than a corrupted sum. Last writer
  wins, which is correct for absolute semantics.

Ruff clean. All test data removed; `carts` 0, `cart_items` 0, `products` 1, `users` 2.

#### Risk & Controls Note

- **Regulatory / data protection:** Unchanged from Step 37. Cart contents remain personal data
  linking a customer identity to purchasing intent. `DELETE /cart` gives a customer a way to
  erase that intent on demand, which is a small step towards a deletion right, but it is not a
  retention policy and abandoned carts still accumulate — open item.
- **Security:** Access control stays structural: no cart id or user id is accepted from any
  request, so the three new endpoints add no parameter to tamper with. Isolation was proven by
  driving the shopper's `PUT`, `DELETE` item and `DELETE` cart against an admin holding an
  identical line for the same product, and checking the admin's cart after each. `DELETE /cart`
  is the most destructive endpoint in the API so far and is bounded to the caller's own data by
  construction.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`. All
  test data synthetic.
- **Required controls / approvals:** Still no rate limiting on cart mutations (Step 63), and
  still no audit of who emptied a cart and when — low consequence while a cart is working
  state, but it must not carry into orders, where the equivalent action is financially
  material. Retention policy still required before production.
- **Residual risk:** **Low.** Ownership is enforced by construction and proven by test, the
  locking order follows the rule established in Step 37, and concurrent writes were shown to
  produce a value that was actually sent rather than a corrupted one.

---

### ✅ Step 39 — Price and Availability Handling in a Cart

**Completed:** 2026-10-31 · No migration. No new dependency.

Availability checks on the write paths, and per-line issue reporting on the read path.

#### The price problem that does not exist

The classic cart bug is a stale price: the item was added at 12.00, the price rose to 15.00,
and the customer checks out at the old figure or is charged a different one from the one shown.

That bug is impossible here. `cart_items` has no price column, so there is nothing to go stale,
and the cart reads `products.price` on every request. The Step 36 decision removed the whole
class of bug rather than managing it. There is deliberately no "price changed since you added
this" warning, because there is nothing to compare against.

#### The central rule: a cart check is a courtesy, not a reservation

Refusing an add of 5 when 3 exist is helpful. Passing that check guarantees **nothing** —
another customer can buy the last one a moment later, and the cart holds no claim on anything.

Demonstrated rather than asserted. One product, stock 1, two customers:

```
product 52, stock 1
customer A adds it   -> HTTP 200
customer B adds it   -> HTTP 200
stock afterwards     -> 1
```

Both succeeded and stock never moved. Exactly one of them can actually be sold it, and
deciding which is the order transaction's job. Getting this backwards — treating the cart
check as authoritative — is how real shops oversell.

#### Decision: `GET /cart` never fails because of availability

A cart holding an off-sale product still returns 200 and still lists the line. A customer
whose cart cannot be read cannot fix it. Problems are reported per line, not by refusing the
request.

#### Decision: a short code, not a sentence

`issue` is `"unavailable"`, `"insufficient_stock"` or `null`. The client chooses the wording
and the translation, and the message is then free to change without breaking anyone.
`is_active` and `available_stock` are reported alongside so a client can explain the problem
rather than only report it.

#### Decision: the total includes lines that cannot be bought

`total` sums every line, matching what the customer can see listed. Quietly dropping a line
from the total would make the arithmetic on screen look wrong. `has_issues` carries the
signal instead, and checkout will refuse while it is true.

#### Decision: the add check is against the resulting total

Five adds of one each are refused at the same point as one add of five. Checking only what the
request carried would let a customer walk past the limit one unit at a time.

#### Decision: one `UnavailableError` for both causes

Off sale and not enough stock both map to 409 — the request is well formed and the product
exists, it conflicts with the product's current state. The message says which. Kept distinct
from `InsufficientStockError`, which belongs to stock adjustments and means an admin tried to
remove more than exists.

#### Files changed

| File | Change |
|---|---|
| `app/core/exceptions.py` | `UnavailableError` → 409 |
| `app/modules/cart/schemas.py` | `is_active`, `available_stock`, `issue` on the line; `has_issues` on the cart |
| `app/modules/cart/service.py` | `line_issue`, `_check_can_be_bought`; applied in `add_item` and `set_item_quantity` |
| `app/modules/cart/router.py` | populates the new fields; maps `UnavailableError` to 409 |

#### Verification

23 of 23 assertions over HTTP against a running server:

| Group | Cases |
|---|---|
| refusing at add | 5 when 3 exist → 409; an off-sale product → 409; exactly 3 → 200; one more making 4 → 409, proving the check is cumulative |
| a healthy cart | `has_issues` false, `issue` null, `is_active` and `available_stock` reported |
| product goes off sale | `GET` still 200; `issue` `unavailable`; `has_issues` true; the line still listed; total still counts it; `PUT` on that line → 409; `DELETE` of that line → 200 |
| stock falls below the cart | `issue` `insufficient_stock`; `available_stock` shows 2; `has_issues` true |
| fixing it | setting 3 when 2 exist → 409; setting 2 → 200; `issue` and `has_issues` both clear |

Plus the no-reservation demonstration above.

Note the pair in the third group: a line that cannot be bought can still be **removed** but not
**changed**. Blocking removal would trap a customer with a cart they cannot check out and
cannot repair.

Ruff clean. All test data removed; `carts` 0, `cart_items` 0, `products` 1, `users` 2.

#### Risk & Controls Note

- **Regulatory / data protection:** Unchanged. No new personal data. Cart contents remain
  personal data with no retention policy — still open.
- **Security:** Availability responses disclose `available_stock` to any authenticated customer
  who has the product in their cart. That is ordinary shop information and the figure is
  already implicit in whether an add succeeds, so the disclosure is deliberate rather than
  accidental. A competitor could poll it to track inventory; acceptable for a consumer
  catalogue, and worth revisiting if stock levels ever become commercially sensitive. Recorded
  as an open item rather than treated as settled.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`. All
  test data synthetic.
- **Required controls / approvals:** The cart check must **never** be mistaken for the
  authoritative one. Phase 9 must re-check availability inside the order transaction while
  holding the product row lock, and that check — not this one — is what prevents overselling.
  This is the single most important carry-forward in Phase 7.
- **Residual risk:** **Low** for this step in isolation, because nothing here is relied on for
  correctness. It becomes **High** if checkout is later built on the assumption that a cart
  without issues is safe to fulfil.

#### Open items added

- `available_stock` is visible to any authenticated customer with the product in their cart;
  revisit if inventory levels become commercially sensitive.

---

### ✅ Step 40 — When to Calculate Prices and Validate Inventory

**Completed:** 2026-10-31 · Phase 7 complete. No code change; the existing behaviour was
attacked rather than described.

#### The attack, attempted seven ways

The oldest e-commerce exploit is a client sending its own price. Every attempt was refused:

| Attempt | Result |
|---|---|
| `POST /cart/items` with `price`, `unit_price`, `line_total`, `total` | 422 each |
| `PUT /cart/items/{id}` with `price`, `unit_price`, `total` | 422 each |
| customer creates a product priced `0.01` | 403 |
| customer patches a product's price | 403 |

Two independent defences, and the order matters. **No request schema has a money field a
customer can set** — `CartItemAdd` carries only `product_id` and `quantity` — so there is
nothing to validate. `extra="forbid"`, added in Step 33 after a silent-drop bug, turns an
attempt into a visible 422 rather than a silent ignore. Writing prices at all requires admin,
which is the Step 30 role check.

The strongest defence is the first one: the field does not exist. A validator can be wrong; an
absent field cannot be set.

#### Prices are read, never remembered

Demonstrated: with a product at `100.00` in a customer's cart, an admin raised it to `250.00`,
and the customer's next `GET /cart` showed `250.00` with the total following. Nothing was
cached, so nothing could be stale.

#### Why `Decimal`, measured

```
  A cart of 3 items at 0.10 each
    float   0.1 * 3 = 0.30000000000000004
    Decimal 0.10 * 3 = Decimal('0.30')

  1000 orders of 19.99 each
    float   19990.000000000135
    Decimal 19990.00
    off by  1.35E-10
    float   == 19990.00 ?  False
    Decimal == 19990.00 ?  True
```

After a thousand ordinary orders the float total is wrong and an equality check against the
expected figure fails. `Numeric(12, 2)` in PostgreSQL and `Decimal` in Python keep it exact at
both ends with no lossy conversion between them.

The server also refuses prices it cannot represent honestly: `-1.00` → 422, and `9.999` → 422
rather than rounding to `10.00` silently.

#### The timeline: when a price is calculated

| Moment | What happens | Source of truth |
|---|---|---|
| Browsing | read `products.price` | `products` |
| Add to cart | **nothing stored** | — |
| Viewing cart | read `products.price` | `products` |
| **Order created** | **copied into `order_items.unit_price`** | the order |
| After | never changes again | the order |

The copy at order time is not duplication of the same fact. `products.price` means *what this
costs today*; `order_items.unit_price` means *what this customer agreed to pay on that date*.
The second must survive every later price change, or an invoice cannot be reprinted. Copying
earlier — at add-to-cart — would be duplication of the same fact, which is why Step 36 refused
it.

#### The timeline: when inventory is validated

| Moment | Check | Authority |
|---|---|---|
| Add to cart | yes, no lock held | **none** — a courtesy |
| Viewing cart | reported as `issue` | **none** |
| **Order created** | `SELECT ... FOR UPDATE`, then decrement | **authoritative** |

Everything built in Phase 7 is advisory. It exists to give a good error early, not to make a
promise.

#### Carry-forward for Phase 9

1. **Lock every product row in the order, sorted by `product_id`** — the deadlock rule proven
   in Step 35. Two orders containing the same two products in different cart order deadlock
   otherwise, and PostgreSQL kills one of them.
2. **Re-check availability under the lock.** A cart reporting `has_issues: false` proves
   nothing; it was computed before any lock existed.
3. **Read prices inside the transaction** and copy them into `order_items`.
4. **Decrement stock in the same transaction** as the order insert. Separate transactions
   allow an order to exist for stock that was never taken.
5. **Clear the cart only after the order commits** (roadmap Step 50). Clearing first loses the
   customer's basket when the order fails.

#### Verification

14 of 14 assertions over HTTP, plus the arithmetic demonstration above. No application code
was changed in this step. All test data removed.

#### Risk & Controls Note

- **Regulatory / data protection:** None directly. Pricing integrity is a financial-reporting
  and consumer-protection concern rather than a data-protection one: a customer charged a
  figure other than the one displayed is a regulatory problem in every jurisdiction in scope.
- **Security:** The client-price injection class is closed, and closed structurally — the
  field does not exist in any customer-facing request schema, so there is no validator to
  bypass. Price writes require an administrator. Verified by attempting seven variants rather
  than by reading the schemas.
- **Data residency / cross-border:** None. Local Docker PostgreSQL on `127.0.0.1:5433`. All
  test data synthetic.
- **Required controls / approvals:** Price changes are **not audited** — there is no record of
  who changed a price, when, or from what. For a regulated fintech this is a genuine gap:
  pricing history is routinely required to answer a customer dispute or a regulator's
  question, and `products.updated_at` records only that something changed. Step 60 must cover
  price changes specifically, not only authentication events. Until then, a disputed charge
  cannot be reconstructed from the data.
- **Residual risk:** **Medium**, driven entirely by the missing price-change audit rather than
  by anything in the request path. The injection risk itself is **Low** and structurally
  closed.

#### Open items added

- No audit trail for price changes; a disputed charge cannot be reconstructed. Must be covered
  by Step 60.

---

### ✅ Step 41 — Customer Addresses

**Completed:** 2026-10-31 · Phase 8 begins. Migration generated and run by the user.

`app/modules/addresses/models.py` with one table, `addresses`. Model only; endpoints are
Step 42.

#### Decision: an address book, not a record — orders will copy, never reference

The same shape as the price decision in Step 40.

| | Price | Address |
|---|---|---|
| Lives in | `products.price` | `addresses` |
| Changed by | an admin, at any time | the customer, at any time |
| An order needs | what they agreed to pay | where it was actually sent |
| Solution | copy into `order_items` | **copy into `orders`** |

An order holding `address_id` would have its shipping address silently rewritten when the
customer later corrected a typo, and nobody could answer where the parcel was actually sent.
Phase 9 must snapshot the fields, and `orders` must have **no foreign key to `addresses`**.

That is also what makes `ON DELETE CASCADE` on `user_id` safe here: deleting a customer takes
their personal data with it without stranding an order.

#### Decision: one default per customer, enforced by a partial unique index

```sql
CREATE UNIQUE INDEX uq_addresses_user_id_default ON addresses (user_id) WHERE is_default
```

Unique across the rows where `is_default` is true, silent about the rest. Two simultaneous
requests cannot both set a default; the database decides, as with the SKU index and the
cart-line index.

A plain unique index on `(user_id, is_default)` would be wrong in a way that is easy to miss:
it would allow only **one non-default address** per customer, which is the opposite of the
intended rule.

#### Decision: what is stored, and what deliberately is not

Fourteen columns, and nothing fulfilment does not need. Notable choices:

- `country` is `VARCHAR(2)`, ISO 3166-1 alpha-2, upper case — so "UAE", "U.A.E." and "United
  Arab Emirates" cannot all mean the same place.
- `postal_code` and `region` are **optional**. Postal codes are not universally used or
  required across KSA, the UAE and Bahrain, and demanding one would make valid addresses
  unenterable.
- `recipient_name` is separate from the account holder's name, because the person receiving a
  parcel is often not the person who ordered it.
- `phone` is stored as typed. Normalising to E.164 would be better for dialling but needs a
  library that knows every country's numbering plan, and a wrong "correction" to a delivery
  number is worse than an unformatted one.
- `MAX_ADDRESSES_PER_USER = 20`, enforced in the service at Step 42. A data-protection limit
  rather than a business rule: personal data should not accumulate without bound.

No national identifier, date of birth, or any other identity-document field. Nothing here
requires one.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/addresses/__init__.py` | module marker |
| `app/modules/addresses/models.py` | `Address`, `MAX_ADDRESSES_PER_USER` |
| `alembic/env.py` | imports `Address` so autogenerate sees it |

#### Verification

Compiled DDL inspected before the migration was generated: all fourteen columns, the FK with
`ON DELETE CASCADE`, the FK index, and the partial unique index with its `WHERE is_default`
clause. Ruff clean.

Migration `786dd9382dba` needed no hand edit. Autogenerate kept
`postgresql_where=sa.text('is_default')` on both the create and the drop, which it needs in
order to identify the right index. No check constraints in this table, so the Step 30 and 32
trap does not apply here. `alembic check` then reported no drift.

Behaviour verified against the migrated database:

| Case | Result |
|---|---|
| a customer may have a default address | allowed |
| a **second** default for that customer | refused, `uq_addresses_user_id_default` |
| three further **non-default** addresses alongside it | allowed, 4 rows total |
| another customer's own default | allowed |
| a three-letter country code | refused, `DataError` |
| deleting a user | their addresses go, the other customer's stay |

The third row is the one that matters. A plain unique index on `(user_id, is_default)` would
have refused the second non-default address — the exact failure mode predicted before the
index was written, confirmed by allowing it rather than by reasoning about it.

Synthetic test data only, removed afterwards; no addresses left behind.

#### Risk & Controls Note

- **Regulatory / data protection:** **The most sensitive table in the project so far.** Every
  column is personal data under PDPL and the UAE and Bahrain equivalents, and a delivery
  address plus a phone number is directly identifying and locating. Collection is limited to
  what fulfilment needs, with no identity-document or date-of-birth fields. `ON DELETE CASCADE`
  gives a working deletion path when a user is removed. Retention is **not** addressed: there
  is no rule saying how long an address book is kept after a customer stops ordering, and that
  is now a required control rather than an observation.
- **Security:** No endpoint yet, so no surface. The rule for Step 42 is fixed now and is the
  same structural one used for carts: addresses are reachable only through the authenticated
  user, never by an id in a path that a client could change. An address id in a URL would be a
  direct IDOR onto home addresses, which is the worst-consequence version of that bug in this
  codebase. Admin read access for fulfilment is **not** granted and must be designed
  deliberately when Phase 9 needs it, with least privilege and logging, rather than falling out
  of a generic admin role.
- **Data residency / cross-border:** None today — local Docker PostgreSQL on `127.0.0.1:5433`.
  This is the table that makes residency a live question for production: addresses of KSA data
  subjects are expected to remain in approved locations, and any backup, analytics copy, log
  export or third-party fulfilment integration carrying this table is a cross-border transfer
  that needs assessment. Flagged now, before the data exists, rather than after.
- **Required controls / approvals:** Retention and deletion policy for addresses. Encryption at
  rest for the database holding them. Access review for any admin path that can read them.
  Masking in logs — no address field may ever be written to an application log or an error
  response. Residency assessment before any non-local deployment.
- **Residual risk:** **Medium.** The schema is minimal and the deletion path works, but the
  table holds directly identifying location data with no retention rule, no encryption-at-rest
  decision recorded, and no logging or masking controls yet. It drops to Low once Step 42
  lands the ownership-scoped endpoints and the controls above are in place.

#### Open items added

- No retention or deletion policy for addresses after a customer stops ordering.
- No encryption-at-rest decision recorded for the database holding addresses.
- No log-masking rule for address fields.
- Admin read access to customer addresses must be designed deliberately in Phase 9, not
  inherited from the generic admin role.

---

### ✅ Step 42 — Associate Addresses with Users

**Completed:** 2026-10-31 · No migration. No new dependency.

Five endpoints under `/addresses`, all scoped to the authenticated customer.

#### Correction to the Step 41 rule: scoping, not absence

Step 37 removed the cart id from every URL, and Step 41 restated that as the rule for
addresses. It does not transfer. A customer has **one** cart, so the id was unnecessary; a
customer has **many** addresses, so they must be able to name one to edit or delete it.

The defence is therefore scoping rather than absence:

```python
select(Address).where(Address.id == address_id, Address.user_id == user_id)
```

`user_id` is part of the `WHERE` clause rather than checked after the row is fetched. A
forgotten check is a data leak; a missing `WHERE` clause is a query that returns nothing.

#### Decision: 404 for someone else's address, never 403

A 403 would confirm that the address exists, turning the endpoint into an oracle for
discovering which ids are real. 404 says only *not yours or not there* and does not
distinguish between them. This is the opposite of the Step 30 choice, where 403 was right
because the resource was public and only the action was restricted — here the existence of the
row is itself the secret.

#### Decision: the first address becomes the default whatever the request said

A customer with addresses but no default is a state checkout would have to cope with for no
reason.

#### Decision: unsetting the only default is refused, not obeyed

`PATCH {"is_default": false}` on the current default returns 422 telling the customer to make
another address the default instead. Obeying it would leave them with addresses and none
chosen — the state the previous decision exists to prevent.

#### Decision: deleting the default promotes the oldest survivor

So *if you have addresses, one of them is the default* stays true without the customer having
to think about it.

#### Decision: address writes serialise on the customer's `users` row

`_lock_address_book` takes `SELECT users.id ... FOR UPDATE`. The thing being protected is
*this customer's address book*, and the `users` row is the only row that always exists to
stand for it — there is no address-book row to lock, and the addresses themselves may not
exist yet.

Without it, two requests could both decide to become the default, both clear the old one, and
the partial unique index would turn the loser into a 500 rather than a sensible result. Only
address writes take this lock, so nothing else is serialised by it.

#### Decision: no `Page` envelope on the list

`MAX_ADDRESSES_PER_USER` caps the list at 20, so paging it would be ceremony. The cap is
enforced in `create_address` with a 422.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/addresses/schemas.py` | `AddressCreate`, `AddressUpdate`, `AddressRead` |
| `app/modules/addresses/repository.py` | `list_for_user`, `get_for_user`, `count_for_user`, `clear_default`, `add`, `remove` |
| `app/modules/addresses/service.py` | `_lock_address_book`, list, get, create, update, delete |
| `app/modules/addresses/router.py` | `GET`, `POST`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` |
| `app/api/router.py` | registers the addresses router |

#### Verification

34 of 34 assertions over HTTP against a running server:

| Group | Cases |
|---|---|
| access control | `GET` and `POST` with no token → 401 |
| creating | `country: "bh"` stored as `BH`; the first address is default unasked; the second is not; a third asking to be default leaves exactly one default and is listed first |
| validation | three-letter country, digits as country, empty recipient, unknown field, and a `user_id` in the body → 422 each |
| updating | partial update changes only what was sent; making another address the default leaves exactly one; unsetting the only default → 422 |
| **ownership** | `GET`, `PATCH` and `DELETE` of another customer's address → **404 each**; their row is verifiably untouched afterwards; their id never appears in my list |
| deleting | deleting the default promotes another, leaving exactly one; deleting twice → 404 |
| the cap | 21 creates → `{201: 20, 422: 1}` |
| concurrency | 5 simultaneous "make me the default" → 5 × 200, no 500s, exactly one default survived |

The ownership group is the one that matters. It attacks the boundary with a real id belonging
to a real other customer, and checks the victim's row afterwards rather than trusting the
status code.

Ruff clean. All test data removed; `addresses` 0, `users` 2.

#### Risk & Controls Note

- **Regulatory / data protection:** These are the first endpoints that read and write directly
  identifying location data. Data minimisation holds — `AddressRead` omits `user_id`, which the
  client already knows and which would only widen what an error or a log could leak. The
  20-address cap limits accumulation per customer. `DELETE /addresses/{id}` gives a customer a
  self-service erasure path for this data, which is a meaningful step towards a deletion right,
  though **not a retention policy**: nothing expires an address when a customer stops ordering.
- **Security:** The boundary is enforced in the `WHERE` clause of every query rather than by a
  check that could be forgotten, and `user_id` cannot be injected through any request body —
  `extra="forbid"` rejects it with 422, proven by sending it. 404 rather than 403 prevents the
  endpoint from confirming which address ids exist. Concurrency on the default flag was proven
  not to produce 500s or two defaults.
- **Data residency / cross-border:** None today — local Docker PostgreSQL on `127.0.0.1:5433`.
  Unchanged from Step 41: this is the data whose location must be assessed before any non-local
  deployment, and any log export or third-party fulfilment integration carrying it is a
  cross-border transfer.
- **Required controls / approvals:** Carried forward unchanged and still **not in place** —
  retention and deletion policy, encryption at rest, log masking for address fields, residency
  assessment. Added by this step: address endpoints are **not rate limited**, so the cap is on
  stored rows rather than on request volume, and enumeration attempts against
  `GET /addresses/{id}` are neither throttled nor logged. Folds into Steps 60 and 63.
- **Residual risk:** **Medium**, unchanged from Step 41 and for the same reasons — the access
  control added here is sound and proven, but the surrounding controls on retention,
  encryption, masking and monitoring do not exist yet. The endpoints themselves are **Low**.

#### Open items added

- Address endpoints are not rate limited; enumeration attempts against `GET /addresses/{id}`
  are neither throttled nor logged.

---

### ✅ Step 43 — Shipping and Checkout Data Contracts

**Completed:** 2026-10-31 · Phase 8 complete. No migration. No new dependency. Shapes only —
no models and no endpoints.

#### Decision: the checkout request is one field

```json
{"address_id": 7}
```

No items, no quantities, no prices, no total, no user. Every one of those already exists on
the server: the cart rows, `products.price`, the arithmetic, and the token.

| What a naive API accepts | Where it actually comes from |
|---|---|
| `items` | the customer's cart rows |
| `unit_price` | `products.price`, read under lock |
| `total` | computed server-side |
| `user_id` | the token |
| `shipping_address` | copied from `addresses`, scoped to the user |

A field a client can send is a field an attacker can set, so the shortest request is the
safest one. `address_id` is the single exception and is safe only because it resolves against
that customer's own addresses — an id belonging to someone else does not match, so it cannot
be used to post a parcel to an address the caller cannot already see.

#### Decision: `ShippingAddress` is a copy, not a pointer

Eight fields: `recipient_name`, `phone`, `line1`, `line2`, `city`, `region`, `postal_code`,
`country`.

Deliberately absent: `id`, `user_id`, `label`, `is_default`, `created_at`, `updated_at`. None
of those describe where a parcel went. Keeping the `id` in particular would invite someone to
follow it back to the live row, which is precisely the staleness the copy exists to prevent.

The same reasoning as `order_items.unit_price`: `products.price` means *what this costs
today*, and a shipping address means *where this parcel was sent*, which must stay true
forever.

It lives in `app/modules/addresses/schemas.py` rather than the orders module, because it is an
address shape and address knowledge belongs with addresses. Orders import it.

#### Decision: the snapshot is taken through `get_address`

`snapshot_for_shipping` calls the same ownership-scoped lookup every other address operation
uses, so an id belonging to someone else raises `NotFoundError` here exactly as it does
elsewhere. Checkout must never reach around this and read the row directly.

#### Decision: order read shapes and statuses are *not* defined here

They arrive in Step 45 beside `models.py`, so the status values are defined once next to the
check constraint that enforces them rather than twice in two modules. `app/modules/orders/`
exists now holding only `CheckoutRequest`.

#### Deliberately deferred: the idempotency key

A double-submitted checkout creating two orders is a real problem, not a hypothetical one. The
field is **not** added now because the mechanism behind it belongs to Steps 47 and 52, and a
field with no mechanism is half a feature that looks like a whole one. Recorded as an open
item, and noted that adding it later changes this contract.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/addresses/schemas.py` | `ShippingAddress` |
| `app/modules/addresses/service.py` | `snapshot_for_shipping` |
| `app/modules/orders/__init__.py` | module marker |
| `app/modules/orders/schemas.py` | `CheckoutRequest` |

#### Verification

25 of 25 contract assertions, against the schemas directly:

- `address_id` alone is accepted and is the only field present
- `items`, `total`, `unit_price`, `price`, `user_id`, `status` and `shipping_address` are each
  rejected by name
- `address_id` is required and must be positive
- `ShippingAddress` carries all eight shipping fields and none of `id`, `user_id`,
  `is_default`, `label`, `created_at`, `updated_at`

7 of 7 behavioural assertions against the live database, which is where the point of a
snapshot actually shows:

| Case | Result |
|---|---|
| snapshot taken from a real address | `Original Person, 1 Old Street` |
| customer then edits the address | live row becomes `99 New Street` |
| the snapshot | **unchanged** — line, recipient and country all still the originals |
| customer then deletes the address | the snapshot still reads `1 Old Street` |
| snapshotting another customer's address | `NotFoundError: Address 37 does not exist` |

The edit and the delete are the whole argument for copying rather than referencing, and they
were run rather than asserted. Ruff clean; no test data left behind.

#### Risk & Controls Note

- **Regulatory / data protection:** The snapshot **duplicates personal data** — a second copy
  of a delivery address and phone number that a customer's `DELETE /addresses/{id}` will not
  reach, proven above. That is deliberate and necessary, since an order must record where a
  parcel was actually sent, but it means a customer erasure request cannot be satisfied by
  deleting the address book alone. Order retention is a separate decision with a different
  basis: commercial and tax records are normally retained for a fixed statutory period, so the
  lawful position is retention-with-justification rather than deletion. Required before
  production, not optional, and now the single most important data-protection item open in the
  project.
- **Security:** The contract closes the injection surface structurally rather than by
  validation — there is no money, no user and no item field to attack, proven by rejecting
  seven of them by name. The one id a client may send is resolved through the same
  ownership-scoped lookup as every other address read, so checkout cannot ship to an address
  the caller cannot already see.
- **Data residency / cross-border:** Unchanged, and now slightly wider: once orders exist, the
  same personal data sits in two tables, so any residency assessment, backup scope or analytics
  export must cover `orders` as well as `addresses`.
- **Required controls / approvals:** Retention policy for order-held personal data, with the
  statutory basis stated. An erasure procedure that accounts for snapshots, rather than
  assuming address deletion suffices. Both carried into Phase 9 and neither is optional.
  Existing items unchanged: encryption at rest, log masking, rate limiting.
- **Residual risk:** **Low** for this step as written, since nothing is stored yet and the
  contracts narrow rather than widen what is accepted. It becomes **Medium** the moment orders
  persist, on the retention and erasure gap above rather than on anything in the request path.

#### Open items added

- Order-held personal data will not be reached by customer-initiated address deletion; an
  erasure procedure covering snapshots is required.
- No idempotency key on the checkout contract; a double-submitted checkout would create two
  orders. Steps 47 and 52, and adding it will change this contract.

---

### ✅ Step 44 — Order Creation Design with Transaction Boundaries

**Completed:** 2026-10-31 · Phase 8 fully closed. No code change; the design is settled and the
failure modes it prevents were demonstrated against the live database.

#### The sequence

```
BEGIN
 1.  lock the customer's cart row                     FOR UPDATE
 2.  load its lines and their products
 3.  refuse an empty cart                             -> 409
 4.  snapshot the shipping address (ownership-scoped) -> 404 if not theirs
 5.  collect the product ids and SORT them
 6.  lock those product rows, in that sorted order    FOR UPDATE
 7.  re-read price and stock FROM THE LOCKED ROWS
 8.  validate: active, and stock >= quantity          -> 409
 9.  INSERT orders       (status 'pending', shipping snapshot, total)
10.  INSERT order_items  (sku, name, unit_price, quantity - all copies)
11.  UPDATE products     SET stock_quantity = stock_quantity - n
12.  DELETE cart_items
COMMIT
```

**Line 7 is not redundant.** Everything Phase 7 reported was read without a lock and is now
potentially stale. The values that decide money and stock must be the ones read after line 6.

**Line 12 is inside the transaction**, not after it. The roadmap phrases Step 50 as *clear the
cart only after successful order creation*; inside the same transaction is strictly stronger.
A separate clearing transaction leaves a window in which the order exists and the cart still
does, and a refresh in that window orders twice.

#### Demonstrated: why it is one transaction

```
1. One transaction    stock before 100 -> taken to 90 -> failure -> stock after 100
2. Two transactions   stock before 100 -> committed 90 -> failure -> stock after 90
```

The second case is the one that reaches a support queue: ten units sold to nobody and no order
to refund against. Nothing in the database records that it happened; the only trace is a stock
count that no longer matches the shelf.

#### Demonstrated: why payment is outside it

```
0.00s  A   locked the product, now calling the payment provider...
0.30s  B   tries to check out the same product
3.00s  A   payment returned, committing
3.01s  B   got the lock after waiting 2.71s
```

A three-second payment round trip is unremarkable. Holding a row lock across it makes every
customer buying that product queue behind it, and each waiting request holds a connection from
a finite pool. At a few hundred checkouts a minute the pool empties and endpoints unrelated to
orders begin failing.

The boundary is therefore:

```
transaction 1   create the order as 'pending', take stock, clear the cart   COMMIT
                --- outside any transaction ---
                call the payment provider
transaction 2   record the result, move the status                          COMMIT
```

**Consequence, recorded now rather than discovered in Phase 10:** taking stock at order
creation means a pending order that is never paid holds that stock indefinitely. Something
must release it — an expiry sweep, a timeout, or a compensating return of stock when payment
fails. This is design debt Phase 10 inherits deliberately, not an oversight.

The alternative — taking stock only after payment succeeds — trades it for a worse problem:
the shop can accept money for goods it no longer has.

#### Lock ordering across the whole application

| Operation | Locks |
|---|---|
| add, change or remove a cart line | cart |
| adjust stock | product |
| change addresses | user |
| **checkout** | **cart, then products sorted by id** |

No operation takes a product lock and then a cart lock, so there is no cycle between resource
types. Within checkout, sorting the product ids prevents the cycle between two checkouts —
the deadlock demonstrated in Step 35.

#### What each failure does

| Failure | When | Result |
|---|---|---|
| empty cart | before any lock | 409, nothing written |
| address not the caller's | before product locks | 404, nothing written |
| product inactive | under lock | 409, rollback, stock untouched |
| insufficient stock | under lock | 409, rollback |
| deadlock | under lock | one transaction killed; prevented by sorting |
| crash before `COMMIT` | any point | nothing happened at all |
| crash after `COMMIT` | — | order, stock and cart all consistent |

#### Still unresolved, deliberately

A double-submitted checkout creates two orders. Nothing above prevents it: both requests find
a full cart, both pass validation, and the first one's `DELETE cart_items` only takes effect at
its commit. Serialising on the cart lock means the second waits rather than racing, and will
then find an empty cart and get a 409 — which is the right answer by accident rather than by
design. It is the right answer only while the cart is cleared in the same transaction, and it
says nothing useful to the customer. A proper idempotency key is Steps 47 and 52.

#### Verification

Three demonstrations against the live database, using `products.stock_quantity` because the
order tables do not exist yet. No application code was changed. The temporary product was
removed.

#### Risk & Controls Note

- **Regulatory / data protection:** None directly. Indirectly material: the atomicity
  established here is what makes stock figures and order records reconcile, and both feed
  financial reporting. The two-transaction failure shown above produces an inventory
  discrepancy with no corresponding record, which is precisely the kind of unexplained
  difference an audit is designed to find.
- **Security:** Neutral — no new surface. The design fixes two controls that Phase 9 must
  honour: availability is re-validated under lock rather than trusted from the cart, and the
  shipping address is resolved through the ownership-scoped lookup rather than read directly.
- **Data residency / cross-border:** None for the design. The payment call placed outside the
  transaction **is** a cross-border consideration in its own right: it leaves the system
  boundary, and what is sent with it must be assessed in Phase 10. Deciding that now, before
  any integration exists, is cheaper than deciding it afterwards.
- **Required controls / approvals:** Pending-order stock release must be designed in Phase 10,
  not left implicit. Idempotency on checkout is required before any real payment integration —
  a double charge is a regulatory and reputational event, not a bug report. `lock_timeout`
  remains unset and matters more here than anywhere else, because checkout holds several locks
  at once.
- **Residual risk:** **Low** for the design itself, which narrows failure modes rather than
  adding any. The risks it names — pending-order stock, idempotency, lock timeouts — are all
  carried forward explicitly and none are closed.

#### Open items added

- A pending order that is never paid holds stock indefinitely; a release mechanism is required
  in Phase 10.
- What is sent to the payment provider leaves the system boundary and needs a cross-border
  assessment before any integration.

---

### ✅ Step 45 — Order and Order-Item Models

**Completed:** 2026-10-31 · Phase 9 begins. One migration, applied. No endpoints and no checkout
logic — those are Steps 47–50.

#### The change in the rules

Everything before this step was working state. An order is a record, and the rules invert:

| | Cart / address | Order |
|---|---|---|
| May be edited later | yes | no |
| Deleted with the user | yes (CASCADE) | **no (RESTRICT)** |
| Reads today's price | yes | **never — its own copy** |
| Reads the live address | yes | **never — its own copy** |

#### Decisions

**The address is eight flat columns, copied.** Not a foreign key — Step 43 demonstrated the
staleness — and not JSON, so the columns can be indexed, constrained and read in `psql` without
JSON operators. Nullable exactly where `Address` is nullable.

**`orders.user_id` is `ON DELETE RESTRICT`.** Carts and addresses CASCADE; a financial record
must not. The consequence is deliberate and now live: **a customer who has ordered cannot be
deleted.**

**`total_amount` is stored.** It is what was charged, a fact about money that moved, not
arithmetic to redo on every read. Recomputing it would let a future rounding change silently
rewrite history. `NUMERIC(12,2)`, never float.

**Order items have no `created_at` or `updated_at`.** An item never changes, so `updated_at`
could only repeat its creation time, and its creation time is already its order's.

**`status` has no `server_default`.** Whoever creates an order states its state in the calling
code, where it can be seen. The check constraint makes a typo impossible.

**The status list is written once:**

```python
OrderStatus = Literal["pending", "paid", "shipped", "delivered", "cancelled"]
ORDER_STATUSES: tuple[str, ...] = get_args(OrderStatus)
```

`get_args` reads the values back off the type, so the API type and the check constraint are the
same list and cannot drift. Which moves between statuses are legal is Step 49.

**No `cascade="all, delete-orphan"` on `Order.items`**, unlike `Cart.items`. Removing a line
from an order should not be possible, so the ORM is given no quiet way to do it: deleting an
`Order` through the session would try to null the children's `order_id` and fail loudly.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/orders/models.py` | `Order`, `OrderItem`, `OrderStatus`, `ORDER_STATUSES` |
| `app/modules/orders/schemas.py` | `OrderItemRead`, `OrderRead` |
| `alembic/env.py` | imports the two new models |
| `alembic/versions/..._add_orders_and_order_items.py` | the migration |

`OrderRead.from_order()` is written out by hand because the eight shipping columns are flat on
the table and nested under `shipping` in the API. An explicit function reading
`order.shipping_city` is easier to follow than a validator that rearranges fields invisibly.

`OrderItemRead.line_total` is **computed**, not stored — both inputs are frozen snapshots, so it
can only ever give the same answer. `Order.total_amount` is the opposite case.

#### Verification

Autogenerate rendered both check constraints, because this is a `create_table` path rather than
the `add_column` path that silently dropped one in Step 32. `alembic check` afterwards: *No new
upgrade operations detected.*

10 of 10 behavioural assertions against the applied schema:

| Case | Result |
|---|---|
| status `'refunded'` | refused — `ck_orders_status_is_known` |
| `total_amount` −1 | refused — `ck_orders_total_not_negative` |
| an order with one line | created, total 39.98 |
| a second line for the same product | refused — `uq_order_items_order_id_product_id` |
| a line of quantity 0 | refused — `ck_order_items_quantity_is_positive` |
| deleting the customer who ordered | refused — RESTRICT on `fk_orders_user_id_users` |
| deleting the product that was sold | refused — RESTRICT on `fk_order_items_product_id_products` |
| `OrderRead` shipping | nested, eight fields |
| `OrderRead` | no `user_id` |
| `line_total` | 39.98, computed |

Ruff clean; no test data left behind.

Note for reading `\d orders`: PostgreSQL rewrites `status IN (...)` into
`status::text = ANY (ARRAY[...])` when it stores the constraint. It means the same thing.

#### Risk & Controls Note

- **Regulatory / data protection:** This step **creates a second store of personal data**.
  Recipient name, phone and full address now live in `orders` as well as `addresses`, and the
  RESTRICT above means a customer with orders cannot be deleted at all — demonstrated, not
  assumed. That is correct for a financial record under commercial and tax retention, but it
  converts the Step 43 item from a design note into a live obligation: an erasure request can no
  longer be satisfied by deleting rows, so a documented retention basis and an erasure procedure
  that distinguishes order data from address-book data are now required.
- **Security:** `OrderRead` omits `user_id`, as `AddressRead` does. No endpoints exist yet, so
  there is no access path to review — ownership scoping on order reads is Step 51 and must not
  be skipped, since order ids are sequential and an unscoped `GET /orders/{id}` is a textbook
  IDOR.
- **Data residency / cross-border:** Widened as predicted in Step 43. Any residency assessment,
  backup scope, replica or analytics export must now cover `orders` and `order_items`.
  `order_items` also holds purchase history, which is behavioural data about a person and is
  often more sensitive in aggregate than a single address.
- **Required controls / approvals:** Retention policy with its statutory basis, before
  production. Encryption at rest and log masking now apply to two more tables. New item: **the
  schema assumes a single currency** — no currency column on `products` or `orders` — which is a
  real constraint for a KSA/UAE/Bahrain footprint and must be decided before launch rather than
  retrofitted across stored totals.
- **Residual risk:** **Medium**, up from Low, and the increase is the point: data is now stored
  that deletion will not reach. The schema is sound; the risk is the policy gap it makes
  concrete.

#### Open items added

- A customer with orders cannot be deleted. Erasure now requires a documented procedure that
  separates order data from address-book data; deleting rows is no longer an option.
- Single-currency assumption, undeclared anywhere in the schema. Decide before launch.

### ✅ Step 46 — Immutable Order-Item Snapshots

**Completed:** 2026-10-31 · One migration, applied. Still no endpoints — checkout is Step 47.

#### Objective

Step 45 created columns called `sku`, `name` and `unit_price` on `order_items`. Nothing yet
filled them, and nothing stopped anyone changing them afterwards. This step does both, so that
*immutable* describes the database rather than an intention.

#### Decisions

**The copy happens in the service, not the repository.** Deciding *which* price is frozen is a
business rule; writing rows is not. `build_order` takes products the caller has already locked
and returns an unsaved `Order`, so Step 47 keeps control of the transaction. A function that
fetched its own products would be reading them unlocked — the staleness Step 44 ruled out.

**The total is summed from the copies.**

```python
total = sum((item.unit_price * item.quantity for item in items), Decimal("0.00"))
```

Not from `product.price` a second time. Reading the live price again would let the total
disagree with the lines it is supposed to be the sum of. The `Decimal("0.00")` start value
matters as well: bare `sum()` begins at integer `0` and mixes an `int` into money arithmetic.

**The repository has no update function for order lines**, because there should be no way to
change one at all. A mistake on an order is corrected by a new record, not by rewriting the old
one.

**A database trigger, chosen over application-level discipline alone.** The repository binds
only this application; a stray `UPDATE` in `psql`, or a future developer adding a setter, would
silently rewrite a financial record.

```sql
CREATE TRIGGER order_items_no_update
    BEFORE UPDATE ON order_items
    FOR EACH ROW EXECUTE FUNCTION order_items_are_immutable();
```

`BEFORE UPDATE`, so nothing is written when it raises. `ERRCODE = 'restrict_violation'` gives it
SQLSTATE `23001` instead of the generic `P0001`, so code can recognise it rather than matching
on message text.

**`UPDATE` only, not `DELETE`.** Covering `DELETE` would break the `ON DELETE CASCADE` from
`orders` and make an order impossible to remove at all. Deleting a whole order is a different
decision from rewriting one: it leaves nothing behind that could mislead, while a rewritten line
leaves an invoice that lies.

#### Files added or changed

| File | Change |
|---|---|
| `app/modules/orders/service.py` | `build_order` |
| `app/modules/orders/repository.py` | `add` |
| `alembic/versions/..._make_order_items_immutable.py` | the trigger and its function |

#### Verification

12 of 12 against the live database. An order was placed for two products, then the shop renamed,
re-SKU'd, repriced and deactivated both:

| Case | Result |
|---|---|
| total summed from the copies | 2 × 19.99 + 3 × 5.50 = **56.48** |
| after the products changed — line name | still `Blue Mug` |
| — unit price | still `19.99` |
| — SKU | still `S46-A` |
| — the discontinued product's line | still `Red Mug` |
| — the total | still `56.48` |
| the live product meanwhile | `Mug, Azure (2027 range)` at `29.99` |
| `UPDATE order_items SET unit_price = 0.01` | refused — *order_items row 4 cannot be changed once written* |
| its SQLSTATE | `23001` |
| the same change through the ORM | refused by the same trigger |
| `DELETE FROM orders` | cascaded; 0 lines left |

That last row is the one that would have failed had the trigger covered `DELETE` too.

`alembic check`: *No new upgrade operations detected.* Ruff clean; no test data left behind.

#### A limitation worth knowing

**Alembic cannot see the trigger.** Autogenerate and `alembic check` compare tables, columns,
indexes and constraints — not functions or triggers. If someone drops this trigger, nothing in
the project detects it, and `alembic check` will keep reporting that everything is in order. The
same blind-spot family as the `CheckConstraint` Step 32 silently omitted, and the reason the
verification above exercises the behaviour rather than inspecting the schema.

#### Risk & Controls Note

- **Regulatory / data protection:** This is the step that makes order records defensible. A
  financial record that can be edited in place is not evidence of anything, and the demonstration
  above — price changed on the product, unchanged on the order, direct `UPDATE` refused — is the
  kind of evidence an audit asks for. It does **not** amount to an audit trail: nothing records
  *who* created an order or *what was attempted*. That remains Step 60 and is now more clearly
  needed, since the trigger produces a refusal that nobody is logging.
- **Security:** Narrows the blast radius of a compromised application credential. Application
  code can no longer alter a price after the fact, so an attacker with the app's database user
  cannot quietly rewrite what was charged — they would have to drop the trigger, which is a
  louder, separately-privileged act. A production role for the application should therefore
  **not** hold the rights to drop triggers or functions; that is a least-privilege control to
  apply before launch, not a default.
- **Data residency / cross-border:** Unchanged by this step.
- **Required controls / approvals:** Database migration privileges should be separated from
  application runtime privileges, so the role that can drop this trigger is not the role the API
  runs as. Trigger existence should be monitored, since Alembic will not notice its absence. Both
  carried forward.
- **Residual risk:** **Low** for this step, which only removes a capability. The project's
  standing Medium from Step 45 — personal data that deletion will not reach — is untouched.

#### Open items added

- Alembic does not track triggers or functions; a dropped `order_items_no_update` would go
  undetected. Needs either a monitoring check or a startup assertion.
- The application's runtime database role should not be able to drop triggers. Least-privilege
  separation from the migration role, before production.
- The trigger raises on a rewrite attempt and nothing logs it. Ties into Step 60.

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
