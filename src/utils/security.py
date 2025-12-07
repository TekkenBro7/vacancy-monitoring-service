from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.core.config import jwt_config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=jwt_config.JWT_ACCESS_EXPIRE_SECONDS)
    payload = data.copy()
    payload.update({"exp": expire})
    return jwt.encode(payload, jwt_config.JWT_SECRET_KEY, algorithm=jwt_config.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=jwt_config.JWT_REFRESH_EXPIRE_SECONDS)
    payload = data.copy()
    payload.update({"exp": expire})
    return jwt.encode(
        payload, jwt_config.JWT_REFRESH_SECRET_KEY, algorithm=jwt_config.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, jwt_config.JWT_SECRET_KEY, algorithms=[jwt_config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Access token expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid access token") from e


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, jwt_config.JWT_REFRESH_SECRET_KEY, algorithms=[jwt_config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Refresh token expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid refresh token") from e
