from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.dependencies.database import get_db

# NOTE: Using the MAIN database (app.db) as requested.
# We do NOT override get_db. We do NOT drop_all tables.

client = TestClient(app)

def ensure_test_users():
    """
    Ensures that the required test users exist in the main database.
    Does NOT delete existing data.
    """
    # Ensure tables exist (safe to run if they already exist)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    users_to_create = [
        {"email": "admin@test.com", "role": UserRole.ADMIN, "password": "password"},
        {"email": "coach@test.com", "role": UserRole.COACH, "password": "password"},
        {"email": "player@test.com", "role": UserRole.PLAYER, "password": "password"},
    ]
    
    tokens = {}
    
    print("\nEnsuring test users exist...")
    for u_data in users_to_create:
        existing_user = db.query(User).filter(User.email == u_data["email"]).first()
        
        if not existing_user:
            print(f" - Creating {u_data['email']} ({u_data['role']})...")
            new_user = User(
                email=u_data["email"],
                password_hash=get_password_hash(u_data["password"]),
                role=u_data["role"]
            )
            db.add(new_user)
            db.commit() # Commit to generate ID
            db.refresh(new_user)
        else:
            print(f" - Found existing {u_data['email']}. Updating password...")
            existing_user.password_hash = get_password_hash(u_data["password"])
            db.commit()
            
        # Login to get token
        resp = client.post("/auth/login", data={"username": u_data["email"], "password": u_data["password"]})
        if resp.status_code == 200:
            tokens[u_data["role"]] = resp.json()["access_token"]
        else:
            print(f"ERROR: Failed to login as {u_data['email']}: {resp.text}")

    db.close()
    return tokens

def test_rbac():
    tokens = ensure_test_users()
    
    if len(tokens) < 3:
        print("SKIPPING: Could not get tokens for all roles. Check login.")
        return

    admin_token = {"Authorization": f"Bearer {tokens[UserRole.ADMIN]}"}
    coach_token = {"Authorization": f"Bearer {tokens[UserRole.COACH]}"}
    player_token = {"Authorization": f"Bearer {tokens[UserRole.PLAYER]}"}
    
    # 1. Test Admin Endpoint (Only Admin)
    print("Testing /test/admin...")
    assert client.get("/test/admin", headers=admin_token).status_code == 200, "Admin denied access to admin route"
    assert client.get("/test/admin", headers=coach_token).status_code == 403, "Coach allowed access to admin route"
    assert client.get("/test/admin", headers=player_token).status_code == 403, "Player allowed access to admin route"
    print("SUCCESS")

    # 2. Test Coach Endpoint (Admin + Coach)
    print("Testing /test/coach...")
    assert client.get("/test/coach", headers=admin_token).status_code == 200, "Admin denied access to coach route"
    assert client.get("/test/coach", headers=coach_token).status_code == 200, "Coach denied access to coach route"
    assert client.get("/test/coach", headers=player_token).status_code == 403, "Player allowed access to coach route"
    print("SUCCESS")

    # 3. Test Player Endpoint (Only Player - strict)
    print("Testing /test/player...")
    assert client.get("/test/player", headers=player_token).status_code == 200, "Player denied access to player route"
    assert client.get("/test/player", headers=admin_token).status_code == 403, "Admin allowed access to player route (Strict Mode)"
    assert client.get("/test/player", headers=coach_token).status_code == 403, "Coach allowed access to player route (Strict Mode)"
    print("SUCCESS")

if __name__ == "__main__":
    try:
        test_rbac()
        print("\nALL RBAC TESTS PASSED!")
    except AssertionError as e:
        print(f"\nFAILURE: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
