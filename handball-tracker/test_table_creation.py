from app.models.base import Base # Import Base before importing models
from app.models.user import User # Import User to register it with Base
from app.core.database import engine
from sqlalchemy import inspect

def test_table_creation():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Existing tables: {tables}")
    
    if "users" in tables:
        print("SUCCESS: 'users' table created.")
        columns = [col['name'] for col in inspector.get_columns("users")]
        print(f"Columns: {columns}")
        expected_cols = ["id", "email", "password_hash", "role", "created_at"]
        if all(col in columns for col in expected_cols):
             print("SUCCESS: All expected columns present.")
        else:
             print(f"FAILURE: Missing columns. Expected {expected_cols}")
    else:
        print("FAILURE: 'users' table not found.")

if __name__ == "__main__":
    test_table_creation()
