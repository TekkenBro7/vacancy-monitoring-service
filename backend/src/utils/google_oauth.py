import httpx

from src.core.config import oauth_config
from src.core.logger import logger

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


async def exchange_code_for_token(code: str) -> dict:
    logger.info("Exchanging Google OAuth code for token")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": oauth_config.GOOGLE_CLIENT_ID,
                "client_secret": oauth_config.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": oauth_config.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    response.raise_for_status()
    return response.json()


async def get_google_user_info(access_token: str) -> dict:
    logger.info("Fetching Google user info")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    response.raise_for_status()

    return response.json()
