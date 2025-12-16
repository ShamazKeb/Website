import pytest
from app.models.user import User, UserRole
from app.models.team import Team
from app.models.player import Player
from app.models.coach import Coach
from app.core.security import create_access_token
from app.core.database import SessionLocal

# Helper to get headers
def get_auth_headers(email: str):
    access_token = create_access_token(data={"sub": email})
    return {"Authorization": f"Bearer {access_token}"}

def test_admin_create_team(client, db_session):
    # Setup Admin
    admin_email = "admin_teams@test.com"
    # Ensure cleanup
    db_session.query(User).filter(User.email == admin_email).delete()
    db_session.commit()
    
    user = User(email=admin_email, role=UserRole.ADMIN, password_hash="dummy")
    db_session.add(user)
    db_session.commit()
    
    headers = get_auth_headers(admin_email)
    
    response = client.post(
        "/admin/teams/",
        json={"name": "Test Team Alpha", "season": "24/25"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Team Alpha"
    assert data["id"] is not None

def test_coach_cannot_create_team(client, db_session):
    coach_email = "coach_teams@test.com"
    db_session.query(User).filter(User.email == coach_email).delete()
    db_session.commit()
    
    user = User(email=coach_email, role=UserRole.COACH, password_hash="dummy")
    db_session.add(user)
    db_session.commit()
    
    headers = get_auth_headers(coach_email)
    
    response = client.post(
        "/admin/teams/",
        json={"name": "Coach Attempt", "season": "24/25"},
        headers=headers
    )
    assert response.status_code == 403

def test_assign_player_to_team(client, db_session):
    # Setup Data
    admin_email = "admin_assign@test.com"
    player_email = "player_assign@test.com"
    
    # Cleanup
    db_session.query(Player).filter(Player.first_name == "Assign").delete()
    db_session.query(Team).filter(Team.name == "Assign Team").delete()
    db_session.query(User).filter(User.email.in_([admin_email, player_email])).delete()
    db_session.commit()
    
    # Create Admin
    admin = User(email=admin_email, role=UserRole.ADMIN, password_hash="dummy")
    
    # Create Player User + Profile
    p_user = User(email=player_email, role=UserRole.PLAYER, password_hash="dummy")
    db_session.add(admin)
    db_session.add(p_user)
    db_session.commit()
    
    player = Player(user_id=p_user.id, first_name="Assign", last_name="Player", is_active=True)
    db_session.add(player)
    
    # Create Team
    team = Team(name="Assign Team", season="24/25")
    db_session.add(team)
    db_session.commit()
    
    headers = get_auth_headers(admin_email)
    
    # Initial check
    assert len(team.players) == 0
    
    # Test Assignment
    response = client.post(
        f"/admin/teams/{team.id}/players",
        json=[player.id],
        headers=headers
    )
    assert response.status_code == 200
    out = response.json()
    assert player.id in out["added_player_ids"]
    
    # Verify DB
    db_session.refresh(team)
    assert len(team.players) == 1
    assert team.players[0].id == player.id

