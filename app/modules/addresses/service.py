"""Business rules for addresses. The only layer that commits.

Every function takes the user id. There is no way to ask for an address
without saying whose it is.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.addresses import repository as repo
from app.modules.addresses.models import MAX_ADDRESSES_PER_USER, Address
from app.modules.addresses.schemas import AddressCreate, AddressUpdate
from app.modules.users.models import User


def _lock_address_book(db: Session, user_id: int) -> None:
    """Serialise this customer's address changes.

    The thing being protected is "this customer's address book", and the
    users row is the only row that always exists to stand for it. Without
    this, two requests could both decide to become the default, both clear
    the old one, and the partial unique index would turn the loser into a
    500 instead of a sensible result.

    Only address writes take this lock, so it serialises nothing else.
    """
    db.execute(select(User.id).where(User.id == user_id).with_for_update())


def list_addresses(db: Session, user_id: int) -> Sequence[Address]:
    return repo.list_for_user(db, user_id)


def get_address(db: Session, user_id: int, address_id: int) -> Address:
    """One address, or 404.

    404 rather than 403 for someone else's address. A 403 would confirm
    that the address exists, turning this endpoint into a way to discover
    which ids are real. 404 says only "not yours or not there".
    """
    address = repo.get_for_user(db, user_id, address_id)
    if address is None:
        raise NotFoundError(f"Address {address_id} does not exist")
    return address


def create_address(db: Session, user_id: int, data: AddressCreate) -> Address:
    _lock_address_book(db, user_id)

    existing = repo.count_for_user(db, user_id)
    if existing >= MAX_ADDRESSES_PER_USER:
        db.rollback()
        raise ValidationError(f"You cannot keep more than {MAX_ADDRESSES_PER_USER} addresses")

    # The first address is the default whatever the request said. A customer
    # with addresses but no default is a state checkout would have to cope
    # with for no reason.
    make_default = data.is_default or existing == 0
    if make_default:
        repo.clear_default(db, user_id)

    address = Address(**(data.model_dump() | {"user_id": user_id, "is_default": make_default}))
    repo.add(db, address)
    db.commit()
    return address


def update_address(db: Session, user_id: int, address_id: int, data: AddressUpdate) -> Address:
    _lock_address_book(db, user_id)
    address = repo.get_for_user(db, user_id, address_id)
    if address is None:
        db.rollback()
        raise NotFoundError(f"Address {address_id} does not exist")

    changes = data.model_dump(exclude_unset=True)

    if changes.get("is_default") is True:
        repo.clear_default(db, user_id, except_id=address_id)
    elif changes.get("is_default") is False and address.is_default:
        # Refused rather than obeyed. Clearing the only default would leave
        # the customer with addresses and none chosen; choosing a different
        # one is how you stop this being the default.
        db.rollback()
        raise ValidationError("Make another address the default instead of unsetting this one")

    for field, value in changes.items():
        setattr(address, field, value)
    db.commit()
    return address


def delete_address(db: Session, user_id: int, address_id: int) -> None:
    _lock_address_book(db, user_id)
    address = repo.get_for_user(db, user_id, address_id)
    if address is None:
        db.rollback()
        raise NotFoundError(f"Address {address_id} does not exist")

    was_default = address.is_default
    repo.remove(db, address)
    db.flush()

    # Promote the oldest survivor, so "if you have addresses, one of them is
    # the default" stays true without the customer having to think about it.
    if was_default:
        remaining = repo.list_for_user(db, user_id)
        if remaining:
            remaining[0].is_default = True
    db.commit()
