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
| **Current step** | **Step 13 — Pydantic schemas for products** (Steps 1–12 complete) |
| **Phases complete** | 2 of 12 |
| **Steps complete** | 12 of 74 |

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
| 13 | Pydantic request/response schemas | 🔵 |
| 14 | Product repository | ⬜ |
| 15 | Product service and business rules | ⬜ |
| 16 | FastAPI routes with dependency injection | ⬜ |
| 17 | Create, list, get-by-ID, update, delete endpoints | ⬜ |
| 18 | Pagination, filtering, sorting, search, validation | ⬜ |
| 19 | Explain full request lifecycle with a real product request | ⬜ |

### Phase 4 — Categories and Relationships

| # | Step | Status |
|---|---|---|
| 20 | Implement categories | ⬜ |
| 21 | Product–category relationships | ⬜ |
| 22 | Explain FKs, relationship loading, lazy vs eager, N+1 | ⬜ |
| 23 | Constraints and indexes | ⬜ |

### Phase 5 — Users and Authentication

| # | Step | Status |
|---|---|---|
| 24 | User model and migration | ⬜ |
| 25 | Registration and password hashing | ⬜ |
| 26 | Login | ⬜ |
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
