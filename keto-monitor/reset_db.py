from app.db import init_db, get_engine, Base
# Import models to ensure they are registered with Base
from app.models import Company, Article, Topic, Summary, TopicArticle

def reset_database():
    print("--- Resetting Database ---")
    engine = get_engine()
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(engine)
        print("Tables dropped.")
    except Exception as e:
        print(f"Error dropping tables (might be locked): {e}")
        return

    print("Re-initializing database...")
    init_db()
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
