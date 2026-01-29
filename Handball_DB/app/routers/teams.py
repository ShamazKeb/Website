from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.security import (
    get_current_admin,
    get_current_coach_or_admin,
    verify_coach_has_team_access,
    get_current_user, # Added dependency
)
from app.crud import teams as crud_teams

router = APIRouter(prefix="/teams", tags=["teams"])


# Dependency to get a team by ID
async def get_team_by_id(team_id: int, db: AsyncSession = Depends(get_db)):
    team = await crud_teams.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


@router.post("/", response_model=schemas.Team, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: schemas.TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new team (Admin only).
    """
    db_team = await crud_teams.create_team(db=db, team_in=team_in)
    return db_team


@router.get("/", response_model=List[schemas.Team])
async def read_teams(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user), # Allow any user
):
    """
    Retrieve all teams (Admin/Player) or assigned teams (Coach).
    """
    if current_user.role == models.Role.coach:
        teams = await crud_teams.get_teams_for_coach(db, current_user.coach.id)
    else:  # Admin or Player (Players can see all teams for leaderboards)
        teams = await crud_teams.get_all_teams(db)
    return teams


@router.get("/{team_id}", response_model=schemas.Team)
async def read_team(
    team: models.Team = Depends(get_team_by_id),
    current_user: models.User = Depends(get_current_coach_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve specific team details (Coach/Admin).
    Coach can only access assigned teams.
    """
    if current_user.role == models.Role.coach:
        # Check if the coach has access to this team using the helper from security
        await verify_coach_has_team_access(current_user, team.id, db)
    return team


@router.put("/{team_id}", response_model=schemas.Team)
async def update_team(
    team_update: schemas.TeamUpdate,
    team: models.Team = Depends(get_team_by_id),
    current_admin: models.User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update team name/season (Admin only).
    """
    updated_team = await crud_teams.update_team(db=db, db_team=team, team_in=team_update)
    return updated_team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team: models.Team = Depends(get_team_by_id),
    current_admin: models.User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete or archive team (Admin only).
    Sets is_active to False.
    """
    await crud_teams.delete_team(db=db, db_team=team)
    return


@router.post("/{team_id}/players", response_model=schemas.Team, status_code=status.HTTP_200_OK)
async def add_player_to_team(
    team_id: int,
    player_assignment: schemas.TeamPlayerAssignment,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Add a player to a team (Admin only).
    """
    team = await crud_teams.add_player_to_team(db, team_id, player_assignment.player_id)
    return team


@router.delete("/{team_id}/players/{player_id}", status_code=status.HTTP_200_OK)
async def remove_player_from_team(
    team_id: int,
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Remove a player from a team (Admin only).
    """
    team = await crud_teams.remove_player_from_team(db, team_id, player_id)
    return team


@router.post("/{team_id}/coaches", response_model=schemas.Team, status_code=status.HTTP_200_OK)
async def add_coach_to_team(
    team_id: int,
    coach_assignment: schemas.TeamCoachAssignment,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Add a coach to a team (Admin only).
    """
    team = await crud_teams.add_coach_to_team(db, team_id, coach_assignment.coach_id)
    return team


@router.delete("/{team_id}/coaches/{coach_id}", status_code=status.HTTP_200_OK)
async def remove_coach_from_team(
    team_id: int,
    coach_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Remove a coach from a team (Admin only).
    """
    team = await crud_teams.remove_coach_from_team(db, team_id, coach_id)
    return team


@router.get("/{team_id}/players", response_model=List[schemas.Player])
async def list_team_players(
    team: models.Team = Depends(get_team_by_id),
    current_user: models.User = Depends(get_current_coach_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all players in a team (Coach/Admin).
    Coach must be assigned to team.
    """
    if current_user.role == models.Role.coach:
        await verify_coach_has_team_access(current_user, team.id, db)
    players = await crud_teams.get_players_in_team(db, team.id)
    return players


@router.get("/{team_id}/coaches", response_model=List[schemas.Coach])
async def list_team_coaches(
    team: models.Team = Depends(get_team_by_id),
    current_user: models.User = Depends(get_current_coach_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all coaches in a team (Coach/Admin).
    Coach must be assigned to team.
    """
    if current_user.role == models.Role.coach:
        await verify_coach_has_team_access(current_user, team.id, db)
    coaches = await crud_teams.get_coaches_in_team(db, team.id)
    return coaches

