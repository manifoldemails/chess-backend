# auth/schemas.py
from pydantic import BaseModel, EmailStr, field_validator, ValidationError

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password cannot be longer than 72 bytes.")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
