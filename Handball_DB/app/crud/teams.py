from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app import models, schemas


async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[models.Team]:
    """
    Retrieves a single Team by its ID, eagerly loading its players and coaches.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.id == team_id, models.Team.is_active == True)
    )
    return result.scalars().first()


async def get_all_teams(db: AsyncSession) -> List[models.Team]:
    """
    Retrieves all active teams (for Admin).
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.is_active == True)
    )
    return result.scalars().all()


async def get_teams_for_player(db: AsyncSession, player_id: int) -> List[models.Team]:
    """
    Retrieves a list of teams a player is assigned to.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .join(models.team_players)
        .filter(models.team_players.c.player_id == player_id, models.Team.is_active == True)
    )
    return result.scalars().all()


async def get_teams_for_coach(db: AsyncSession, coach_id: int) -> List[models.Team]:
    """
    Retrieves a list of teams a coach is assigned to.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .join(models.team_coaches)
        .filter(models.team_coaches.c.coach_id == coach_id, models.Team.is_active == True)
    )
    return result.scalars().all()


async def create_team(db: AsyncSession, team_in: schemas.TeamCreate) -> models.Team:
    """
    Creates a new team.
    """
    db_team = models.Team(name=team_in.name, season=team_in.season)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team


async def update_team(db: AsyncSession, db_team: models.Team, team_in: schemas.TeamUpdate) -> models.Team:
    """
    Updates an existing team.
    """
    if team_in.name is not None:
        db_team.name = team_in.name
    if team_in.season is not None:
        db_team.season = team_in.season
    await db.commit()
    await db.refresh(db_team)
    return db_team


async def delete_team(db: AsyncSession, db_team: models.Team) -> None:
    """
    Soft deletes a team by setting is_active to False.
    """
    db_team.is_active = False
    await db.commit()


async def add_player_to_team(db: AsyncSession, team_id: int, player_id: int) -> models.Team:
    """
    Adds a player to a team.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.id == team_id)
    )
    team = result.scalars().first()
    
    player_result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    player = player_result.scalars().first()
    
    if player and player not in team.players:
        team.players.append(player)
        await db.commit()
        await db.refresh(team)
    return team


async def remove_player_from_team(db: AsyncSession, team_id: int, player_id: int) -> models.Team:
    """
    Removes a player from a team.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.id == team_id)
    )
    team = result.scalars().first()
    
    player_result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    player = player_result.scalars().first()
    
    if player and player in team.players:
        team.players.remove(player)
        await db.commit()
        await db.refresh(team)
    return team


async def add_coach_to_team(db: AsyncSession, team_id: int, coach_id: int) -> models.Team:
    """
    Adds a coach to a team.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.id == team_id)
    )
    team = result.scalars().first()
    
    coach_result = await db.execute(select(models.Coach).filter(models.Coach.id == coach_id))
    coach = coach_result.scalars().first()
    
    if coach and coach not in team.coaches:
        team.coaches.append(coach)
        await db.commit()
        await db.refresh(team)
    return team


async def remove_coach_from_team(db: AsyncSession, team_id: int, coach_id: int) -> models.Team:
    """
    Removes a coach from a team.
    """
    result = await db.execute(
        select(models.Team)
        .options(selectinload(models.Team.players), selectinload(models.Team.coaches))
        .filter(models.Team.id == team_id)
    )
    team = result.scalars().first()
    
    coach_result = await db.execute(select(models.Coach).filter(models.Coach.id == coach_id))
    coach = coach_result.scalars().first()
    
    if coach and coach in team.coaches:
        team.coaches.remove(coach)
        await db.commit()
        await db.refresh(team)
    return team


async def get_players_in_team(db: AsyncSession, team_id: int) -> List[models.Player]:
    """
    Retrieves a list of players assigned to a specific team.
    """
    result = await db.execute(
        select(models.Player)
        .join(models.team_players)
        .filter(models.team_players.c.team_id == team_id)
    )
    return result.scalars().all()


async def get_coaches_in_team(db: AsyncSession, team_id: int) -> List[models.Coach]:
    """
    Retrieves a list of coaches assigned to a specific team.
    """
    result = await db.execute(
        select(models.Coach)
        .join(models.team_coaches)
        .filter(models.team_coaches.c.team_id == team_id)
    )
    return result.scalars().all()