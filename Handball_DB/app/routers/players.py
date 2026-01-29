from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import get_current_user, get_current_coach_or_admin, get_current_admin
from app.crud import measurements as crud_measurements
from app.crud import teams as crud_teams
from app.crud import players as crud_players
from app.crud.activity_logs import create_activity_log
from app.schemas import ActivityLogCreate
from app.models import ActionType

router = APIRouter(prefix="/players", tags=["players"])

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Added for select statement
from typing import Optional
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import get_current_user, get_current_coach_or_admin, get_current_admin, hash_password # hash_password added
from app.crud import measurements as crud_measurements
from app.crud import teams as crud_teams
from app.crud import players as crud_players
from app.crud.activity_logs import create_activity_log
from app.schemas import ActivityLogCreate
from app.models import ActionType

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/", response_model=List[schemas.Player])
async def read_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve players.
    Coach sees only players in their teams.
    Admin sees all players.
    """
    if current_user.role == models.Role.coach:
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        if not coach_teams:
            return []
        
        all_players = set()
        for team in coach_teams:
            players = await crud_teams.get_players_in_team(db, team.id)
            all_players.update(players)
        
        # Manually pagination for now since we are merging lists from teams
        # ideally we should do this in a single query join
        players_list = list(all_players)
        players_list.sort(key=lambda x: x.last_name) # Sort by name
        return players_list[skip : skip + limit]

    elif current_user.role == models.Role.admin or current_user.role == models.Role.player:
        return await crud_players.get_players(db, skip=skip, limit=limit)
    
    return []


@router.post("/", response_model=schemas.Player, status_code=status.HTTP_201_CREATED)
async def create_player_endpoint(
    player_in: schemas.PlayerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Create a new player (Coach or Admin).
    A corresponding user account will be created with role 'player'.
    The password for this user will be a placeholder and should be updated by an admin/coach.
    """
    # First, create a User record for the player
    # Using a placeholder password and the player's first name + last name as email for now
    # In a real app, this would involve a more robust user invitation/creation flow.
    player_email = f"{player_in.first_name.lower()}.{player_in.last_name.lower()}@handball.player"
    
    # Check if user already exists
    result = await db.execute(select(models.User).filter(models.User.email == player_email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player email already registered.")

    # Create a placeholder password (e.g., "password123", should be changed on first login)
    temp_password = "changeme" # This needs a proper flow for password setting
    hashed_password = hash_password(temp_password) # Using the imported hash_password

    db_user = models.User(
        email=player_email,
        password_hash=hashed_password,
        role=models.Role.player
    )
    db.add(db_user)
    await db.flush() # Flush to get the user_id

    # Now create the Player record linked to the new user
    db_player = await crud_players.create_player(db=db, player_in=player_in, user_id=db_user.id)

    # Log the activity
    description = ""
    if current_user.role == models.Role.coach:
        description = f"Coach {current_user.coach.first_name} {current_user.coach.last_name} created new player {player_in.first_name} {player_in.last_name}."
    elif current_user.role == models.Role.admin:
        description = f"Admin {current_user.email} created new player {player_in.first_name} {player_in.last_name}."

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=ActionType.coach_create_player if current_user.role == models.Role.coach else ActionType.admin_action,
            user_id=current_user.id,
            target_player_id=db_player.id,
            description=description,
        ),
    )

    return db_player


@router.put("/{player_id}/deactivate", response_model=schemas.Player)
async def deactivate_player_endpoint(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Deactivate a player (Coach or Admin).
    Coaches can only deactivate players in their assigned teams.
    Admins can deactivate any player.
    """
    player_to_deactivate = await crud_players.get_player_by_id(db, player_id)
    if not player_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")

    if current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach cannot deactivate players not in their assigned teams.",
            )
        description = f"Coach {current_user.coach.first_name} {current_user.coach.last_name} deactivated player {player_to_deactivate.first_name} {player_to_deactivate.last_name}."
    elif current_user.role == models.Role.admin:
        description = f"Admin {current_user.email} deactivated player {player_to_deactivate.first_name} {player_to_deactivate.last_name}."
    
    deactivated_player = await crud_players.deactivate_player(db, player_to_deactivate)

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=ActionType.coach_deactivate_player if current_user.role == models.Role.coach else ActionType.admin_action,
            user_id=current_user.id,
            target_player_id=deactivated_player.id,
            description=description,
        ),
    )
    return deactivated_player


@router.put("/{player_id}/activate", response_model=schemas.Player)
async def activate_player_endpoint(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Activate a player (Coach or Admin).
    Coaches can only activate players in their assigned teams.
    Admins can activate any player.
    """
    player_to_activate = await crud_players.get_player_by_id(db, player_id)
    if not player_to_activate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")

    if current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach cannot activate players not in their assigned teams.",
            )
        description = f"Coach {current_user.coach.first_name} {current_user.coach.last_name} activated player {player_to_activate.first_name} {player_to_activate.last_name}."
    elif current_user.role == models.Role.admin:
        description = f"Admin {current_user.email} activated player {player_to_activate.first_name} {player_to_activate.last_name}."
    
    activated_player = await crud_players.activate_player(db, player_to_activate)

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=ActionType.admin_action, # Activation is generally an admin action or a coach action for their own player.
            user_id=current_user.id,
            target_player_id=activated_player.id,
            description=description,
        ),
    )
    return activated_player

@router.get("/{player_id}/stats", response_model=schemas.PlayerStatsAcrossExercisesResponse)
async def get_player_stats_across_exercises_endpoint(
    player_id: int,
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve a player's statistics across all exercises.
    - A **player** can only retrieve their own stats.
    - A **coach** can retrieve stats for any player on a team they coach.
    - An **admin** can retrieve any player's stats.
    """
    # Authorization check
    if current_user.role == models.Role.player:
        if current_user.player.id != player_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Players can only view their own stats.")
    elif current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach cannot view stats for this player.")
    # Admin has access to all players' stats, no specific check needed.

    stats = await crud_measurements.get_player_stats_across_exercises(
        db,
        player_id,
        date_from,
        date_to,
    )
    return schemas.PlayerStatsAcrossExercisesResponse(player_id=player_id, stats_by_exercise=stats)


@router.get("/me/measurements", response_model=list[schemas.PlayerMeasurementResponse])
async def get_my_measurements(
    exercise_id: Optional[int] = Query(None, description="Filter by exercise ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve current player's own measurements.
    """
    if not current_user.player:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a player.")
    
    measurements = await crud_measurements.get_player_measurements(
        db=db,
        player_id=current_user.player.id,
        exercise_id=exercise_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return measurements


@router.post("/me/measurements", response_model=schemas.PlayerMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def record_my_measurement(
    measurement_in: schemas.PlayerMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Record a measurement for the current player.
    """
    if not current_user.player:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a player.")
    
    if measurement_in.player_id != current_user.player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Players can only record measurements for themselves via this endpoint.",
        )
    
    # Validate that all required measurement types for the exercise have values
    exercise = await crud_measurements.get_exercise_with_measurement_types(db, measurement_in.exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    required_types = {mt.measurement_type for mt in exercise.measurement_type_links if mt.is_required}
    provided_types = {mv.measurement_type for mv in measurement_in.values}

    if not required_types.issubset(provided_types):
        missing_types = required_types - provided_types
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required measurement types: {', '.join([mt.value for mt in missing_types])}",
        )
    
    # Check for unknown measurement types
    allowed_types = {mt.measurement_type for mt in exercise.measurement_type_links}
    unknown_types = provided_types - allowed_types
    if unknown_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown measurement types for this exercise: {', '.join([mt.value for mt in unknown_types])}",
        )

    db_measurement = await crud_measurements.create_player_measurement(
        db=db, measurement=measurement_in, created_by_user_id=current_user.id
    )
    return db_measurement
