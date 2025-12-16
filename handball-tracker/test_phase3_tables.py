from app.core.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.team import Team
from app.models.player import Player, Hand, Position
from app.models.coach import Coach
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import sys

def verify_tables():
    print("--- Verifying Phase 3 Tables ---")
    
    # 1. Create Tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    db = SessionLocal()
    
    try:
        # 2. Create a User for Player and Coach
        email_player = "verif_player@test.com"
        email_coach = "verif_coach@test.com"
        
        # Cleanup previous run
        db.query(Player).filter(Player.first_name == "Verif").delete()
        db.query(Coach).filter(Coach.first_name == "Verif").delete()
        db.query(Team).filter(Team.name == "VerifTeam").delete()
        db.query(User).filter(User.email.in_([email_player, email_coach])).delete()
        db.commit()

        user_p = User(email=email_player, role=UserRole.PLAYER, password_hash="dummy")
        user_c = User(email=email_coach, role=UserRole.COACH, password_hash="dummy")
        db.add_all([user_p, user_c])
        db.commit()
        db.refresh(user_p)
        db.refresh(user_c)
        print(f"Users created: {user_p.id}, {user_c.id}")

        # 3. Create Player Profile
        player = Player(
            user_id=user_p.id,
            first_name="Verif",
            last_name="Player",
            year_of_birth=2010,
            hand=Hand.RECHTS,
            position=Position.LA,
            jersey_number=10,
            notes="Test Note"
        )
        db.add(player)
        db.commit()
        print("Player profile created.")

        # 4. Create Coach Profile
        coach = Coach(
            user_id=user_c.id,
            first_name="Verif",
            last_name="Coach",
            phone_number="123456"
        )
        db.add(coach)
        db.commit()
        print("Coach profile created.")

        # 5. Create Team
        team1 = Team(name="VerifTeam", season="24/25", age_group="C-Jugend")
        db.add(team1)
        db.commit()
        print("Team 1 created.")
        
        # 6. Test Team Unique Constraint (name + season)
        print("Testing Team Unique Constraint...")
        try:
            team_dup = Team(name="VerifTeam", season="24/25", age_group="Duplicate")
            db.add(team_dup)
            db.commit()
            print("ERROR: Duplicate team created! Constraint failed.")
        except IntegrityError:
            db.rollback()
            print("SUCCESS: Duplicate team prevented.")
            
        # 7. Test allowed same name different season
        team2 = Team(name="VerifTeam", season="25/26", age_group="C-Jugend")
        db.add(team2)
        db.commit()
        print("SUCCESS: Same team name in new season allowed.")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_tables()
