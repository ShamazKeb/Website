from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app import models, schemas
from app.security import hash_password # For player creation with user


async def create_player(db: AsyncSession, player_in: schemas.PlayerCreate, user_id: int) -> models.Player:
    db_player = models.Player(
        user_id=user_id,
        first_name=player_in.first_name,
        last_name=player_in.last_name,
        birth_year=player_in.birth_year,
    )
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player

async def get_player_by_id(db: AsyncSession, player_id: int) -> Optional[models.Player]:
    result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    return result.scalars().first()

async def get_players(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Player]:
    result = await db.execute(select(models.Player).offset(skip).limit(limit))
    return result.scalars().all()

async def deactivate_player(db: AsyncSession, player: models.Player) -> models.Player:
    player.is_active = False
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player

async def activate_player(db: AsyncSession, player: models.Player) -> models.Player:
    player.is_active = True
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player