from typing import Optional
from pydantic import BaseModel, EmailStr

class CoachCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

class CoachResponse(BaseModel):
    id: int # Coach Profile ID
    user_id: int
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
