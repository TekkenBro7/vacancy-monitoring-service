from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.users import UserMe
from src.services.user_service import UserService
from src.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> UserMe:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token: no subject"
            )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    user_service = UserService(db)
    user = await user_service.get_user_me(int(user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserMe.model_validate(user)


async def validate_access_token(
    token: str = Depends(oauth2_scheme),
) -> dict[str, Any]:
    try:
        payload = decode_access_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


async def require_admin(current_user: UserMe = Depends(get_current_user)) -> UserMe:
    if current_user.role_name.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
