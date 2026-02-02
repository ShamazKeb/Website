from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    total_remaining = Column(Integer, default=500)
    
    entries = relationship("PushupEntry", back_populates="player")


class PushupEntry(Base):
    __tablename__ = "pushup_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="entries")
