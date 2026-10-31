"""HTTP endpoints for a customer's own addresses.

The address id is in the path, unlike the cart, because a customer has
many addresses and must be able to name one. The protection is therefore
scoping rather than absence: every query filters on the authenticated
user, so another customer's id matches nothing.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import DbSession
from app.modules.addresses import service
from app.modules.addresses.schemas import AddressCreate, AddressRead, AddressUpdate
from app.modules.users.dependencies import CurrentUser

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", summary="List my addresses")
def list_addresses(user: CurrentUser, db: DbSession) -> list[AddressRead]:
    # No Page envelope here: the list is capped at 20 by
    # MAX_ADDRESSES_PER_USER, so paging it would be ceremony.
    return [AddressRead.model_validate(a) for a in service.list_addresses(db, user.id)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Add an address")
def create_address(data: AddressCreate, user: CurrentUser, db: DbSession) -> AddressRead:
    try:
        return service.create_address(db, user.id, data)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.get("/{address_id}", summary="Get one of my addresses")
def get_address(address_id: int, user: CurrentUser, db: DbSession) -> AddressRead:
    try:
        return service.get_address(db, user.id, address_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.patch("/{address_id}", summary="Update one of my addresses")
def update_address(
    address_id: int, data: AddressUpdate, user: CurrentUser, db: DbSession
) -> AddressRead:
    try:
        return service.update_address(db, user.id, address_id, data)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.delete(
    "/{address_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete one of my addresses"
)
def delete_address(address_id: int, user: CurrentUser, db: DbSession) -> None:
    try:
        service.delete_address(db, user.id, address_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
