from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import Base
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.team import Team
from app.models.player import Player
from app.models.coach import Coach
from app.schemas.team import TeamCreate, TeamResponse

router = APIRouter(
    prefix="/admin/teams",
    tags=["admin-teams"]
)

@router.post("/", response_model=TeamResponse)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    team = Team(
        name=team_in.name,
        season=team_in.season,
        age_group=team_in.age_group,
        notes=team_in.notes,
        is_active=True
    )
    db.add(team)
    try:
        db.commit()
        db.refresh(team)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name and season already exists."
        )
    return team

@router.post("/{team_id}/players", tags=["admin-teams"])
def assign_players_to_team(
    team_id: int,
    player_ids: List[int],
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    added_ids = []
    already_present_ids = []

    # Pre-fetch players to validate existence
    # Creating a set of existing player IDs in the team for simpler checking
    existing_player_ids = {p.id for p in team.players}

    for pid in player_ids:
        player = db.query(Player).filter(Player.id == pid).first()
        if not player:
            raise HTTPException(status_code=404, detail=f"Player {pid} not found")
        
        if pid in existing_player_ids:
            already_present_ids.append(pid)
        else:
            team.players.append(player)
            added_ids.append(pid)
    
    db.commit()
    
    return {
        "team_id": team.id,
        "added_player_ids": added_ids,
        "already_present": already_present_ids
    }

@router.post("/{team_id}/coaches", tags=["admin-teams"])
def assign_coaches_to_team(
    team_id: int,
    coach_ids: List[int],
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    added_ids = []
    already_present_ids = []

    existing_coach_ids = {c.id for c in team.coaches}

    for cid in coach_ids:
        coach = db.query(Coach).filter(Coach.id == cid).first()
        if not coach:
            raise HTTPException(status_code=404, detail=f"Coach {cid} not found")
        
        if cid in existing_coach_ids:
            already_present_ids.append(cid)
        else:
            team.coaches.append(coach)
            added_ids.append(cid)
    
    db.commit()

    return {
        "team_id": team.id,
        "added_coach_ids": added_ids,
        "already_present": already_present_ids
    }
