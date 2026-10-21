"""The categories table."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(Base):
    # The real table name in PostgreSQL. Plural by convention.
    __tablename__ = "categories"

    # Mapped[int] tells SQLAlchemy the Python type, mapped_column() describes
    # the database column. primary_key=True also makes PostgreSQL generate
    # the value, so we never set id ourselves.
    id: Mapped[int] = mapped_column(primary_key=True)

    # String(100) becomes VARCHAR(100). unique=True adds a constraint, so
    # the database itself rejects a duplicate name even if our code misses it.
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # server_default=func.now() means PostgreSQL fills this in on INSERT.
    # timezone=True stores the offset, so times stay correct across regions.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
