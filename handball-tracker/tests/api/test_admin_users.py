import pytest
from app.models.user import User, UserRole
from app.models.player import Player
from app.models.coach import Coach
from app.core.security import create_access_token

def get_auth_headers(email: str):
    access_token = create_access_token(data={"sub": email})
    return {"Authorization": f"Bearer {access_token}"}

def test_admin_create_player(client, db_session):
    admin_email = "admin_users@test.com"
    # Ensure cleanup
    db_session.query(User).filter(User.email == admin_email).delete()
    db_session.commit()
    
    # Create Admin
    admin = User(email=admin_email, role=UserRole.ADMIN, password_hash="dummy")
    db_session.add(admin)
    db_session.commit()
    
    headers = get_auth_headers(admin_email)
    
    player_data = {
        "email": "new_player@test.com",
        "password": "securepassword",
        "first_name": "New",
        "last_name": "Player",
        "year_of_birth": 2005
    }
    
    # Clean potential previous run
    db_session.query(Player).filter(Player.first_name == "New").delete()
    db_session.query(User).filter(User.email == player_data["email"]).delete()
    db_session.commit()
    
    response = client.post(
        "/admin/players",
        json=player_data,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "New"
    assert data["id"] is not None
    assert data["user_id"] is not None
    
    # Verify DB
    created_user = db_session.query(User).filter(User.email == player_data["email"]).first()
    assert created_user is not None
    assert created_user.role == UserRole.PLAYER
    
    created_profile = db_session.query(Player).filter(Player.user_id == created_user.id).first()
    assert created_profile is not None
    assert created_profile.year_of_birth == 2005

def test_admin_create_coach(client, db_session):
    admin_email = "admin_users@test.com"
    # Re-use admin if exists or create new? (Fixture usually better, but simplified here)
    if not db_session.query(User).filter(User.email == admin_email).first():
        admin = User(email=admin_email, role=UserRole.ADMIN, password_hash="dummy")
        db_session.add(admin)
        db_session.commit()
    
    headers = get_auth_headers(admin_email)
    
    coach_data = {
        "email": "new_coach@test.com",
        "password": "securepassword",
        "first_name": "New",
        "last_name": "Coach"
    }
    
    # Clean
    db_session.query(Coach).filter(Coach.first_name == "New").delete()
    db_session.query(User).filter(User.email == coach_data["email"]).delete()
    db_session.commit()
    
    response = client.post(
        "/admin/coaches",
        json=coach_data,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "New"
    
    # Verify DB
    created_user = db_session.query(User).filter(User.email == coach_data["email"]).first()
    assert created_user.role == UserRole.COACH

def test_create_duplicate_user(client, db_session):
    admin_email = "admin_users@test.com"
    
    # Create Admin (Required since DB is wiped per test)
    if not db_session.query(User).filter(User.email == admin_email).first():
        admin = User(email=admin_email, role=UserRole.ADMIN, password_hash="dummy")
        db_session.add(admin)
        db_session.commit()

    headers = get_auth_headers(admin_email)
    
    player_data = {
        "email": "duplicate@test.com",
        "password": "pw",
        "first_name": "Dup",
        "last_name": "Lic"
    }
    
    # Cleanup
    db_session.query(Player).filter(Player.first_name == "Dup").delete()
    db_session.query(User).filter(User.email == "duplicate@test.com").delete()
    db_session.commit()
    
    # First create
    response = client.post("/admin/players", json=player_data, headers=headers)
    assert response.status_code == 200
    
    # Second create (Duplicate)
    response = client.post("/admin/players", json=player_data, headers=headers)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
