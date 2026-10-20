"""The base class that every database model inherits from."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Gives indexes, constraints and foreign keys predictable names.
# Without this PostgreSQL invents its own names, and migrations cannot
# reliably undo them later. Worth setting before the first model exists.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """All models inherit from this class."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
