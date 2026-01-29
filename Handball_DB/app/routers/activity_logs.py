from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import get_current_coach_or_admin
from app.crud import activity_logs as crud_activity_logs
from app.crud import teams as crud_teams

router = APIRouter(prefix="/activity-logs", tags=["activity logs"])

@router.get("/", response_model=List[schemas.ActivityLogResponse])
async def get_activity_logs_endpoint(
    user_id: Optional[int] = Query(None, description="Filter by user ID who performed the action"),
    player_id: Optional[int] = Query(None, description="Filter by target player ID"),
    team_id: Optional[int] = Query(None, description="Filter by target team ID"),
    exercise_id: Optional[int] = Query(None, description="Filter by target exercise ID"),
    action_type: Optional[models.ActionType] = Query(None, description="Filter by action type"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (e.g., 2023-01-01T00:00:00)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (e.g., 2023-12-31T23:59:59)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Retrieve activity logs with filtering and pagination.
    Coach sees logs related to their teams/players. Admin sees all logs.
    """
    allowed_player_ids: Optional[List[int]] = None
    allowed_team_ids: Optional[List[int]] = None

    if current_user.role == models.Role.coach:
        coach_teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
        if not coach_teams:
            return [] # Coach has no teams, so no logs related to their teams

        allowed_team_ids = [team.id for team in coach_teams]
        
        # Get all players in those teams
        all_players_in_coach_teams = set()
        for team_id in allowed_team_ids:
            players = await crud_teams.get_players_in_team(db, team_id)
            all_players_in_coach_teams.update([p.id for p in players])
        allowed_player_ids = list(all_players_in_coach_teams)

        # If a specific team_id is requested by the coach, ensure it's one of their teams
        if team_id and team_id not in allowed_team_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach does not have access to logs for this team.",
            )
        # If a specific player_id is requested by the coach, ensure it's one of their players
        if player_id and player_id not in allowed_player_ids:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach does not have access to logs for this player.",
            )
        
        # Filter by logs where target_player_id is one of the coach's players
        # OR target_team_id is one of the coach's teams
        # We also need to consider logs where user_id is the coach themselves
        logs = []
        player_logs = await crud_activity_logs.get_activity_logs(
            db=db,
            player_id=player_id,
            team_id=team_id,
            exercise_id=exercise_id,
            action_type=action_type,
            date_from=date_from,
            date_to=date_to,
            skip=0, # Handled pagination manually
            limit=1000, # Max limit to get all relevant logs for merging
            allowed_player_ids=allowed_player_ids, # Pass this to filter logs by target player
            allowed_team_ids=allowed_team_ids, # Pass this to filter logs by target team
        )
        logs.extend(player_logs)

        # Additionally, get logs where the current coach is the user performing the action
        coach_own_logs = await crud_activity_logs.get_activity_logs(
            db=db,
            user_id=current_user.id, # Filter by the coach's own user_id
            exercise_id=exercise_id,
            action_type=action_type,
            date_from=date_from,
            date_to=date_to,
            skip=0, # These should be added to the main list
            limit=1000, # Max limit to get all of coach's own logs
        )
        
        # Merge and deduplicate if necessary, then paginate
        combined_logs = {log.id: log for log in logs}
        combined_logs.update({log.id: log for log in coach_own_logs})
        
        sorted_logs = sorted(combined_logs.values(), key=lambda x: x.created_at, reverse=True)
        return sorted_logs[skip : skip + limit]

    else: # Admin user
        logs = await crud_activity_logs.get_activity_logs(
            db=db,
            user_id=user_id,
            player_id=player_id,
            team_id=team_id,
            exercise_id=exercise_id,
            action_type=action_type,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )
        return logs