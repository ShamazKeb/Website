import os
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.player import Player
from app.models.coach import Coach
from app.models.team import Team
from app.models.category import Category
from app.models import associations # Ensure associations are registered
from app.core.security import get_password_hash
from app.core.config import settings

def setup_manual_test():
    # 1. Check for .env
    if not os.path.exists(".env"):
        print("WARNING: .env file not found!")
        print("Please copy .env.example to .env and configure it.")
        print("Continuing might fail if env vars are not set in shell...")
    else:
        print("FOUND: .env file.")

    # 2. Re-create tables (Optional: Comment out if you want to keep existing data)
    # For manual test, let's keep it safe and NOT drop everything by default unless asked.
    # But to ensure the user exists, we might need to be careful.
    # Let's just try to add the user.
    
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    # Create Admin
    admin_email = "admin@test.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        print(f"Creating Admin: {admin_email}")
        admin = User(email=admin_email, password_hash=get_password_hash("password123"), role=UserRole.ADMIN)
        db.add(admin)
        db.commit()
    else:
        print(f"Admin already exists: {admin_email}")

    # Create Coach
    coach_email = "coach@test.com"
    existing_coach = db.query(User).filter(User.email == coach_email).first()
    if not existing_coach:
        print(f"Creating Coach: {coach_email}")
        coach_user = User(email=coach_email, password_hash=get_password_hash("password123"), role=UserRole.COACH)
        db.add(coach_user)
        db.commit()
        
        # Create Coach Profile
        coach_profile = Coach(user_id=coach_user.id, first_name="Test", last_name="Coach")
        db.add(coach_profile)
        db.commit()
        print(f"Coach Profile created (ID: {coach_profile.id})")
    else:
        print(f"Coach already exists: {coach_email}")

    # Create Player
    player_email = "player@test.com"
    existing_player = db.query(User).filter(User.email == player_email).first()
    if not existing_player:
        print(f"Creating Player: {player_email}")
        player_user = User(email=player_email, password_hash=get_password_hash("password123"), role=UserRole.PLAYER)
        db.add(player_user)
        db.commit()
        
        # Create Player Profile
        player_profile = Player(user_id=player_user.id, first_name="Test", last_name="Player", is_active=True)
        db.add(player_profile)
        db.commit()
        print(f"Player Profile created (ID: {player_profile.id})")
    else:
        print(f"Player already exists: {player_email}")

    db.close()
    print("\nREADY FOR MANUAL TESTING:")
    print("1. Run: uvicorn app.main:app --reload")
    print("2. Open: http://127.0.0.1:8000/docs")
    print("3. Use credentials (password123 for all):")
    print(f"   Admin: {admin_email}")
    print(f"   Coach: {coach_email} (ID to assign: Check DB or output)")
    print(f"   Player: {player_email} (ID to assign: Check DB or output)")

    print(f"   Player: {player_email} (ID to assign: Check DB or output)")

    # 4. Seed Categories
    print("Seeding categories...")
    from app.core.seeds import seed_categories
    seed_categories(db)
    
    print("Manual test setup complete!")

if __name__ == "__main__":
    setup_manual_test()
