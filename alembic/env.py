"""Tells Alembic how to reach the database and what the models look like.

Two changes from the file Alembic generated:

1. The database URL comes from app settings, so no password is written into
   alembic.ini - that file IS committed to git.
2. target_metadata points at our Base, so `alembic revision --autogenerate`
   can compare the models against the real database.
"""

from logging.config import fileConfig

from alembic import context
from app.core.config import get_settings
from app.db.base import Base

# Importing a model module registers its table on Base.metadata.
# EVERY new model must be added here, or autogenerate will not see it and
# will quietly produce an empty migration.
from app.modules.addresses.models import Address  # noqa: F401
from app.modules.cart.models import Cart, CartItem  # noqa: F401
from app.modules.categories.models import Category  # noqa: F401
from app.modules.orders.models import Order, OrderItem  # noqa: F401
from app.modules.products.models import Product  # noqa: F401
from app.modules.users.models import User  # noqa: F401
from sqlalchemy import create_engine, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

database_url = get_settings().database_url


def run_migrations_offline() -> None:
    """Print the SQL instead of running it. Useful for review by a DBA."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and apply the migrations."""
    # NullPool: a migration command is short-lived, so pooling gains nothing.
    engine = create_engine(database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
