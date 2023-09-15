from pydantic import BaseModel


class SwitToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str
    scope: str


class Payload(BaseModel):
    aud: str
    exp: int
    iss: str
    sub: str
    cmp_id: str | None
    apps_id: str
    app_user_id: str
    issue_type: int


class UserSchema(BaseModel):
    swit_id: str
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True
