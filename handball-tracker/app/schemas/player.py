from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.player import Hand, Position

class PlayerCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    year_of_birth: Optional[int] = None
    hand: Optional[Hand] = None
    position: Optional[Position] = None
    jersey_number: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None

class PlayerResponse(BaseModel):
    id: int  # This is the Player Profile ID
    user_id: int
    first_name: str
    last_name: str
    year_of_birth: Optional[int] = None
    hand: Optional[Hand] = None
    position: Optional[Position] = None
    jersey_number: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
