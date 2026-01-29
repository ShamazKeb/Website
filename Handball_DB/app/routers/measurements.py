from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import (
    get_current_admin,
    get_current_coach,
    get_current_player,
    get_current_coach_or_admin,
    verify_coach_has_team_access,
    get_current_user
)
from app.crud import measurements as crud_measurements
from app.crud import teams as crud_teams # Import crud_teams
from app.crud.activity_logs import create_activity_log
from app.schemas import ActivityLogCreate
from app.models import ActionType

router = APIRouter(prefix="/measurements", tags=["player measurements"])


# Dependency to get a measurement by ID
async def get_measurement_by_id(
    measurement_id: int, db: AsyncSession = Depends(get_db)
) -> models.PlayerMeasurement:
    measurement = await crud_measurements.get_player_measurement_by_id(db, measurement_id)
    if not measurement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return measurement


@router.post("/", response_model=schemas.PlayerMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def record_measurement(
    measurement_in: schemas.PlayerMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Record measurement for a player on an exercise.
    Player can only record for themselves.
    Coach can record for players in their teams.
    Admin can record for any player.
    """
    # Authorization checks
    if current_user.role == models.Role.player:
        if measurement_in.player_id != current_user.player.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Players can only record measurements for themselves.",
            )
        action_type = ActionType.player_entry
        player_obj = await crud_measurements.get_player(db, measurement_in.player_id)
        exercise_obj = await crud_measurements.get_exercise(db, measurement_in.exercise_id)
        description = f"Player {player_obj.first_name} {player_obj.last_name} recorded a measurement for exercise {exercise_obj.name}."

    elif current_user.role == models.Role.coach:
        # Check if the coach has access to the player's team
        player_teams = await crud_teams.get_teams_for_player(db, measurement_in.player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach can only record measurements for players in their assigned teams.",
            )
        action_type = ActionType.coach_add_measurement
        player_obj = await crud_measurements.get_player(db, measurement_in.player_id)
        exercise_obj = await crud_measurements.get_exercise(db, measurement_in.exercise_id)
        description = f"Coach {current_user.coach.first_name} {current_user.coach.last_name} added a measurement for player {player_obj.first_name} {player_obj.last_name} for exercise {exercise_obj.name}."

    elif current_user.role == models.Role.admin:
        # Admin can record for any player, no further checks needed
        action_type = ActionType.admin_action
        player_obj = await crud_measurements.get_player(db, measurement_in.player_id)
        exercise_obj = await crud_measurements.get_exercise(db, measurement_in.exercise_id)
        description = f"Admin {current_user.email} added a measurement for player {player_obj.first_name} {player_obj.last_name} for exercise {exercise_obj.name}."
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to record measurements.")

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

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=action_type,
            user_id=current_user.id,
            target_player_id=measurement_in.player_id,
            target_exercise_id=measurement_in.exercise_id,
            description=description,
        ),
    )

    return db_measurement


@router.get("/", response_model=List[schemas.PlayerMeasurementResponse])
async def list_measurements(
    player_id: Optional[int] = Query(None, description="Filter by player ID"),
    exercise_id: Optional[int] = Query(None, description="Filter by exercise ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin), # Only coach or admin can list all measurements
):
    """
    List measurements with filters.
    Coach can only see measurements from their team's players.
    Admin can see all measurements.
    """
    allowed_player_ids: Optional[List[int]] = None

    if current_user.role == models.Role.coach:
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        if not coach_teams:
            return [] # Coach has no teams, so no measurements
        
        coach_player_ids = set()
        for team in coach_teams:
            players_in_team = await crud_teams.get_players_in_team(db, team.id)
            coach_player_ids.update(p.id for p in players_in_team)
        
        if player_id and player_id not in coach_player_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach does not have access to this player's measurements.",
            )
        
        # If a specific player_id is requested and it's in the coach's allowed players,
        # then we filter by that player_id. Otherwise, we allow all players in coach's teams.
        allowed_player_ids = list(coach_player_ids)
        if player_id:
            allowed_player_ids = [player_id]

        if team_id:
            # Additionally verify that the coach has access to the requested team_id
            try:
                await crud_teams.get_team_by_id(db, team_id) # Check if team exists
                await verify_coach_has_team_access(current_user, team_id, db)
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Coach does not have access to this team's measurements.",
                )
    
    measurements = await crud_measurements.get_player_measurements(
        db=db,
        player_id=player_id if current_user.role == models.Role.admin else None, # Admin can specify any player_id
        exercise_id=exercise_id,
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
        allowed_player_ids=allowed_player_ids, # Pass allowed player IDs for coaches
        skip=skip,
        limit=limit,
    )
    return measurements





@router.get("/aggregated-stats", response_model=schemas.MeasurementStatsResponse)
async def get_measurement_aggregated_stats(
    player_id: int = Query(..., description="Player ID for which to retrieve stats"),
    exercise_id: int = Query(..., description="Exercise ID for which to retrieve stats"),
    measurement_type: models.MeasurementType = Query(..., description="Measurement type for which to retrieve stats"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Retrieve measurement statistics (average, best, trend) for a specific player and exercise.
    Coach can only see stats for players in their teams. Admin can see stats for any player.
    """
    if current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach does not have access to this player's statistics.",
            )
    
    stats = await crud_measurements.get_measurement_stats(
        db,
        player_id,
        exercise_id,
        measurement_type,
        date_from,
        date_to,
    )
    return schemas.MeasurementStatsResponse(**stats)


@router.get("/stats", response_model=List[schemas.PlayerMeasurementResponse])
async def get_measurement_raw_stats(
    exercise_id: int = Query(..., description="Exercise ID"),
    player_ids: Optional[str] = Query(None, description="Comma-separated list of player IDs"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Get raw measurement data for charting.
    """
    requested_player_ids = []
    if player_ids:
        try:
            requested_player_ids = [int(pid.strip()) for pid in player_ids.split(",") if pid.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid player_ids format. Must be comma-separated integers.")

    allowed_player_ids = None
    if current_user.role == models.Role.coach:
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        if not coach_teams:
            return []
        
        coach_player_ids = set()
        for team in coach_teams:
            players = await crud_teams.get_players_in_team(db, team.id)
            coach_player_ids.update(p.id for p in players)
        
        # Verify requested players are in coach's allowed list
        if requested_player_ids:
            for pid in requested_player_ids:
                if pid not in coach_player_ids:
                     raise HTTPException(status_code=403, detail=f"Coach does not have access to player {pid}")
            allowed_player_ids = requested_player_ids
        else:
            allowed_player_ids = list(coach_player_ids)
    elif current_user.role == models.Role.admin:
        allowed_player_ids = requested_player_ids if requested_player_ids else None

    measurements = await crud_measurements.get_player_measurements(
        db=db,
        exercise_id=exercise_id,
        date_from=date_from,
        date_to=date_to,
        allowed_player_ids=allowed_player_ids,
        limit=1000 # Increase limit for charts
    )
    return measurements


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntryResponse])
async def get_leaderboard(
    exercise_id: int = Query(..., description="Exercise ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    birth_year: Optional[int] = Query(None, description="Filter by birth year"),
    season: Optional[str] = Query(None, description="Filter by season"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user), # Any user can view leaderboards ideally? Or just authenticated.
):
    """
    Get leaderboard for an exercise.
    """
    # 1. Get exercise to know measurement type logic (higher/lower is better)
    exercise = await crud_measurements.get_exercise_with_measurement_types(db, exercise_id)
    if not exercise:
         raise HTTPException(status_code=404, detail="Exercise not found")
    
    if not exercise.measurement_type_links:
        return []

    # Assume the first measurement type is the primary one for leaderboard
    primary_mt = exercise.measurement_type_links[0].measurement_type

    # 2. Get all relevant measurements
    # We need to filter manually for team/birth_year if crud doesn't support deep filtering efficiently yet
    # But crud supports team_id. logic for birth_year/season needs to be handled.
    
    filter_team_id = team_id
    
    # Check permissions if coach? Actually leaderboards are usually public within the org.
    # But strictly speaking, coach should only see their teams? Or maybe all teams?
    # Let's assume open for all authenticated users for now, or apply standard RBAC if needed.
    # Spec doesn't strictly restriction leaderboard visibility.

    measurements = await crud_measurements.get_player_measurements(
        db=db,
        exercise_id=exercise_id,
        team_id=filter_team_id,
        limit=5000 # Fetch enough to aggregate
    )
    
    # 3. Filter and Aggregate in Memory (for MVP simplicity)
    leaderboard = {} # player_id -> {best_value, recorded_at}

    for m in measurements:
        # Filter by birth_year if needed (requires fetching player details if not eager loaded, but crud loads values)
        # m.player is NOT eager loaded in get_player_measurements by default options?
        # Check crud: select(models.PlayerMeasurement).options(selectinload(models.PlayerMeasurement.values))
        # It does NOT join player. So we can't filter by birth_year easily without join.
        # However, for MVP, if birth_year is required, we might need to fetch player info.
        # Let's Skip birth_year filter implementation for now inside this loop loop unless we update CRUD.
        # Or we can lazy load player (bad for performance).
        # Better: Update CRUD to join player if needed. 
        # For now, let's implement the aggregation first.
        
        val_entry = next((v for v in m.values if v.measurement_type == primary_mt), None)
        if not val_entry:
            continue
            
        try:
            val = float(val_entry.value)
        except ValueError:
            continue
            
        pid = m.player_id
        
        is_better = False
        if pid not in leaderboard:
            is_better = True
        else:
            current_best = leaderboard[pid]['best_value']
            # Determine if better based on type
            if primary_mt in [models.MeasurementType.seconds, models.MeasurementType.meters, models.MeasurementType.centimeters]: # Usually lower seconds is better? Wait. Meters/Centimeters HIGHER is better. Seconds LOWER is better.
                # Assuming Time (seconds) -> Lower is better. Distance/Weight -> Higher is better.
                if primary_mt == models.MeasurementType.seconds:
                    if val < current_best: is_better = True
                else: # Distance, Weight, Reps
                    if val > current_best: is_better = True
            else: # Reps, Weight
                 if val > current_best: is_better = True

        if is_better:
            leaderboard[pid] = {
                'player_id': pid,
                'best_value': val,
                'recorded_at': m.recorded_at
            }

    results = list(leaderboard.values())
    
    # Sort final results
    if primary_mt == models.MeasurementType.seconds:
        results.sort(key=lambda x: x['best_value']) # Ascending
    else:
        results.sort(key=lambda x: x['best_value'], reverse=True) # Descending

    return [schemas.LeaderboardEntryResponse(**r) for r in results]

@router.get('/{measurement_id}', response_model=schemas.PlayerMeasurementResponse)
async def get_single_measurement(
    measurement: models.PlayerMeasurement = Depends(get_measurement_by_id),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    '''
    Get a single measurement detail.
    Owner player, coach (of player's team), or admin can access.
    '''
    if current_user.role == models.Role.player:
        if measurement.player_id != current_user.player.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Players can only view their own measurements.',
            )
    elif current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, measurement.player_id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Coach does not have access to this player''s measurements.',
            )
    elif current_user.role == models.Role.admin:
        pass # Admin has full access
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to view this measurement.')
    
    return measurement


@router.put('/{measurement_id}', response_model=schemas.PlayerMeasurementResponse)
async def update_single_measurement(
    measurement_in: schemas.PlayerMeasurementUpdate,
    measurement: models.PlayerMeasurement = Depends(get_measurement_by_id),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin), # Only coach or admin can update
):
    '''
    Update measurement values.
    Only coach (of player's team) or admin can edit. Players cannot edit after submission.
    '''
    if current_user.role == models.Role.coach:
        player_teams = await crud_teams.get_teams_for_player(db, measurement.player.id)
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        
        player_team_ids = {t.id for t in player_teams}
        coach_team_ids = {t.id for t in coach_teams}

        if not player_team_ids.intersection(coach_team_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Coach does not have permission to update this player''s measurements.',
            )
        action_type = ActionType.coach_edit_measurement
        player_obj = await crud_measurements.get_player(db, measurement.player.id)
        exercise_obj = await crud_measurements.get_exercise(db, measurement.exercise.id)
        description = f'Coach {current_user.coach.first_name} {current_user.coach.last_name} edited a measurement for player {player_obj.first_name} {player_obj.last_name} for exercise {exercise_obj.name}.'
    
    elif current_user.role == models.Role.admin:
        # Admin can update any measurement
        action_type = ActionType.admin_action
        player_obj = await crud_measurements.get_player(db, measurement.player.id)
        exercise_obj = await crud_measurements.get_exercise(db, measurement.exercise.id)
        description = f'Admin {current_user.email} edited a measurement for player {player_obj.first_name} {player_obj.last_name} for exercise {exercise_obj.name}.'
    
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to update this measurement.')


    updated_measurement = await crud_measurements.update_player_measurement(
        db=db, db_measurement=measurement, measurement_update=measurement_in
    )

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=action_type,
            user_id=current_user.id,
            target_player_id=measurement.player.id,
            target_exercise_id=measurement.exercise.id,
            description=description,
        ),
    )

    return updated_measurement


@router.delete('/{measurement_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_measurement(
    measurement: models.PlayerMeasurement = Depends(get_measurement_by_id),
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin), # Only admin can delete
):
    '''
    Soft delete measurement.
    Admin only.
    '''
    await crud_measurements.delete_player_measurement(db=db, db_measurement=measurement)

    # Log the activity
    player_obj = await crud_measurements.get_player(db, measurement.player.id)
    exercise_obj = await crud_measurements.get_exercise(db, measurement.exercise.id)
    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=ActionType.admin_action,
            user_id=current_admin.id,
            target_player_id=measurement.player.id,
            target_exercise_id=measurement.exercise.id,
            description=f'Admin {current_admin.email} soft-deleted a measurement for player {player_obj.first_name} {player_obj.last_name} for exercise {exercise_obj.name}.',
        ),
    )

    return

