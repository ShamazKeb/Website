from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import engine, get_db, Base, SessionLocal
from models import Player, PushupEntry

# Create tables
Base.metadata.create_all(bind=engine)

# Team members with their push-up targets
PLAYERS = [
    ("Andilaus", 1000),  # Trainer-Challenge!
    ("Brutus", 500),
    ("Doro", 500),
    ("Friedi", 500),
    ("Fabi", 500),
    ("Johann", 500),
    ("Justin", 500),
    ("Konrad", 500),
    ("Loddar", 500),
    ("Niek", 500),
    ("Nils", 500),
    ("Archie", 500),
    ("Forest", 500),
    ("Ross", 500),
    ("Simson", 500),
    ("Tobi", 500),
    ("Sandro", 500),
    ("Dewies", 500),
    ("Leo", 500),
    ("Micky", 500),
    ("Robert", 500),
    ("Vale", 500),
]

def seed_if_empty():
    """Auto-seed players if database is empty"""
    db = SessionLocal()
    try:
        if db.query(Player).count() == 0:
            print("Seeding players...")
            for name, target in PLAYERS:
                player = Player(name=name, total_remaining=target)
                db.add(player)
            db.commit()
            print(f"Added {len(PLAYERS)} players!")
    finally:
        db.close()

# Auto-seed on startup
seed_if_empty()

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


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    done: int
    target: int
    remaining: int
    percentage: float
    completed: bool


# Routes
@app.get("/api/players", response_model=List[PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    """Get all players with their remaining push-ups"""
    return db.query(Player).order_by(Player.total_remaining).all()


@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """Get leaderboard sorted by completion percentage"""
    players = db.query(Player).all()
    
    # Calculate stats for each player
    leaderboard = []
    for p in players:
        # Determine original target (Andilaus has 1000, others 500)
        target = 1000 if p.name == "Andilaus" else 500
        done = target - p.total_remaining
        percentage = (done / target) * 100 if target > 0 else 0
        
        leaderboard.append({
            "name": p.name,
            "done": done,
            "target": target,
            "remaining": p.total_remaining,
            "percentage": round(percentage, 1),
            "completed": p.total_remaining == 0
        })
    
    # Sort by percentage (descending)
    leaderboard.sort(key=lambda x: x["percentage"], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return leaderboard


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
    total_target = sum(1000 if p.name == "Andilaus" else 500 for p in players)
    total_remaining = sum(p.total_remaining for p in players)
    total_done = total_target - total_remaining
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
