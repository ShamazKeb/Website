from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from typing import Optional
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Added this import
from app import models, schemas
from app.database import get_db
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 24 * 60)) # 24 hours

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(models.User).options(selectinload(models.User.coach), selectinload(models.User.player)).filter(models.User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.Role.admin:
        raise HTTPException(status_code=403, detail="The user is not an admin")
    return current_user


async def get_current_coach(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.Role.coach:
        raise HTTPException(status_code=403, detail="The user is not a coach")
    return current_user


async def get_current_coach_or_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.Role.coach, models.Role.admin]:
        raise HTTPException(status_code=403, detail="The user is not a coach or an admin")
    return current_user


async def get_current_player(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.Role.player:
        raise HTTPException(status_code=403, detail="The user is not a player")
    return current_user


async def get_coach_teams(coach_user: models.User, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.team_coaches.c.team_id).where(models.team_coaches.c.coach_id == coach_user.coach.id)
    )
    return [row[0] for row in result.all()]


async def verify_coach_has_team_access(coach_user: models.User, team_id: int, db: AsyncSession = Depends(get_db)):
    coach_teams = await get_coach_teams(coach_user, db)
    if team_id not in coach_teams:
        raise HTTPException(status_code=403, detail="Coach does not have access to this team")


async def verify_player_self_access(current_user: models.User, target_player_id: int):
    if current_user.role == models.Role.player and current_user.player.id != target_player_id:
        raise HTTPException(status_code=403, detail="Player can only access their own data")