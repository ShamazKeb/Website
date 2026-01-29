import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models
from app.security import hash_password
from conftest import create_player_user, create_coach_user


@pytest.mark.asyncio
async def test_read_admin_dashboard(async_client: AsyncClient, get_admin_token: str):
    response = await async_client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert "total_users" in response.json()
    assert "total_teams" in response.json()
    assert "total_players" in response.json()
    assert "total_coaches" in response.json()
    assert "total_measurements" in response.json()
    assert "users_by_role" in response.json()

@pytest.mark.asyncio
async def test_get_all_users(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # Create some test users
    await async_client.post(
        "/admin/users",
        json={"email": "player_admin_test@test.com", "password": "password", "role": "player"},
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    await async_client.post(
        "/admin/users",
        json={"email": "coach_admin_test@test.com", "password": "password", "role": "coach"},
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )

    response = await async_client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 3 # admin, plus the two new ones

@pytest.mark.asyncio
async def test_create_user_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    new_user_data = {"email": "newuser@test.com", "password": "newpassword", "role": "player"}
    response = await async_client.post(
        "/admin/users",
        json=new_user_data,
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]
    assert "id" in created_user

    # Verify player entry was created
    player_result = await async_session.execute(select(models.Player).filter(models.Player.user_id == created_user["id"]))
    player_entry = player_result.scalars().first()
    assert player_entry is not None
    assert player_entry.user_id == created_user["id"]

@pytest.mark.asyncio
async def test_create_user_admin_existing_email(async_client: AsyncClient, get_admin_token: str):
    new_user_data = {"email": "existing@test.com", "password": "password", "role": "player"}
    await async_client.post(
        "/admin/users",
        json=new_user_data,
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    response = await async_client.post(
        "/admin/users",
        json=new_user_data,
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_user_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # First, create a user to update
    create_response = await async_client.post(
        "/admin/users",
        json={"email": "updateuser@test.com", "password": "oldpassword", "role": "player"},
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    user_id_to_update = create_response.json()["id"]

    # Update user's email and role
    update_data = {"email": "updateduser@test.com", "role": "coach"}
    response = await async_client.put(
        f"/admin/users/{user_id_to_update}",
        json=update_data,
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == update_data["email"]
    assert updated_user["role"] == update_data["role"]

    # Verify password update (by trying to login with new password)
    # Note: password is not returned in UserResponse, so we can't directly check it
    # We would typically test this by trying to log in with the updated password.
    # For simplicity, we'll skip login test for now.
    password_update_data = {"password": "newstrongpassword"}
    password_update_response = await async_client.put(
        f"/admin/users/{user_id_to_update}",
        json=password_update_data,
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert password_update_response.status_code == 200

@pytest.mark.asyncio
async def test_delete_user_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # Create a player user
    create_player_response = await async_client.post(
        "/admin/users",
        json={"email": "player_to_delete@test.com", "password": "password", "role": "player"},
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    player_user_id = create_player_response.json()["id"]

    # Delete (deactivate) the player user
    delete_response = await async_client.delete(
        f"/admin/users/{player_user_id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert delete_response.status_code == 204

    # Verify player is marked as inactive
    player_result = await async_session.execute(select(models.Player).filter(models.Player.user_id == player_user_id))
    player_entry = player_result.scalars().first()
    assert player_entry is not None
    assert player_entry.is_active == False

    # Create a coach user
    create_coach_response = await async_client.post(
        "/admin/users",
        json={"email": "coach_to_delete@test.com", "password": "password", "role": "coach"},
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    coach_user_id = create_coach_response.json()["id"]

    # Delete the coach user (should remove the coach entry)
    delete_coach_response = await async_client.delete(
        f"/admin/users/{coach_user_id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert delete_coach_response.status_code == 204

    # Verify coach entry is removed
    coach_result = await async_session.execute(select(models.Coach).filter(models.Coach.user_id == coach_user_id))
    coach_entry = coach_result.scalars().first()
    assert coach_entry is None


# Admin Team Management Tests
@pytest.mark.asyncio
async def test_get_all_teams_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # Create a test team (using a direct session operation since we don't have a public endpoint for team creation yet)
    team1 = models.Team(name="Team A", season="2024")
    async_session.add(team1)
    await async_session.commit()
    await async_session.refresh(team1)

    response = await async_client.get(
        "/admin/teams",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) >= 1
    assert any(team["name"] == "Team A" for team in teams)


@pytest.mark.asyncio
async def test_add_remove_player_to_team_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # Create team, player
    team = models.Team(name="Test Team Player", season="2025")
    async_session.add(team)
    await async_session.commit()
    await async_session.refresh(team)

    player_user, player_entry = await create_player_user(async_session, email="player_for_team@test.com")

    # Add player to team
    add_response = await async_client.post(
        f"/admin/teams/{team.id}/add_player/{player_entry.id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert add_response.status_code == 200
    updated_team = add_response.json()
    assert any(p["id"] == player_entry.id for p in updated_team["players"])

    # Remove player from team
    remove_response = await async_client.delete(
        f"/admin/teams/{team.id}/remove_player/{player_entry.id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert remove_response.status_code == 200
    updated_team_after_remove = remove_response.json()
    assert not any(p["id"] == player_entry.id for p in updated_team_after_remove["players"])


@pytest.mark.asyncio
async def test_add_remove_coach_to_team_admin(async_client: AsyncClient, get_admin_token: str, async_session: AsyncSession):
    # Create team, coach
    team = models.Team(name="Test Team Coach", season="2026")
    async_session.add(team)
    await async_session.commit()
    await async_session.refresh(team)

    coach_user, coach_entry = await create_coach_user(async_session, email="coach_for_team@test.com")

    # Add coach to team
    add_response = await async_client.post(
        f"/admin/teams/{team.id}/add_coach/{coach_entry.id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert add_response.status_code == 200
    updated_team = add_response.json()
    assert any(c["id"] == coach_entry.id for c in updated_team["coaches"])

    # Remove coach from team
    remove_response = await async_client.delete(
        f"/admin/teams/{team.id}/remove_coach/{coach_entry.id}",
        headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert remove_response.status_code == 200
    updated_team_after_remove = remove_response.json()
    assert not any(c["id"] == coach_entry.id for c in updated_team_after_remove["coaches"])
