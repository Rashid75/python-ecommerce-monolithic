"""HTTP endpoints for products.

The only layer that knows about HTTP. It reads the request, calls the
service, and turns application errors into status codes. No business rules
and no database queries live here.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import NotFoundError
from app.db.session import DbSession
from app.modules.products import service
from app.modules.products.schemas import ProductRead

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
