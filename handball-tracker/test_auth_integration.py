from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.dependencies.database import get_db

# NOTE: Using the MAIN database (app.db) as requested.
# SAFE MODE: We do NOT drop existing tables. We only ensure test user exists.

client = TestClient(app)

def setup_test_user():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    email = "test@example.com"
    password = "password"
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Creating test user {email}...")
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.PLAYER # Default to player for basic auth test
        )
        db.add(user)
        db.commit()
    else:
        print(f"Test user {email} exists. Updating password...")
        user.password_hash = get_password_hash(password)
        db.commit()
        
    db.close()

def test_auth_flow():
    setup_test_user()
    
    # 1. Login
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    
    # 2. Access Protected Route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    
    # 3. Access with Invalid Token
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    
    print("Auth Integration Test Passed!")

if __name__ == "__main__":
    test_auth_flow()
