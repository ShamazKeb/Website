from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Setup Test Client
client = TestClient(app)

def setup_test_db():
    # Helper to clean and init DB
    # WARNING: This uses the configured database. Ensure it is a test DB or local dev DB.
    # verify we are using sqlite local
    from app.core.config import settings
    print(f"Using DB: {settings.DATABASE_URL}")
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create Test User
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        role=UserRole.PLAYER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

def test_login_flow():
    setup_test_db()
    
    # Test 1: Successful Login
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    if response.status_code == 200:
        print("SUCCESS: Login successful (200 OK)")
        data = response.json()
        if "access_token" in data and data["token_type"] == "bearer":
             print("SUCCESS: Token received.")
        else:
             print(f"FAILURE: Invalid token response: {data}")
    else:
        print(f"FAILURE: Login failed. Status: {response.status_code}, Body: {response.text}")

    # Test 2: Wrong Password
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    if response.status_code == 401:
        print("SUCCESS: Wrong password rejected (401 Unauthorized)")
    else:
        print(f"FAILURE: Wrong password accepted? Status: {response.status_code}")

    # Test 3: Non-existent User
    response = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "testpassword"}
    )
    if response.status_code == 401:
        print("SUCCESS: Unknown user rejected (401 Unauthorized)")
    else:
        print(f"FAILURE: Unknown user accepted? Status: {response.status_code}")

if __name__ == "__main__":
    test_login_flow()
