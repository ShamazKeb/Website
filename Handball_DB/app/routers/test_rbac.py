from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from app.security import (
    get_current_admin,
    get_current_coach,
    get_current_coach_or_admin,
    get_current_player,
    get_current_user,
    verify_player_self_access,
)
from app.database import get_db
from app.models import User


router = APIRouter(prefix="/test_rbac", tags=["test_rbac"])


@router.get("/admin", response_model=schemas.UserResponse)
async def read_admin_data(current_user: User = Depends(get_current_admin)):
    return current_user


@router.get("/coach", response_model=schemas.UserResponse)
async def read_coach_data(current_user: User = Depends(get_current_coach)):
    return current_user


@router.get("/coach_or_admin", response_model=schemas.UserResponse)
async def read_coach_or_admin_data(
    current_user: User = Depends(get_current_coach_or_admin)
):
    return current_user


@router.get("/player", response_model=schemas.UserResponse)
async def read_player_data(current_user: User = Depends(get_current_player)):
    return current_user


@router.get("/player_self_access/{target_player_id}", response_model=schemas.UserResponse)
async def player_self_access_test_endpoint(
    target_player_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await verify_player_self_access(current_user, target_player_id)
    return current_user
