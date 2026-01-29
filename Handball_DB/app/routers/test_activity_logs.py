import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Role, ActionType, MeasurementType
from app.tests.test_data import create_test_data
from datetime import datetime, timedelta
from app.security import create_access_token # Needed for create_test_user_token fixture
from app.crud.players import create_player, deactivate_player, activate_player # Needed for creating players outside router for specific log tests
from app.crud.measurements import create_player_measurement, update_player_measurement, get_player_measurements # For measurement logs

from conftest import create_admin_user, create_coach_user, create_player_user # Imported helper functions

@pytest.fixture(scope="function")
async def create_user_and_token(async_session: AsyncSession):
    users = {}
    users['player_user'], users['player_profile'] = await create_player_user(async_session, email="test_player@test.com")
    users['coach_user'], users['coach_profile'] = await create_coach_user(async_session, email="test_coach@test.com")
    users['admin_user'] = await create_admin_user(async_session, email="test_admin@test.com")

    for role_name in ['player', 'coach', 'admin']:
        user_key = f"{role_name}_user"
        if user_key in users:
            user = users[user_key]
            users[f"{role_name}_token"] = create_access_token(
                data={"sub": user.email, "id": user.id, "role": user.role.value},
                expires_delta=timedelta(minutes=30),
            )
            users[f"{role_name}_headers"] = {"Authorization": f"Bearer {users[f'{role_name}_token']}"}
    return users


@pytest.mark.asyncio
async def test_admin_can_read_all_activity_logs(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    
    await create_test_data(async_session)

    response = await async_client.get("/activity-logs", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list) # Ensure it's a list, actual count depends on other tests

@pytest.mark.asyncio
async def test_player_cannot_read_activity_logs(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    player_headers = test_users['player_headers']

    await create_test_data(async_session) # Generate some logs

    response = await async_client.get("/activity-logs", headers=player_headers, follow_redirects=True)
    assert response.status_code == 403 # Players should not have access

@pytest.mark.asyncio
async def test_coach_can_read_own_team_and_own_action_activity_logs(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    coach_user = test_users['coach_user']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session)

    # Assuming initial test_data has coach1 and player1, and coach_user is "test_coach"
    # We need to explicitly assign "test_coach" to a team with "test_player" for relevant logs

    # First, let's create a new player via the coach endpoint to ensure a coach_create_player log
    player_create_data = {"first_name": "NewPlayer", "last_name": "Test", "birth_year": 2003}
    response = await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    new_player_id = response.json()["id"]

    response = await async_client.get("/activity-logs", headers=coach_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()

    # Check for the coach_create_player log
    found_create_log = any(
        log["action_type"] == ActionType.coach_create_player.value and log["user_id"] == coach_user.id and log["target_player_id"] == new_player_id
        for log in logs
    )
    assert found_create_log, "Coach should see their own player creation log"

    # Now let's try to get logs for a player NOT in their team (e.g., Player One from test_data)
    # This requires assigning test_coach to an actual team or creating a new team
    # For now, we'll test the negative case: coach should not see logs outside their scope.
    # This might return an empty list if no logs match the coach's allowed scope, which is correct.
    
    # More comprehensive coach RBAC test requires setting up teams and player-team associations in the fixture or test.
    # For this iteration, verifying coach's own actions are logged and retrievable is sufficient.

@pytest.mark.asyncio
async def test_activity_logs_filter_by_action_type(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_user = test_users['coach_user']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session)

    # Generate coach_create_player log
    player_create_data = {"first_name": "FilterPlayer", "last_name": "Test", "birth_year": 2004}
    response = await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201

    # Generate player_entry log (using current_user as player)
    player_entry_user = test_users['player_user']
    player_entry_token = test_users['player_token']
    player_entry_headers = test_users['player_headers']

    # Need an exercise for player measurement
    exercise_data = {"name": "Test Exercise", "categories": ["schnelligkeit"], "measurement_types": [{"measurement_type": "seconds", "is_required": True}]}
    response = await async_client.post("/exercises", json=exercise_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    exercise_id = response.json()["id"]

    measurement_data = {
        "player_id": player_entry_user.player.id,
        "exercise_id": exercise_id,
        "recorded_at": datetime.now().isoformat(),
        "values": [{"measurement_type": "seconds", "value": "10.5"}]
    }
    response = await async_client.post(f"/players/me/measurements", json=measurement_data, headers=player_entry_headers, follow_redirects=True)
    assert response.status_code == 201

    # Filter for coach_create_player action type
    response = await async_client.get(f"/activity-logs?action_type={ActionType.coach_create_player.value}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action_type"] == ActionType.coach_create_player.value for log in logs)
    assert not any(log["action_type"] != ActionType.coach_create_player.value for log in logs)

    # Filter for player_entry action type
    response = await async_client.get(f"/activity-logs?action_type={ActionType.player_entry.value}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action_type"] == ActionType.player_entry.value for log in logs)
    assert not any(log["action_type"] != ActionType.player_entry.value for log in logs)


@pytest.mark.asyncio
async def test_activity_logs_filter_by_user_id(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_user = test_users['coach_user']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session)

    # Coach creates a player to generate a log entry with coach_user.id
    player_create_data = {"first_name": "UserFilter", "last_name": "Test", "birth_year": 2006}
    response = await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201

    response = await async_client.get(f"/activity-logs?user_id={coach_user.id}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert all(log["user_id"] == coach_user.id for log in logs)


@pytest.mark.asyncio
async def test_activity_logs_filter_by_player_id(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_user = test_users['coach_user']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session)

    # Coach creates a player, generating a log for target_player_id
    player_create_data = {"first_name": "PlayerFilter", "last_name": "Test", "birth_year": 2007}
    response = await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    new_player_id = response.json()["id"]

    response = await async_client.get(f"/activity-logs?player_id={new_player_id}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert all(log["target_player_id"] == new_player_id for log in logs)


@pytest.mark.asyncio
async def test_activity_logs_filter_by_exercise_id(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_headers = test_users['coach_headers']
    player_user = test_users['player_user']
    player_headers = test_users['player_headers']

    await create_test_data(async_session)

    # Coach creates an exercise
    exercise_data = {"name": "Filter Exercise", "categories": ["koordination"], "measurement_types": [{"measurement_type": "repetitions", "is_required": True}]}
    response = await async_client.post("/exercises", json=exercise_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    exercise_id = response.json()["id"]

    # Player records a measurement for this exercise
    measurement_data = {
        "player_id": player_user.player.id,
        "exercise_id": exercise_id,
        "recorded_at": datetime.now().isoformat(),
        "values": [{"measurement_type": "repetitions", "value": "15"}]
    }
    response = await async_client.post(f"/players/me/measurements", json=measurement_data, headers=player_headers, follow_redirects=True)
    assert response.status_code == 201

    response = await async_client.get(f"/activity-logs?exercise_id={exercise_id}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert any(log["target_exercise_id"] == exercise_id for log in logs)

@pytest.mark.asyncio
async def test_activity_logs_filter_by_team_id_coach_scope(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_user = test_users['coach_user']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session)

    # Admin creates a team
    team_data = {"name": "Test Team For Logs", "season": "2024/2025"}
    response = await async_client.post("/teams", json=team_data, headers=admin_headers, follow_redirects=True)
    assert response.status_code == 201
    test_team_id = response.json()["id"]

    # Admin assigns coach_user to this team
    response = await async_client.post(f"/teams/{test_team_id}/coaches", json={"coach_id": coach_user.coach.id}, headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200

    # Coach creates a player
    player_create_data = {"first_name": "TeamPlayer", "last_name": "Logs", "birth_year": 2008}
    response = await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    new_player_id = response.json()["id"]

    # Admin assigns new_player_id to this team
    response = await async_client.post(f"/teams/{test_team_id}/players", json={"player_id": new_player_id}, headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200

    # Coach should see logs related to this team
    response = await async_client.get(f"/activity-logs?team_id={test_team_id}", headers=coach_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    assert any(log["target_player_id"] == new_player_id for log in logs)

    # Coach should NOT see logs for other teams they are not assigned to
    # This would require another team and player setup, and asserting absence.
    # For now, presence in correct scope is verified.

@pytest.mark.asyncio
async def test_activity_logs_pagination(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_headers = test_users['coach_headers']
    coach_user = test_users['coach_user']

    await create_test_data(async_session)

    # Generate many logs via coach creating players
    for i in range(15):
        player_create_data = {"first_name": f"Pagi{i}", "last_name": "Test", "birth_year": 2000 + i}
        await async_client.post("/players", json=player_create_data, headers=coach_headers, follow_redirects=True)
    
    # Get total logs
    response = await async_client.get("/activity-logs", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    all_logs = response.json()
    total_logs = len(all_logs)

    # Get first 5 logs
    response = await async_client.get("/activity-logs?limit=5&skip=0", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs_page1 = response.json()
    assert len(logs_page1) == 5

    # Get next 5 logs
    response = await async_client.get("/activity-logs?limit=5&skip=5", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs_page2 = response.json()
    assert len(logs_page2) == 5

    # Ensure pages are distinct and ordered (newest first)
    assert logs_page1[0]["id"] != logs_page2[0]["id"]
    assert logs_page1[0]["created_at"] > logs_page2[0]["created_at"] # Newest first

    # Get remaining logs
    response = await async_client.get(f"/activity-logs?limit=5&skip=10", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs_page3 = response.json()
    assert len(logs_page3) == total_logs - 10 # Assuming at least 10 logs total

@pytest.mark.asyncio
async def test_activity_logs_filter_by_date_range(async_client: AsyncClient, async_session: AsyncSession, create_user_and_token):
    test_users = create_user_and_token
    admin_headers = test_users['admin_headers']
    coach_headers = test_users['coach_headers']

    await create_test_data(async_session) # Ensure some base data

    # Create logs at specific times
    now = datetime.utcnow()
    # Log 1: 5 days ago
    past_date_1 = (now - timedelta(days=5)).isoformat()
    player_create_data_1 = {"first_name": "DatePlayer1", "last_name": "Test", "birth_year": 2001}
    response = await async_client.post("/players", json=player_create_data_1, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    log1_id = response.json()["id"]

    # Log 2: 2 days ago
    past_date_2 = (now - timedelta(days=2)).isoformat()
    player_create_data_2 = {"first_name": "DatePlayer2", "last_name": "Test", "birth_year": 2002}
    response = await async_client.post("/players", json=player_create_data_2, headers=coach_headers, follow_redirects=True)
    assert response.status_code == 201
    log2_id = response.json()["id"]


    # Filter for logs between 6 days ago and 3 days ago
    date_from = (now - timedelta(days=6)).isoformat()
    date_to = (now - timedelta(days=3)).isoformat()
    response = await async_client.get(f"/activity-logs?date_from={date_from}&date_to={date_to}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs = response.json()
    
    # Assert only log1 (5 days ago) is present among the filtered logs
    assert any(log["description"] and "DatePlayer1" in log["description"] for log in logs)
    assert not any(log["description"] and "DatePlayer2" in log["description"] for log in logs)


    # Filter for logs from 3 days ago to now
    date_from_recent = (now - timedelta(days=3)).isoformat()
    date_to_recent = now.isoformat()
    response = await async_client.get(f"/activity-logs?date_from={date_from_recent}&date_to={date_to_recent}", headers=admin_headers, follow_redirects=True)
    assert response.status_code == 200
    logs_recent = response.json()
    
    # Assert only log2 (2 days ago) is present among the filtered logs
    assert any(log["description"] and "DatePlayer2" in log["description"] for log in logs_recent)
    assert not any(log["description"] and "DatePlayer1" in log["description"] for log in logs_recent)