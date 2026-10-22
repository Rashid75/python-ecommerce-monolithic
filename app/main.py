"""Application entry point.

Run with:
    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

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

# Health probes stay at the root, outside the version prefix: infrastructure
# should not have to change when the API version does.
app.include_router(health_router)

# Everything else lives under /api/v1.
app.include_router(api_router, prefix=settings.api_v1_prefix)
