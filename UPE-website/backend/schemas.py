from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BeverageCreate(BaseModel):
    name: str
    type: str
    volume: float
    price: float
    store: str
    alcohol_content: float


class BeverageResponse(BaseModel):
    id: int
    name: str
    type: str
    volume: float
    price: float
    store: str
    alcohol_content: float
    created_at: datetime

    class Config:
        from_attributes = True
