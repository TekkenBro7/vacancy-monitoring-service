from pydantic import BaseModel, EmailStr, Field

from src.core.enums import VerificationPurpose


class LoginSchema(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str


class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    id_token: str


class GoogleUserInfo(BaseModel):
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str | None = None


class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: VerificationPurpose
    password: str | None = None
    username: str | None = None


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    purpose: VerificationPurpose
