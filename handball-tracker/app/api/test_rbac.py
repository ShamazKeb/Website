from fastapi import APIRouter, Depends
from typing import Annotated
from app.models.user import User
from app.dependencies.auth import get_current_admin, get_current_coach, get_current_player

router = APIRouter(prefix="/test", tags=["rbac-test"])

@router.get("/admin")
def test_admin_access(current_user: Annotated[User, Depends(get_current_admin)]):
    return {"message": "admin access granted"}

@router.get("/coach")
def test_coach_access(current_user: Annotated[User, Depends(get_current_coach)]):
    return {"message": "coach access granted"}

@router.get("/player")
def test_player_access(current_user: Annotated[User, Depends(get_current_player)]):
    return {"message": "player access granted"}
