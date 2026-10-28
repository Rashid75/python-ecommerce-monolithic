"""Turning a bearer token into the User it belongs to.

Any module that needs a signed-in user imports CurrentUser from here.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import DbSession
from app.modules.users import repository as repo
from app.modules.users.models import ROLE_ADMIN, User

# Reads the Authorization: Bearer <token> header. auto_error=False so a
# missing header reaches our code: FastAPI's built-in error for this is a
# 403, and "you did not sign in" is a 401.
_bearer = HTTPBearer(auto_error=False)

# One message for every reason. A caller should not learn whether a token
# was missing, malformed, expired, or belonged to a deleted account.
_NOT_AUTHENTICATED = "Not authenticated"


def _unauthorised() -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        _NOT_AUTHENTICATED,
        # Tells the client which scheme to use when it retries.
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """Return the signed-in user, or raise 401."""
    if credentials is None:
        raise _unauthorised()

    try:
        user_id = decode_access_token(credentials.credentials)
    except AuthenticationError as exc:
        raise _unauthorised() from exc

    # Look the user up on every request rather than trusting the token
    # alone. The token proves who signed in; the database decides whether
    # that account may still act. Without this, a deleted or disabled
    # account would keep working until its token expired - the closest
    # thing to revocation this design has.
    user = repo.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise _unauthorised()

    return user


# Lets an endpoint write `user: CurrentUser` and be protected by it.
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    """Allow only administrators through.

    401 and 403 are different answers. 401 means "I do not know who you
    are" - sign in and try again. 403 means "I know exactly who you are and
    you still may not do this", so retrying with the same account is
    pointless. Returning 401 here would tell an administrator to sign in
    again when they already had.
    """
    if user.role != ROLE_ADMIN:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Administrator access required",
        )
    return user


# For an endpoint that needs the administrator object.
AdminUser = Annotated[User, Depends(require_admin)]
