from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from app.models import ActivityLog, ActionType
from app.schemas import ActivityLogCreate

async def create_activity_log(db: AsyncSession, log: ActivityLogCreate):
    db_log = ActivityLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_activity_logs(
    db: AsyncSession,
    user_id: Optional[int] = None,
    player_id: Optional[int] = None,
    team_id: Optional[int] = None,
    exercise_id: Optional[int] = None,
    action_type: Optional[ActionType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    allowed_player_ids: Optional[List[int]] = None,
    allowed_team_ids: Optional[List[int]] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(ActivityLog).options(
        selectinload(ActivityLog.user),
        selectinload(ActivityLog.target_player),
        selectinload(ActivityLog.target_exercise),
        selectinload(ActivityLog.target_team),
    )

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    # Apply access control filters for coaches
    # Note: Logic slightly adjusted to match the intent of "filtering if allowed_ids are provided"
    
    # Logic for allowed_player_ids (Coach view restriction)
    if allowed_player_ids is not None:
        if player_id:
            # If specific player requested, check if allowed
            if player_id not in allowed_player_ids:
                return [] 
            query = query.filter(ActivityLog.target_player_id == player_id)
        elif allowed_player_ids:
            # If no specific player requested, return logs for ANY allowed player
            query = query.filter(ActivityLog.target_player_id.in_(allowed_player_ids))
        else:
            # allowed_player_ids is empty list -> no access to any player logs
            # However, we might still want to return team logs if available.
            # The original logic seemed to return [] immediately if allowed list was empty.
            # But wait, looking at the router, it merges logs.
            # Let's stick to the stricter interpretation: if specific restrictions are passed, they must be met.
            # But problematic if we want mixed results. 
            # The router calls this function twice: once for players/teams, once for own logs.
            # Let's assume if allowed key is present, we filter by it.
             return []


    # Logic for allowed_team_ids
    if allowed_team_ids is not None:
        if team_id:
            if team_id not in allowed_team_ids:
                 return []
            query = query.filter(ActivityLog.target_team_id == team_id)
        elif allowed_team_ids:
             query = query.filter(ActivityLog.target_team_id.in_(allowed_team_ids))
        else:
             return []


    # General filters (only if access control didn't already handle them or wasn't present)
    # The original code had a bug where it would apply filters twice if not careful.
    # But here: if allowed_player_ids IS None (Admin), we check player_id.
    if player_id and allowed_player_ids is None:
        query = query.filter(ActivityLog.target_player_id == player_id)
    
    if team_id and allowed_team_ids is None:
        query = query.filter(ActivityLog.target_team_id == team_id)

    if exercise_id:
        query = query.filter(ActivityLog.target_exercise_id == exercise_id)
    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)
    if date_from:
        query = query.filter(ActivityLog.created_at >= date_from)
    if date_to:
        query = query.filter(ActivityLog.created_at <= date_to)

    result = await db.execute(query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit))
    return result.scalars().all()
