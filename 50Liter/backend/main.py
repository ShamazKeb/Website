from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import engine, get_db, Base
from models import Player, PushupEntry

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Liegestütz Challenge Tracker", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic schemas
class PushupCreate(BaseModel):
    count: int


class PushupEntryResponse(BaseModel):
    id: int
    count: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PlayerResponse(BaseModel):
    id: int
    name: str
    total_remaining: int
    
    class Config:
        from_attributes = True


class PlayerDetailResponse(PlayerResponse):
    entries: List[PushupEntryResponse] = []


# Routes
@app.get("/api/players", response_model=List[PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    """Get all players with their remaining push-ups"""
    return db.query(Player).order_by(Player.total_remaining).all()


@app.get("/api/players/{player_id}", response_model=PlayerDetailResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get a specific player with their history"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.post("/api/players/{player_id}/pushups", response_model=PlayerResponse)
def add_pushups(player_id: int, pushup: PushupCreate, db: Session = Depends(get_db)):
    """Add push-ups for a player"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if pushup.count <= 0:
        raise HTTPException(status_code=400, detail="Count must be positive")
    
    # Create entry
    entry = PushupEntry(player_id=player_id, count=pushup.count)
    db.add(entry)
    
    # Update remaining count
    player.total_remaining = max(0, player.total_remaining - pushup.count)
    db.commit()
    db.refresh(player)
    
    return player


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall challenge statistics"""
    players = db.query(Player).all()
    total_remaining = sum(p.total_remaining for p in players)
    total_done = sum(500 - p.total_remaining for p in players)
    completed_players = sum(1 for p in players if p.total_remaining == 0)
    
    return {
        "total_players": len(players),
        "total_done": total_done,
        "total_remaining": total_remaining,
        "completed_players": completed_players,
        "challenge_complete": all(p.total_remaining == 0 for p in players)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
