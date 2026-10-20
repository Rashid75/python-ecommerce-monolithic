"""Database engine, session factory, and the session dependency."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# One engine for the whole application. It keeps a pool of open connections
# and every request borrows one from it.
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    # Check a pooled connection still works before handing it out.
    pool_pre_ping=True,
    # Give up after 5 seconds instead of waiting forever when the
    # database is unreachable.
    connect_args={"connect_timeout": 5},
)

# expire_on_commit=False keeps objects readable after commit(). With the
# default, FastAPI hits an error while converting them to JSON.
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Give a request its own session and close it when the request ends."""
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()


# Lets a route write `db: DbSession` instead of the longer Depends() form.
DbSession = Annotated[Session, Depends(get_db)]
