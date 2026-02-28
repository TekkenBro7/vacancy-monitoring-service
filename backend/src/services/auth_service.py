import json

from fastapi import HTTPException, Request, Response, status

from src.core.constants import EMAIL_VERIFICATION_CODE_TTL
from src.core.enums import VerificationPurpose
from src.core.logger import logger
from src.core.redis_client import redis_client
from src.mail.services.email_verification_service import EmailVerificationService
from src.schemas.auth import LoginSchema, Token
from src.schemas.common import MessageResponse
from src.schemas.users import UserCreate
from src.services.user_service import UserService
from src.utils.google_oauth import exchange_code_for_token, get_google_user_info
from src.utils.redis_keys import RedisKeys
from src.utils.security import (
    clear_refresh_token_cookie,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
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

    async def google_auth(self, code: str, response: Response) -> tuple[Token, str]:
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

        logger.info("Google OAuth success for user_id=%s", user.id)

        return Token(access_token=access_token), refresh_token

    async def send_code(
        self,
        email: str,
        purpose: VerificationPurpose,
        password: str | None = None,
        username: str | None = None,
    ) -> MessageResponse:
        logger.info(
            "AuthService.send_code email=%s purpose=%s",
            email,
            purpose,
        )

        pending_key = RedisKeys.pending(email, purpose)

        if purpose == VerificationPurpose.REGISTER:
            if not password:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password required")

            if not username:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username required")

            existing = await self.user_service.get_by_email(email)

            if existing:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")

            hashed = hash_password(password)

            await redis_client.set(
                pending_key,
                json.dumps({"password_hash": hashed, "username": username}),
                ex=EMAIL_VERIFICATION_CODE_TTL,
            )

            logger.info(
                "Pending registration stored email=%s",
                email,
            )

        elif purpose == VerificationPurpose.ADD_PASSWORD:
            if not password:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password required")

            user = await self.user_service.get_by_email(email)

            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            if user.password_hash:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Password already set",
                )

            hashed = hash_password(password)

            await redis_client.set(
                pending_key,
                hashed,
                ex=EMAIL_VERIFICATION_CODE_TTL,
            )

            logger.info(
                "Pending add password stored email=%s",
                email,
            )

        await EmailVerificationService.send_code(
            email,
            purpose,
        )

        logger.info(
            "Verification code sent email=%s purpose=%s",
            email,
            purpose,
        )

        return MessageResponse(message="Verification code sent")

    async def verify_code(
        self,
        email: str,
        code: str,
        purpose: VerificationPurpose,
    ) -> MessageResponse:
        logger.info(
            "AuthService.verify_code email=%s purpose=%s",
            email,
            purpose,
        )

        valid = await EmailVerificationService.verify_code(
            email,
            code,
            purpose,
        )

        if not valid:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Invalid or expired code",
            )

        pending_key = RedisKeys.pending(email, purpose)

        hashed_password = await redis_client.get(pending_key)

        if not hashed_password:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Pending request expired",
            )

        if purpose == VerificationPurpose.REGISTER:
            existing = await self.user_service.get_by_email(email)

            if existing:
                await redis_client.delete(pending_key)
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")

            pending_data = json.loads(hashed_password)
            username = pending_data.get("username")
            password_hash = pending_data.get("password_hash")

            if not username or not password_hash:
                await redis_client.delete(pending_key)
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Invalid pending registration data"
                )

            user = await self.user_service.create_user(
                UserCreate(username=username, email=email, password=password_hash),
                password_already_hashed=True,
            )

            logger.info(
                "User created user_id=%s email=%s username=%s",
                user.id,
                email,
                username,
            )

        elif purpose == VerificationPurpose.ADD_PASSWORD:
            user = await self.user_service.get_by_email(email)  # type: ignore

            if not user:
                await redis_client.delete(pending_key)
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            if user.password_hash:  # type: ignore
                await redis_client.delete(pending_key)
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Password already set",
                )

            await self.user_service.set_password_hash(
                user,  # type: ignore
                hashed_password,
            )

            logger.info(
                "Password added user_id=%s email=%s",
                user.id,
                email,
            )

        await redis_client.delete(pending_key)

        logger.info(
            "Pending state cleared email=%s purpose=%s",
            email,
            purpose,
        )

        return MessageResponse(message="Success")
