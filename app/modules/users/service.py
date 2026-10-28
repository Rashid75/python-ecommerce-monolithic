"""Business rules for users. The only layer that commits."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, AuthenticationError, NotFoundError
from app.core.security import hash_password, verify_password
from app.modules.users import repository as repo
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate

# One message for every failure. See AuthenticationError.
_SIGN_IN_FAILED = "Incorrect email or password"

# Hashing is slow on purpose, so a request that skips it finishes noticeably
# sooner. If an unknown email returned immediately, the response time alone
# would reveal which addresses are registered. Verifying against this
# throwaway hash instead keeps both paths the same length.
_DUMMY_HASH = hash_password("a-password-that-belongs-to-nobody")


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


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Return the user if the credentials are right, otherwise raise.

    Every failure raises the same error with the same message. Telling the
    caller that the email was fine but the password was wrong would confirm
    that the address has an account here.
    """
    user = repo.get_by_email(db, email)

    if user is None:
        # Spend the same time as a real check before failing.
        verify_password(password, _DUMMY_HASH)
        raise AuthenticationError(_SIGN_IN_FAILED)

    if not verify_password(password, user.password_hash):
        raise AuthenticationError(_SIGN_IN_FAILED)

    if not user.is_active:
        # Also generic: a disabled account should not be distinguishable
        # from a wrong password by someone probing from outside.
        raise AuthenticationError(_SIGN_IN_FAILED)

    return user
