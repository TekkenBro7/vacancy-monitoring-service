from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.dependencies.users import get_current_user, validate_access_token
from src.schemas.auth import LoginSchema, Token
from src.schemas.users import UserMe
from src.services.auth_service import AuthService
from src.services.user_service import UserService

router = APIRouter()


def get_user_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(db)


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)


@router.post("/login", response_model=Token)
async def login(
    data: LoginSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(data, response)


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.refresh(request, response)


@router.post("/logout")
async def logout(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    return await auth_service.logout(response)


@router.get("/validate")
async def validate(_: dict = Depends(validate_access_token)) -> dict:
    return {"message": "Access token is valid"}


@router.get("/users/me", response_model=UserMe)
async def get_me(current_user: UserMe = Depends(get_current_user)) -> UserMe:
    return current_user
