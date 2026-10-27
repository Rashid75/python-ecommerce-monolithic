"""Business rules for users. The only layer that commits."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.core.security import hash_password
from app.modules.users import repository as repo
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


def get_user(db: Session, user_id: int) -> User:
    user = repo.get_by_id(db, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} does not exist")
    return user


def register_user(db: Session, data: UserCreate) -> User:
    """Create an account, storing only the hash of the password."""
    user = User(
        email=data.email,
        # The plaintext goes no further than this line.
        password_hash=hash_password(data.password),
    )
    try:
        repo.add(db, user)
        db.commit()
    except IntegrityError as exc:
        # Same reasoning as products and categories: let the unique index
        # decide, rather than checking first and leaving a gap that two
        # simultaneous registrations could both pass through.
        db.rollback()
        raise AlreadyExistsError("That email address is already registered") from exc
    return user
