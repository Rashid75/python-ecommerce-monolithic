"""Application entry point.

Run with:
    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import RequestContextMiddleware, configure_logging
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

settings = get_settings()

# Before the app is built, so anything logged during startup is already
# in the right shape.
configure_logging(settings.log_level)

# The interactive docs list every endpoint and schema, so they are switched
# off in production by passing None instead of a path.
docs = None if settings.is_production else "/docs"
redoc = None if settings.is_production else "/redoc"
openapi = None if settings.is_production else "/openapi.json"

app = FastAPI(
    title=settings.name,
    debug=settings.debug,
    docs_url=docs,
    redoc_url=redoc,
    openapi_url=openapi,
)

# Middleware runs in reverse registration order, so the LAST one added is
# the outermost. The request id must be set before anything else can log,
# so it is added last and sees every request first.
#
# Browsers only. Empty origins means no cross-origin page may read a
# response, which is the default and the right one for an API whose
# clients are servers and mobile apps.
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )

app.add_middleware(SecurityHeadersMiddleware, production=settings.is_production)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestContextMiddleware)

# Every application error becomes an HTTP response in one place, so no
# router has to know what a 404 is.
register_exception_handlers(app)

# Health probes stay at the root, outside the version prefix: infrastructure
# should not have to change when the API version does.
app.include_router(health_router)

# Everything else lives under /api/v1.
app.include_router(api_router, prefix=settings.api_v1_prefix)
