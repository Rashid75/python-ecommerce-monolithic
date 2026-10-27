"""HTTP endpoints for users."""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import AlreadyExistsError
from app.db.session import DbSession
from app.modules.users import service
from app.modules.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Register a new account")
def register(data: UserCreate, db: DbSession) -> UserRead:
    try:
        return service.register_user(db, data)
    except AlreadyExistsError as exc:
        # Note: replying 409 confirms that an address is registered, which
        # lets someone test whether a person has an account here. The usual
        # fix is to always return 201 and send an email instead. Kept simple
        # for now; rate limiting in Step 63 is the partial mitigation.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
