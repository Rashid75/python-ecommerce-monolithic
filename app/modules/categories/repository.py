"""Database queries for categories. No business rules, no HTTP."""

from collections.abc import Sequence

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.modules.categories.models import Category


def get_by_id(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    """Case-insensitive, matching how uniqueness is enforced."""
    return db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))


def _filters(search: str | None) -> list[ColumnElement[bool]]:
    """Conditions shared by the list and count queries, so the two agree."""
    if not search:
        return []
    return [Category.name.ilike(f"%{search}%")]


def list_categories(
    db: Session, *, limit: int = 20, offset: int = 0, search: str | None = None
) -> Sequence[Category]:
    stmt = (
        select(Category)
        .where(*_filters(search))
        .order_by(Category.name, Category.id)
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


def count_categories(db: Session, *, search: str | None = None) -> int:
    stmt = select(func.count()).select_from(Category).where(*_filters(search))
    return db.scalar(stmt) or 0


def add(db: Session, category: Category) -> Category:
    db.add(category)
    db.flush()
    return category


def remove(db: Session, category: Category) -> None:
    db.delete(category)
