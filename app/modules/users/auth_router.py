"""Sign-in endpoint.

Separate from the users router because signing in is not creating or
reading a user resource; it is an action on credentials.
"""

from fastapi import APIRouter

from app.core.security import create_access_token
from app.db.session import DbSession
from app.modules.users import service
from app.modules.users.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Sign in")
def login(data: LoginRequest, db: DbSession) -> TokenResponse:
    """Check the credentials and return an access token."""
    user = service.authenticate_user(db, data.email, data.password)
    return TokenResponse(access_token=create_access_token(user.id))
