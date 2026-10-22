"""HTTP endpoints for products.

The only layer that knows about HTTP. It reads the request, calls the
service, and turns application errors into status codes. No business rules
and no database queries live here.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.db.session import DbSession
from app.modules.products import service
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", summary="List products")
def list_products(
    db: DbSession,
    # Query(...) turns these into ?limit=&offset= with validation attached.
    # The upper bound on limit stops a client asking for a million rows.
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ProductRead]:
    return list(service.list_products(db, limit=limit, offset=offset))


@router.get("/{product_id}", summary="Get one product")
def get_product(product_id: int, db: DbSession) -> ProductRead:
    try:
        return service.get_product(db, product_id)
    except NotFoundError as exc:
        # The service says what went wrong; the router decides that it is a
        # 404. Step 59 moves this mapping into one place for every endpoint.
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


# 201 Created is the correct status for a POST that makes a new thing.
# FastAPI would otherwise return 200.
@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a product")
def create_product(data: ProductCreate, db: DbSession) -> ProductRead:
    try:
        return service.create_product(db, data)
    except AlreadyExistsError as exc:
        # 409 Conflict, not 400: the request is well formed, it just clashes
        # with something that already exists.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


# PATCH, not PUT: the client sends only the fields it wants to change.
# PUT would mean "replace the whole product with this".
@router.patch("/{product_id}", summary="Update a product")
def update_product(product_id: int, data: ProductUpdate, db: DbSession) -> ProductRead:
    try:
        return service.update_product(db, product_id, data)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


# 204 No Content: it worked and there is nothing to send back.
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a product")
def delete_product(product_id: int, db: DbSession) -> None:
    try:
        service.delete_product(db, product_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
