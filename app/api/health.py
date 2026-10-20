"""Health endpoints, used by Docker and load balancers to check the app.

/health       - is the app running?
/health/ready - is the app running AND able to reach the database?
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import DbSession

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"


class ReadinessResponse(BaseModel):
    status: str = "ready"


@router.get("/health", summary="Is the app running?")
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/health/ready", summary="Is the database reachable?")
def readiness(db: DbSession) -> ReadinessResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Keep the message vague: database errors reveal host names,
        # table names and other details a client should not see.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready",
        ) from exc
    return ReadinessResponse()
