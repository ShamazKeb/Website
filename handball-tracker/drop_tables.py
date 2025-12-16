from app.core.database import engine, Base
# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.team import Team
from app.models.player import Player
from app.models.coach import Coach
from app.models.associations import team_players, team_coaches

def drop_all_tables():
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

if __name__ == "__main__":
    drop_all_tables()
