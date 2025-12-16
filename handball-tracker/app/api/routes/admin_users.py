from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User, UserRole
from app.models.player import Player
from app.models.coach import Coach
from app.schemas.player import PlayerCreate, PlayerResponse
from app.schemas.coach import CoachCreate, CoachResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin-users"]
)

@router.post("/players", response_model=PlayerResponse)
def create_player(
    player_in: PlayerCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # 1. Check if user email exists
    if db.query(User).filter(User.email == str(player_in.email)).first():
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # 2. Create User
    try:
        user = User(
            email=str(player_in.email),
            password_hash=get_password_hash(player_in.password),
            role=UserRole.PLAYER
        )
        db.add(user)
        db.flush() # Flush to get user.id
    except Exception: # Catching generically since integrity error might be wrapped
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists (Integrity Error)"
        )
    
    # 3. Create Player Profile
    player = Player(
        user_id=user.id,
        first_name=player_in.first_name,
        last_name=player_in.last_name,
        year_of_birth=player_in.year_of_birth,
        hand=player_in.hand,
        position=player_in.position,
        jersey_number=player_in.jersey_number,
        height_cm=player_in.height_cm,
        weight_kg=player_in.weight_kg,
        notes=player_in.notes,
        is_active=True
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    
    return player

@router.post("/coaches", response_model=CoachResponse)
def create_coach(
    coach_in: CoachCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # 1. Check if user email exists
    if db.query(User).filter(User.email == str(coach_in.email)).first():
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # 2. Create User
    try:
        user = User(
            email=str(coach_in.email),
            password_hash=get_password_hash(coach_in.password),
            role=UserRole.COACH
        )
        db.add(user)
        db.flush()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists (Integrity Error)"
        )
    
    # 3. Create Coach Profile
    coach = Coach(
        user_id=user.id,
        first_name=coach_in.first_name,
        last_name=coach_in.last_name,
        phone_number=coach_in.phone_number,
        is_active=True
    )
    db.add(coach)
    db.commit()
    db.refresh(coach)
    
    return coach
