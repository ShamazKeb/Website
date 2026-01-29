from typing import List, Optional, Dict, Any
from datetime import datetime
from statistics import mean
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.models import MeasurementType, PlayerMeasurement, MeasurementValue


async def create_player_measurement(
    db: AsyncSession,
    measurement: schemas.PlayerMeasurementCreate,
    created_by_user_id: int,
) -> models.PlayerMeasurement:
    """
    Creates a new PlayerMeasurement record and associated MeasurementValue records.
    """
    db_measurement = models.PlayerMeasurement(
        player_id=measurement.player_id,
        exercise_id=measurement.exercise_id,
        recorded_at=measurement.recorded_at,
        notes=measurement.notes,
        created_by_user_id=created_by_user_id,
    )
    db.add(db_measurement)
    await db.flush()  # Flush to get db_measurement.id

    for mv_schema in measurement.values:
        db_value = models.MeasurementValue(
            player_measurement_id=db_measurement.id,
            measurement_type=mv_schema.measurement_type,
            value=mv_schema.value,
        )
        db.add(db_value)

    await db.commit()
    await db.refresh(db_measurement)
    return db_measurement


async def get_player_measurement_by_id(
    db: AsyncSession, measurement_id: int, include_inactive: bool = False
) -> Optional[models.PlayerMeasurement]:
    """
    Retrieves a single PlayerMeasurement by its ID, eagerly loading its values.
    """
    query = select(models.PlayerMeasurement) \
        .options(selectinload(models.PlayerMeasurement.values)) \
        .filter(models.PlayerMeasurement.id == measurement_id)
    if not include_inactive:
        query = query.filter(models.PlayerMeasurement.is_active == True)
    
    result = await db.execute(query)
    return result.scalars().first()


async def get_exercise_with_measurement_types(
    db: AsyncSession, exercise_id: int
) -> Optional[models.Exercise]:
    """
    Retrieves an exercise by ID, eagerly loading its measurement type links.
    """
    result = await db.execute(
        select(models.Exercise)
        .options(selectinload(models.Exercise.measurement_type_links))
        .filter(models.Exercise.id == exercise_id, models.Exercise.is_active == True)
    )
    return result.scalars().first()

async def get_player(db: AsyncSession, player_id: int) -> Optional[models.Player]:
    result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    return result.scalars().first()

async def get_exercise(db: AsyncSession, exercise_id: int) -> Optional[models.Exercise]:
    result = await db.execute(select(models.Exercise).filter(models.Exercise.id == exercise_id))
    return result.scalars().first()



async def get_player_measurements(
    db: AsyncSession,
    player_id: Optional[int] = None,
    exercise_id: Optional[int] = None,
    team_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    include_inactive: bool = False,
    allowed_player_ids: Optional[List[int]] = None, # New parameter
    skip: int = 0,
    limit: int = 100,
) -> List[models.PlayerMeasurement]:
    """
    Retrieves a list of PlayerMeasurement records with various filters.
    """
    query = select(models.PlayerMeasurement).options(
        selectinload(models.PlayerMeasurement.values)
    )

    if not include_inactive:
        query = query.filter(models.PlayerMeasurement.is_active == True)
    
    if player_id:
        query = query.filter(models.PlayerMeasurement.player_id == player_id)
    
    if allowed_player_ids is not None:
        if not allowed_player_ids: # If the list is empty, no players are allowed
            return []
        query = query.filter(models.PlayerMeasurement.player_id.in_(allowed_player_ids))


    if player_id:
        query = query.filter(models.PlayerMeasurement.player_id == player_id)
    if exercise_id:
        query = query.filter(models.PlayerMeasurement.exercise_id == exercise_id)
    if team_id:
        # Filter by team_id: join through Player and team_players
        query = query.join(models.Player).join(models.team_players).filter(models.team_players.c.team_id == team_id)
    if date_from:
        query = query.filter(models.PlayerMeasurement.recorded_at >= date_from)
    if date_to:
        query = query.filter(models.PlayerMeasurement.recorded_at <= date_to)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_player_measurement(
    db: AsyncSession,
    db_measurement: models.PlayerMeasurement,
    measurement_update: schemas.PlayerMeasurementUpdate,
) -> models.PlayerMeasurement:
    """
    Updates an existing PlayerMeasurement and its associated MeasurementValue records.
    """
    if measurement_update.recorded_at:
        db_measurement.recorded_at = measurement_update.recorded_at
    if measurement_update.notes is not None:
        db_measurement.notes = measurement_update.notes

    if measurement_update.values is not None:
        # Delete existing values
        await db.execute(
            models.MeasurementValue.__table__.delete().where(
                models.MeasurementValue.player_measurement_id == db_measurement.id
            )
        )
        # Add new values
        for mv_schema in measurement_update.values:
            db_value = models.MeasurementValue(
                player_measurement_id=db_measurement.id,
                measurement_type=mv_schema.measurement_type,
                value=mv_schema.value,
            )
            db.add(db_value)

    await db.commit()
    await db.refresh(db_measurement)
    return db_measurement


async def delete_player_measurement(db: AsyncSession, db_measurement: models.PlayerMeasurement):
    """
    Soft deletes a PlayerMeasurement record.
    """
    db_measurement.is_active = False
    db.add(db_measurement)
    await db.commit()
    await db.refresh(db_measurement)
    return db_measurement


async def get_measurements_for_player_and_exercise(
    db: AsyncSession, player_id: int, exercise_id: int, include_inactive: bool = False
) -> List[models.PlayerMeasurement]:
    """
    Retrieves all measurements for a specific player and exercise, ordered by recorded_at.
    """
    query = select(models.PlayerMeasurement) \
        .options(selectinload(models.PlayerMeasurement.values)) \
        .filter(
            models.PlayerMeasurement.player_id == player_id,
            models.PlayerMeasurement.exercise_id == exercise_id,
        )
    if not include_inactive:
        query = query.filter(models.PlayerMeasurement.is_active == True)
    
    result = await db.execute(query.order_by(models.PlayerMeasurement.recorded_at))
    return result.scalars().all()


async def get_measurements_for_team_players(
    db: AsyncSession, coach_id: int, team_id: Optional[int] = None, include_inactive: bool = False
) -> List[models.PlayerMeasurement]:
    """
    Retrieves measurements for players within the teams coached by a specific coach.
    If team_id is provided, filters measurements for that specific team.
    """
    query = (
        select(models.PlayerMeasurement)
        .options(selectinload(models.PlayerMeasurement.values))
        .join(models.Player)
        .join(models.team_players)
        .join(models.Team.coaches)
        .filter(models.Coach.id == coach_id)
    )
    if not include_inactive:
        query = query.filter(models.PlayerMeasurement.is_active == True)

    if team_id:
        query = query.filter(models.Team.id == team_id)

    result = await db.execute(query)
    return result.scalars().all()


async def get_measurement_stats(
    db: AsyncSession,
    player_id: int,
    exercise_id: int,
    measurement_type: MeasurementType,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Calculates statistics (average, best, trend) for a specific player, exercise, and measurement type.
    """
    query = select(MeasurementValue.value, PlayerMeasurement.recorded_at) \
            .join(PlayerMeasurement) \
            .filter(
                PlayerMeasurement.player_id == player_id,
                PlayerMeasurement.exercise_id == exercise_id,
                MeasurementValue.measurement_type == measurement_type,
                PlayerMeasurement.is_active == True # Only active measurements
            )
    
    if date_from:
        query = query.filter(PlayerMeasurement.recorded_at >= date_from)
    if date_to:
        query = query.filter(PlayerMeasurement.recorded_at <= date_to)

    result = await db.execute(query.order_by(PlayerMeasurement.recorded_at))
    data = result.all()

    if not data:
        return {"average": None, "best": None, "trend": None, "count": 0}

    values = []
    for val_str, _ in data:
        try:
            values.append(float(val_str))
        except ValueError:
            # Handle cases where value might not be a float
            pass
    
    if not values:
        return {"average": None, "best": None, "trend": None, "count": 0}

    average = mean(values)
    count = len(values)

    best = None
    if measurement_type in [MeasurementType.seconds, MeasurementType.meters, MeasurementType.centimeters]:
        best = min(values) # Lower is better for time/distance
    elif measurement_type in [MeasurementType.repetitions, MeasurementType.kilograms]:
        best = max(values) # Higher is better for reps/weight
    
    # Simple trend: Compare average of first 25% vs last 25% of values
    trend = None
    if count >= 4: # Need at least 4 data points for a meaningful comparison
        quarter_count = count // 4
        first_quarter_avg = mean(values[:quarter_count])
        last_quarter_avg = mean(values[-quarter_count:])
        if first_quarter_avg < last_quarter_avg:
            trend = "improving" if measurement_type in [MeasurementType.repetitions, MeasurementType.kilograms] else "worsening"
        elif first_quarter_avg > last_quarter_avg:
            trend = "worsening" if measurement_type in [MeasurementType.repetitions, MeasurementType.kilograms] else "improving"
        else:
            trend = "stable"
    elif count >= 2: # Or just compare first and last if only 2 or 3
        if values[0] < values[-1]:
            trend = "improving" if measurement_type in [MeasurementType.repetitions, MeasurementType.kilograms] else "worsening"
        elif values[0] > values[-1]:
            trend = "worsening" if measurement_type in [MeasurementType.repetitions, MeasurementType.kilograms] else "improving"
        else:
            trend = "stable"


    return {"average": average, "best": best, "trend": trend, "count": count}


async def get_player_stats_across_exercises(
    db: AsyncSession,
    player_id: int,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Aggregates statistics for a player across all exercises.
    """
    stats_by_exercise: Dict[int, Dict[str, Any]] = {}

    # Get all distinct exercises the player has measurements for
    query_exercises = select(PlayerMeasurement.exercise_id) \
                        .filter(PlayerMeasurement.player_id == player_id, PlayerMeasurement.is_active == True)
    
    if date_from:
        query_exercises = query_exercises.filter(PlayerMeasurement.recorded_at >= date_from)
    if date_to:
        query_exercises = query_exercises.filter(PlayerMeasurement.recorded_at <= date_to)

    exercise_ids_result = await db.execute(query_exercises.distinct())
    exercise_ids = exercise_ids_result.scalars().all()

    for ex_id in exercise_ids:
        exercise = await get_exercise_with_measurement_types(db, ex_id)
        if exercise and exercise.measurement_type_links:
            stats_by_exercise[ex_id] = {
                "exercise_name": exercise.name,
                "measurement_type_stats": {}
            }
            for mt_link in exercise.measurement_type_links:
                stats = await get_measurement_stats(
                    db,
                    player_id,
                    ex_id,
                    mt_link.measurement_type,
                    date_from,
                    date_to,
                )
                stats_by_exercise[ex_id]["measurement_type_stats"][mt_link.measurement_type.value] = stats
    
    return stats_by_exercise
