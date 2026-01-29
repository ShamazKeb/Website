from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app import schemas, models
from app.security import get_current_admin, hash_password

class AdminPasswordReset(BaseModel):
    new_password: str

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
    responses={status.HTTP_403_FORBIDDEN: {"detail": "Operation forbidden"}},
)

@router.put("/users/{user_id}/reset_password", response_model=schemas.UserResponse)
async def reset_password_admin(user_id: int, password_reset: AdminPasswordReset, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.password_hash = hash_password(password_reset.new_password)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/dashboard")
async def read_admin_dashboard(db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count(models.User.id)))).scalar_one()
    total_teams = (await db.execute(select(func.count(models.Team.id)))).scalar_one()
    total_players = (await db.execute(select(func.count(models.Player.id)))).scalar_one()
    total_coaches = (await db.execute(select(func.count(models.Coach.id)))).scalar_one()
    total_measurements = (await db.execute(select(func.count(models.PlayerMeasurement.id)))).scalar_one()

    users_by_role = (await db.execute(select(models.User.role, func.count(models.User.id)).group_by(models.User.role))).all()
    users_by_role_dict = {role.value: count for role, count in users_by_role}

    return {
        "total_users": total_users,
        "total_teams": total_teams,
        "total_players": total_players,
        "total_coaches": total_coaches,
        "total_measurements": total_measurements,
        "users_by_role": users_by_role_dict,
    }

@router.get("/users", response_model=List[schemas.UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create Player or Coach entry if role is player or coach
    if user.role == models.Role.player:
        db_player = models.Player(user_id=db_user.id, first_name="New", last_name="Player")
        db.add(db_player)
        await db.commit()
        await db.refresh(db_player)
    elif user.role == models.Role.coach:
        db_coach = models.Coach(user_id=db_user.id, first_name="New", last_name="Coach")
        db.add(db_coach)
        await db.commit()
        await db.refresh(db_coach)

    return db_user


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user_admin(user_id: int, user_update: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.email:
        existing_user_result = await db.execute(select(models.User).filter(models.User.email == user_update.email))
        existing_user = existing_user_result.scalars().first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        db_user.email = user_update.email
    if user_update.role:
        db_user.role = user_update.role
    if user_update.password:
        db_user.password_hash = hash_password(user_update.password)

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user_admin(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if db_user.role == models.Role.player:
        player_result = await db.execute(select(models.Player).filter(models.Player.user_id == user_id))
        db_player = player_result.scalars().first()
        if db_player:
            db_player.is_active = False
            await db.commit()
    elif db_user.role == models.Role.coach:
        coach_result = await db.execute(select(models.Coach).filter(models.Coach.user_id == user_id))
        db_coach = coach_result.scalars().first()
        if db_coach:
            # We don't have an is_active for coach yet, so we'll just delete the coach entry
            # In a real app, we might soft delete coaches as well.
            await db.delete(db_coach)
            await db.commit()
    
    # Optionally, we could add an is_active field to the User model as well.
    # For now, we are considering the user inactive if their player/coach profile is inactive/deleted.

    return {}


@router.get("/teams", response_model=List[schemas.Team])
async def get_all_teams_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Team).options(selectinload(models.Team.players), selectinload(models.Team.coaches)))
    teams = result.scalars().all()
    return teams


@router.post("/teams/{team_id}/add_player/{player_id}", response_model=schemas.Team)
async def add_player_to_team_admin(team_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(models.Team).options(selectinload(models.Team.players), selectinload(models.Team.coaches)).filter(models.Team.id == team_id))
    team = team_result.scalars().first()
    player_result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    player = player_result.scalars().first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    if player not in team.players:
        team.players.append(player)
        await db.commit()
        await db.refresh(team)
    return team


@router.delete("/teams/{team_id}/remove_player/{player_id}", response_model=schemas.Team)
async def remove_player_from_team_admin(team_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(models.Team).options(selectinload(models.Team.players), selectinload(models.Team.coaches)).filter(models.Team.id == team_id))
    team = team_result.scalars().first()
    player_result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    player = player_result.scalars().first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    if player in team.players:
        team.players.remove(player)
        await db.commit()
        await db.refresh(team)
    return team


@router.post("/teams/{team_id}/add_coach/{coach_id}", response_model=schemas.Team)
async def add_coach_to_team_admin(team_id: int, coach_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(models.Team).options(selectinload(models.Team.players), selectinload(models.Team.coaches)).filter(models.Team.id == team_id))
    team = team_result.scalars().first()
    coach_result = await db.execute(select(models.Coach).filter(models.Coach.id == coach_id))
    coach = coach_result.scalars().first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")

    if coach not in team.coaches:
        team.coaches.append(coach)
        await db.commit()
        await db.refresh(team)
    return team


@router.delete("/teams/{team_id}/remove_coach/{coach_id}", response_model=schemas.Team)
async def remove_coach_from_team_admin(team_id: int, coach_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(models.Team).options(selectinload(models.Team.players), selectinload(models.Team.coaches)).filter(models.Team.id == team_id))
    team = team_result.scalars().first()
    coach_result = await db.execute(select(models.Coach).filter(models.Coach.id == coach_id))
    coach = coach_result.scalars().first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")

    if coach in team.coaches:
        team.coaches.remove(coach)
        await db.commit()
        await db.refresh(team)
    return team


@router.put("/exercises/{exercise_id}", response_model=schemas.Exercise)
async def update_exercise_admin(exercise_id: int, exercise_update: schemas.ExerciseUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Exercise).filter(models.Exercise.id == exercise_id))
    db_exercise = result.scalars().first()
    if not db_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    if exercise_update.name is not None:
        db_exercise.name = exercise_update.name
    if exercise_update.description is not None:
        db_exercise.description = exercise_update.description
    if exercise_update.is_active is not None:
        db_exercise.is_active = exercise_update.is_active
    
    # Handle categories update (replace existing categories)
    if exercise_update.categories is not None:
        db_exercise.categories.clear() # Clear existing categories
        for category_enum in exercise_update.categories:
            db_exercise.categories.append(models.ExerciseCategory(category=category_enum))


    await db.commit()
    await db.refresh(db_exercise)
    return db_exercise

@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_exercise_admin(exercise_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Exercise).filter(models.Exercise.id == exercise_id))
    db_exercise = result.scalars().first()
    if not db_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    db_exercise.is_active = False # Soft delete
    await db.commit()
    return {}

@router.put("/exercises/{exercise_id}/reassign_owner/{new_coach_id}", response_model=schemas.Exercise)
async def reassign_exercise_owner_admin(exercise_id: int, new_coach_id: int, db: AsyncSession = Depends(get_db)):
    exercise_result = await db.execute(select(models.Exercise).filter(models.Exercise.id == exercise_id))
    exercise = exercise_result.scalars().first()
    new_owner_coach_result = await db.execute(select(models.Coach).filter(models.Coach.id == new_coach_id))
    new_owner_coach = new_owner_coach_result.scalars().first()

    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if not new_owner_coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New owner coach not found")

    exercise.owner_coach_id = new_coach_id
    await db.commit()
    await db.refresh(exercise)
    return exercise
