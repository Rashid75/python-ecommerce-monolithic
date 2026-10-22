"""Business rules for categories. The only layer that commits."""

from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.modules.categories import repository as repo
from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Category:
    category = repo.get_by_id(db, category_id)
    if category is None:
        raise NotFoundError(f"Category {category_id} does not exist")
    return category


def list_categories(
    db: Session, *, limit: int = 20, offset: int = 0, search: str | None = None
) -> tuple[Sequence[Category], int]:
    items = repo.list_categories(db, limit=limit, offset=offset, search=search)
    total = repo.count_categories(db, search=search)
    return items, total


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    try:
        repo.add(db, category)
        db.commit()
    except IntegrityError as exc:
        # Same reasoning as products: let the unique constraint decide rather
        # than checking first, which two simultaneous requests could both pass.
        db.rollback()
        raise AlreadyExistsError(f"Category {data.name} already exists") from exc
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AlreadyExistsError(f"Category {data.name} already exists") from exc
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    repo.remove(db, category)
    db.commit()
