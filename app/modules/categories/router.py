"""HTTP endpoints for categories."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas import Page
from app.db.session import DbSession
from app.modules.categories import service
from app.modules.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.modules.users.dependencies import require_admin

router = APIRouter(prefix="/categories", tags=["categories"])

# Writes are administrator-only; reading the category list stays open.
requires_admin = [Depends(require_admin)]


@router.get("", summary="List categories")
def list_categories(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    search: Annotated[str | None, Query(max_length=100)] = None,
) -> Page[CategoryRead]:
    items, total = service.list_categories(db, limit=limit, offset=offset, search=search)
    return Page[CategoryRead](
        items=[CategoryRead.model_validate(c) for c in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{category_id}", summary="Get one category")
def get_category(category_id: int, db: DbSession) -> CategoryRead:
    return service.get_category(db, category_id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
    dependencies=requires_admin,
)
def create_category(data: CategoryCreate, db: DbSession) -> CategoryRead:
    return service.create_category(db, data)


@router.patch("/{category_id}", summary="Update a category", dependencies=requires_admin)
def update_category(category_id: int, data: CategoryUpdate, db: DbSession) -> CategoryRead:
    return service.update_category(db, category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    dependencies=requires_admin,
)
def delete_category(category_id: int, db: DbSession) -> None:
    service.delete_category(db, category_id)
