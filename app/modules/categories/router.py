"""HTTP endpoints for categories."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.common.schemas import Page
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.db.session import DbSession
from app.modules.categories import service
from app.modules.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


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
    try:
        return service.get_category(db, category_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a category")
def create_category(data: CategoryCreate, db: DbSession) -> CategoryRead:
    try:
        return service.create_category(db, data)
    except AlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.patch("/{category_id}", summary="Update a category")
def update_category(category_id: int, data: CategoryUpdate, db: DbSession) -> CategoryRead:
    try:
        return service.update_category(db, category_id, data)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except AlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.delete(
    "/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category"
)
def delete_category(category_id: int, db: DbSession) -> None:
    try:
        service.delete_category(db, category_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
