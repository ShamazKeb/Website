from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.security import get_current_admin, hash_password
from app import models, schemas
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/dev",
    tags=["dev"],
    dependencies=[Depends(get_current_admin)], # Protected by admin auth in dev
    responses={status.HTTP_403_FORBIDDEN: {"detail": "Operation forbidden"}},
)


@router.get("/hacker-mode")
async def hacker_mode_ui():
    return {"message": "Welcome to Hacker Mode! This endpoint is for development purposes only."}

@router.post("/create_test_user/{role}", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_test_user(role: models.Role, db: AsyncSession = Depends(get_db)):
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This endpoint is only available in development environment.")

    email = f"test_{role}@{role}.com"
    password = "password"

    result = await db.execute(select(models.User).filter(models.User.email == email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Test {role} user already exists")

    hashed_password = hash_password(password)
    db_user = models.User(email=email, password_hash=hashed_password, role=role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    if role == models.Role.player:
        db_player = models.Player(user_id=db_user.id, first_name=f"Test {role}", last_name="User")
        db.add(db_player)
        await db.commit()
        await db.refresh(db_player)
    elif role == models.Role.coach:
        db_coach = models.Coach(user_id=db_user.id, first_name=f"Test {role}", last_name="Coach")
        db.add(db_coach)
        await db.commit()
        await db.refresh(db_coach)

    return db_user

@router.post("/generate_sample_data", status_code=status.HTTP_201_CREATED)
async def generate_sample_data(db: AsyncSession = Depends(get_db)):
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This endpoint is only available in development environment.")

    # This is a placeholder. Real sample data generation would be more complex.
    # For example, create some teams, coaches, players, exercises, and measurements.
    
    return {"message": "Sample data generation initiated (placeholder)."}
