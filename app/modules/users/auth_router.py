"""Sign-in endpoint.

Separate from the users router because signing in is not creating or
reading a user resource; it is an action on credentials.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.db.session import DbSession
from app.modules.users import service
from app.modules.users.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Sign in")
def login(data: LoginRequest, db: DbSession) -> TokenResponse:
    """Check the credentials and return an access token."""
    try:
        user = service.authenticate_user(db, data.email, data.password)
        return TokenResponse(access_token=create_access_token(user.id))
    except AuthenticationError as exc:
        # 401 Unauthorized. WWW-Authenticate tells a client what scheme to
        # use; it becomes meaningful once tokens arrive in Step 27.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
