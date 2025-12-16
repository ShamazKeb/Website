from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.associations import team_players, team_coaches

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    season = Column(String, nullable=False) # e.g. "25/26"
    age_group = Column(String, nullable=True) # e.g. "C-Jugend"
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    players = relationship("Player", secondary=team_players, back_populates="teams")
    coaches = relationship("Coach", secondary=team_coaches, back_populates="teams")

    __table_args__ = (
        UniqueConstraint('name', 'season', name='uq_team_name_season'),
    )
