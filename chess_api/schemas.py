# auth/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError

class MoveData(BaseModel):
    from_: str
    to: str
    color: str
    piece: str
    san: str = None
    lan: str = None
    before: str = None
    after: str = None
    class Config:
        fields = {"from_": "from"}

class MoveRequest(BaseModel):
    fen: str
    move: MoveData
    difficulty: int = Field(default=10, ge=0, le=20, description="Stockfish skill level (0-20)")

class MoveResponse(BaseModel):
    fen: str
    bot_move: str
    result: Optional[str] = None