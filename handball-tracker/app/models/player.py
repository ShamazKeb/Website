from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.associations import team_players
import enum

class Hand(str, enum.Enum):
    LINKS = "LINKS"
    RECHTS = "RECHTS"
    BEIDE = "BEIDE"

class Position(str, enum.Enum):
    TW = "TW" # Torwart
    LA = "LA" # Linksaußen
    RL = "RL" # Rückraum Links
    RM = "RM" # Rückraum Mitte
    RR = "RR" # Rückraum Rechts
    RA = "RA" # Rechtsaußen
    KL = "KL" # Kreisläufer

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True) # Linked to login user (optional if managed by coach without login yet?) - User said 1-1 to User, imply nullable=False or True? Phase 1 implies Players have logins. Let's start with True but if they are managed *by* coaches without account, it might be nullable. Plan said 1-1 unique. Let's match plan: ForeignKey("users.id"), unique.
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    year_of_birth = Column(Integer, nullable=True)
    
    hand = Column(Enum(Hand), nullable=True)
    position = Column(Enum(Position), nullable=True)
    
    jersey_number = Column(Integer, nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("app.models.user.User", backref="player_profile")
    teams = relationship("Team", secondary=team_players, back_populates="players")
