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
    # Spelled out in the Step 64 review rather than left to defaults,
    # because the numbers interact with things this application does.
    #
    # Checkout holds row locks for the length of its transaction, so a
    # slow checkout occupies a connection as well as a lock. 5 + 10 is
    # SQLAlchemy's default and is kept, but now visibly: raising it without
    # also raising PostgreSQL's max_connections (100 by default, shared by
    # every process) trades one queue for another.
    pool_size=5,
    max_overflow=10,
    # Wait this long for a free connection before failing. Without it the
    # default is 30s, which turns a busy moment into a pile of requests
    # all holding client sockets open.
    pool_timeout=10,
    # Recycle connections every half hour. Idle connections get closed by
    # firewalls and database restarts; pre_ping catches that, and recycling
    # means it happens far less often.
    pool_recycle=1800,
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
