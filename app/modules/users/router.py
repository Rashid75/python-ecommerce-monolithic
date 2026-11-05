"""HTTP endpoints for users."""

from fastapi import APIRouter, status

from app.db.session import DbSession
from app.modules.users import service
from app.modules.users.dependencies import CurrentUser
from app.modules.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", summary="The signed-in account")
def read_me(user: CurrentUser) -> UserRead:
    """Protected: the CurrentUser dependency rejects the request with 401
    before this function runs unless a valid token was sent."""
    return user


@router.post("", status_code=status.HTTP_201_CREATED, summary="Register a new account")
def register(data: UserCreate, db: DbSession) -> UserRead:
    return service.register_user(db, data)
