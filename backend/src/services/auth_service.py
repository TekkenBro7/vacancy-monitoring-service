from fastapi import HTTPException, status

from src.schemas.auth import LoginSchema, Token
from src.services.user_service import UserService
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def login(self, data: LoginSchema) -> Token:
        user = await self.user_service.get_user_by_username(data.username)

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = create_access_token({"sub": str(user.id), "role": user.role.name})

        refresh_token = create_refresh_token({"sub": str(user.id)})

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> Token:
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, e) from e

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token: no subject")

        user = await self.user_service.user_repo.get_by_id(int(user_id))

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        new_access = create_access_token({"sub": str(user.id), "role": user.role})

        new_refresh = create_refresh_token({"sub": str(user.id)})

        return Token(access_token=new_access, refresh_token=new_refresh)
