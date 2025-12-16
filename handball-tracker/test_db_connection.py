from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.dependencies.database import get_db

def test_connection():
    try:
        # Test 1: Direct Engine Connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Engine Connection Check: {result.scalar()}")
        
        # Test 2: SessionLocal
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print(f"SessionLocal Check: {result.scalar()}")
        db.close()

        # Test 3: get_db dependency
        gen = get_db()
        db_dep = next(gen)
        result = db_dep.execute(text("SELECT 1"))
        print(f"get_db Check: {result.scalar()}")
        try:
            next(gen)
        except StopIteration:
            print("get_db generator closed correctly")
            
        print("SUCCESS: Database connection established!")
        
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_connection()
