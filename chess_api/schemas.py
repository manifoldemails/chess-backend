# auth/schemas.py
from pydantic import BaseModel, EmailStr, field_validator, ValidationError

class MoveData(BaseModel):
    from_: str
    to: str
    class Config:
        fields = {"from_": "from"}

class MoveRequest(BaseModel):
    fen: str
    move: MoveData

class MoveResponse(BaseModel):
    fen: str
    bot_move: str