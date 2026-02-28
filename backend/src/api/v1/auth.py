from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import base_config, oauth_config
from src.database.session import get_async_session
from src.dependencies.users import get_current_user, validate_access_token
from src.schemas.auth import LoginSchema, SendCodeRequest, Token, VerifyCodeRequest
from src.schemas.common import MessageResponse
from src.schemas.users import UserMe
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.utils.security import set_refresh_token_cookie

router = APIRouter()


def get_user_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(db)


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)


@router.post("/login/", response_model=Token)
async def login(
    data: LoginSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(data, response)


@router.post("/refresh/", response_model=Token)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.refresh(request, response)


@router.post("/logout/")
async def logout(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    return await auth_service.logout(response)


@router.get("/validate/", response_model=MessageResponse)
async def validate(_: dict = Depends(validate_access_token)) -> MessageResponse:
    return MessageResponse(message="Access token is valid")


@router.get("/users/me/", response_model=UserMe)
async def get_me(current_user: UserMe = Depends(get_current_user)) -> UserMe:
    return current_user


@router.get("/google/login/")
async def google_login() -> RedirectResponse:
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={oauth_config.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={oauth_config.GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(url)


@router.get("/google/callback/", response_model=Token)
async def google_callback(
    response: Response,
    code: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    token, refresh_token = await auth_service.google_auth(code, response)

    redirect_url = f"{base_config.FRONTEND_URL}/auth/success?access_token={token.access_token}"

    redirect_response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    set_refresh_token_cookie(redirect_response, refresh_token)

    return redirect_response


@router.post(
    "/send-code/",
    response_model=MessageResponse,
)
async def send_code(
    data: SendCodeRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    return await auth_service.send_code(
        email=data.email,
        purpose=data.purpose,
        password=data.password,
        username=data.username,
    )


@router.post(
    "/verify-code/",
    response_model=MessageResponse,
)
async def verify_code(
    data: VerifyCodeRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    return await auth_service.verify_code(
        email=data.email,
        code=data.code,
        purpose=data.purpose,
    )
