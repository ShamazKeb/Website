from sqlalchemy import Table, Column, Integer, ForeignKey
from app.core.database import Base

team_players = Table(
    "team_players",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
)

team_coaches = Table(
    "team_coaches",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("coach_id", Integer, ForeignKey("coaches.id"), primary_key=True),
)
