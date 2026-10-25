"""The categories table."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    # Imported only for type checking. A real import here and in products
    # would be circular, since each model refers to the other.
    from app.modules.products.models import Product


class Category(Base):
    # The real table name in PostgreSQL. Plural by convention.
    __tablename__ = "categories"

    # Mapped[int] tells SQLAlchemy the Python type, mapped_column() describes
    # the database column. primary_key=True also makes PostgreSQL generate
    # the value, so we never set id ourselves.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Uniqueness is enforced by the case-insensitive index in __table_args__,
    # not by unique=True here. unique=True would let "Books" and "books" both
    # exist, which is a duplicate to everyone except the database.
    name: Mapped[str] = mapped_column(String(100))

    # server_default=func.now() means PostgreSQL fills this in on INSERT.
    # timezone=True stores the offset, so times stay correct across regions.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # The other half of the link. Lets you write category.products in Python.
    # It adds no column: the foreign key lives on products.
    #
    # passive_deletes="all" is essential here. By default, deleting a category
    # makes SQLAlchemy load its products and set their category_id to NULL
    # before issuing the DELETE - so PostgreSQL never sees a violation and the
    # ON DELETE RESTRICT is silently bypassed. "all" tells SQLAlchemy to leave
    # the children alone and let the database decide.
    products: Mapped[list["Product"]] = relationship(
        back_populates="category", passive_deletes="all"
    )

    __table_args__ = (
        # A unique index on lower(name), so Books / books / BOOKS collide.
        # Given an explicit name because the naming convention cannot build
        # one for an index on an expression rather than a plain column.
        Index("uq_categories_lower_name", func.lower(name), unique=True),
    )
