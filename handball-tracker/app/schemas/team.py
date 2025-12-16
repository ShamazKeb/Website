from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    season: str
    age_group: Optional[str] = None
    notes: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    name: Optional[str] = None
    season: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    is_active: bool
    created_at: datetime
    # We can return lists of IDs or simple objects. For now, let's keep it simple as requested.
    # If we want to return IDs, we'd need to extract them from the relationships in the ORM model
    # or rely on Pydantic's config if the model has those properties.
    # The SQLA models have 'players' and 'coaches' relationships which are lists of objects.
    # To return IDs, we can add properties to the ORM model or use a validator here.
    # For now, let's omit them to keep recursion simple unless explicitly needed by frontend.
    # The plan mentioned "Optional: player_ids: list[int] = []". Let's add them but they might be empty if not populated.

    class Config:
        orm_mode = True
