from fastapi import HTTPException, Request, Response, status

from src.core.logger import logger
from src.schemas.auth import LoginSchema, Token
from src.services.user_service import UserService
from src.utils.google_oauth import exchange_code_for_token, get_google_user_info
from src.utils.security import (
    clear_refresh_token_cookie,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    set_refresh_token_cookie,
    verify_password,
)


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def login(self, data: LoginSchema, response: Response) -> Token:
        user = await self.user_service.get_user_by_username(data.username)

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = create_access_token({"sub": str(user.id), "role": user.role.name})

        refresh_token = create_refresh_token({"sub": str(user.id)})

        set_refresh_token_cookie(response, refresh_token)

        return Token(access_token=access_token)

    async def refresh(self, request: Request, response: Response) -> Token:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token",
            )

        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        user = await self.user_service.user_repo.get_user_with_role(int(user_id))  # type: ignore
        if not user:
            raise HTTPException(404)

        new_access = create_access_token({"sub": str(user.id), "role": user.role.name})

        new_refresh = create_refresh_token({"sub": str(user.id)})

        set_refresh_token_cookie(response, new_refresh)

        return Token(access_token=new_access)

    async def logout(self, response: Response) -> dict[str, str]:
        clear_refresh_token_cookie(response)
        return {"message": "Successfully logged out"}

    async def google_auth(self, code: str, response: Response) -> Token:
        logger.info("Starting Google OAuth authentication")

        token_data = await exchange_code_for_token(code)
        google_access_token = token_data["access_token"]

        user_info = await get_google_user_info(google_access_token)

        google_id = user_info["sub"]
        email = user_info["email"]
        name = str(user_info.get("name"))

        user = await self.user_service.get_by_google_id(google_id)

        if not user:
            user = await self.user_service.get_by_email(email)

            if user:
                if not user.google_id:
                    logger.info("Attaching google_id to existing user")
                    user = await self.user_service.attach_google_account(
                        user=user,
                        google_id=google_id,
                    )
            else:
                logger.info("Creating new Google user")
                user = await self.user_service.create_google_user(
                    email=email,
                    google_id=google_id,
                    name=name,
                )

        access_token = create_access_token({"sub": str(user.id), "role": "user"})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        set_refresh_token_cookie(response, refresh_token)

        logger.info("Google OAuth success for user_id=%s", user.id)

        return Token(access_token=access_token)
