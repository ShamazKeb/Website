from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import (
    get_current_player,
)
from app.crud import measurements as crud_measurements
from app.crud.activity_logs import create_activity_log
from app.schemas import ActivityLogCreate
from app.models import ActionType

router = APIRouter(prefix="/players/me/measurements", tags=["player measurements (self-access)"])


@router.get("/", response_model=List[schemas.PlayerMeasurementResponse])
async def list_my_measurements(
    exercise_id: Optional[int] = Query(None, description="Filter by exercise ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_player: models.User = Depends(get_current_player),
):
    """
    List current player's own measurements.
    """
    measurements = await crud_measurements.get_player_measurements(
        db=db,
        player_id=current_player.player.id,
        exercise_id=exercise_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return measurements


@router.post("/", response_model=schemas.PlayerMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def record_my_measurement(
    measurement_in: schemas.PlayerMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    current_player: models.User = Depends(get_current_player),
):
    """
    Record a measurement for the current player.
    """
    if measurement_in.player_id != current_player.player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Players can only record measurements for themselves using this endpoint.",
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
        db=db, measurement=measurement_in, created_by_user_id=current_player.id
    )

    # Log the activity
    await create_activity_log(
        db=db,
        log=schemas.ActivityLogCreate(
            action_type=ActionType.player_entry,
            user_id=current_player.id,
            target_player_id=current_player.player.id,
            target_exercise_id=measurement_in.exercise_id,
            description=f"Player {current_player.player.first_name} {current_player.player.last_name} recorded a measurement for exercise {exercise.name}.",
        ),
    )

    return db_measurement


@router.get("/stats", response_model=schemas.PlayerStatsAcrossExercisesResponse)
async def get_my_stats_across_exercises_endpoint(
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    db: AsyncSession = Depends(get_db),
    current_player: models.User = Depends(get_current_player),
):
    """
    Retrieve current player's statistics across all exercises.
    """
    stats = await crud_measurements.get_player_stats_across_exercises(
        db,
        current_player.player.id,
        date_from,
        date_to,
    )
    return schemas.PlayerStatsAcrossExercisesResponse(player_id=current_player.player.id, stats_by_exercise=stats)
