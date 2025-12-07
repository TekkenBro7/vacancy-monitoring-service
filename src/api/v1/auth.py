from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.dependencies.users import get_current_user
from src.schemas.auth import LoginSchema, Token
from src.schemas.users import UserRead
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
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(data)


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.refresh(refresh_token)


@router.get("/users/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
