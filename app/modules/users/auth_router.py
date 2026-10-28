"""Sign-in endpoint.

Separate from the users router because signing in is not creating or
reading a user resource; it is an action on credentials.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import AuthenticationError
from app.db.session import DbSession
from app.modules.users import service
from app.modules.users.schemas import LoginRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Sign in")
def login(data: LoginRequest, db: DbSession) -> UserRead:
    """Check the credentials and return the account.

    Step 27 replaces this response with an access token. Returning the user
    now keeps this step to one idea: verifying a password safely.
    """
    try:
        return service.authenticate_user(db, data.email, data.password)
    except AuthenticationError as exc:
        # 401 Unauthorized. WWW-Authenticate tells a client what scheme to
        # use; it becomes meaningful once tokens arrive in Step 27.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
