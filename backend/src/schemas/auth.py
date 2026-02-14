from pydantic import BaseModel


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
