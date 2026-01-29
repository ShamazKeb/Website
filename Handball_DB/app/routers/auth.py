from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models import Player, Coach # Import Player and Coach

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    result = await db.execute(select(models.User).filter(models.User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    await db.flush()  # Flush to get db_user.id before creating player/coach

    if user.role == models.Role.player:
        # Create a corresponding Player entry
        db_player = models.Player(user_id=db_user.id, first_name=user.email.split('@')[0], last_name="") # Placeholder names
        db.add(db_player)
    elif user.role == models.Role.coach:
        # Create a corresponding Coach entry
        db_coach = models.Coach(user_id=db_user.id, first_name=user.email.split('@')[0], last_name="") # Placeholder names
        db.add(db_coach)
    
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.post("/login", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == form_data.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
