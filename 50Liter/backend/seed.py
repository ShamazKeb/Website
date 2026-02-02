"""
Seed script to add players to the database.
Run with: python seed.py
"""
from database import SessionLocal, engine, Base
from models import Player

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

def seed_players():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if players already exist
        existing = db.query(Player).count()
        if existing > 0:
            print(f"Database already has {existing} players. Skipping seed.")
            print("To reset, delete pushups.db and run again.")
            return
        
        # Add players
        for name, target in PLAYERS:
            player = Player(name=name, total_remaining=target)
            db.add(player)
        
        db.commit()
        print(f"Successfully added {len(PLAYERS)} players!")
        
        # Show players
        for player in db.query(Player).all():
            print(f"  - {player.name}: {player.total_remaining} remaining")
            
    finally:
        db.close()


if __name__ == "__main__":
    seed_players()

