import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Role, Player, Coach, Team
from app import schemas
from conftest import ( # Import from conftest
    async_session, # Changed from db_session
    async_client,  # Changed from client_fixture
    create_test_user_token,
    create_admin_user, # Now helper function
    create_coach_user, # Now helper function
    create_player_user, # Now helper function
    get_admin_token,
    get_coach_token,
    get_player_token,
)


class TestTeamManagement:
    @pytest.mark.asyncio
    async def test_create_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team Alpha", "season": "2023-2024"},
            follow_redirects=True
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Team Alpha"
        assert data["season"] == "2023-2024"
        assert data["is_active"] == True

    @pytest.mark.asyncio
    async def test_create_team_coach_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_coach_token: str):
        coach_token = get_coach_token # This is now a string, not a callable
        response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"name": "Team Beta", "season": "2023-2024"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_team_player_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_player_token: str):
        player_token = get_player_token # This is now a string, not a callable
        response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {player_token}"},
            json={"name": "Team Gamma", "season": "2023-2024"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_all_teams_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        await create_admin_user(async_session, email="admin_for_teams@test.com")
        await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team A", "season": "2023-2024"},
            follow_redirects=True
        )
        await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team B", "season": "2023-2024"},
            follow_redirects=True
        )

        response = await async_client.get(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(t["name"] == "Team A" for t in data)
        assert any(t["name"] == "Team B" for t in data)

    @pytest.mark.asyncio
    async def test_get_assigned_teams_coach(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session)
        coach_token = get_coach_token # This is now a string, not a callable

        # Create teams
        team1_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team C", "season": "2023-2024"},
            follow_redirects=True
        )
        team1_id = team1_response.json()["id"]

        team2_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team D", "season": "2023-2024"},
            follow_redirects=True
        )
        team2_id = team2_response.json()["id"]

        # Assign coach to team1
        await async_client.post(
            f"/teams/{team1_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )

        response = await async_client.get(
            "/teams", headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Team C"
        assert data[0]["id"] == team1_id

    @pytest.mark.asyncio
    async def test_get_team_details_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team E", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.get(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Team E"
        assert data["season"] == "2023-2024"

    @pytest.mark.asyncio
    async def test_get_team_details_coach_assigned(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_assigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team F", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )

        response = await async_client.get(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Team F"
        assert any(c["id"] == coach_profile.id for c in data["coaches"])

    @pytest.mark.asyncio
    async def test_get_team_details_coach_unassigned_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, _ = await create_coach_user(async_session, email="coach_unassigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team G", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.get(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Old Name", "season": "2022-2023"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        update_response = await async_client.put(
            f"/teams/{team_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "New Name", "season": "2023-2024"},
            follow_redirects=True
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "New Name"
        assert data["season"] == "2023-2024"

    @pytest.mark.asyncio
    async def test_update_team_coach_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_token = get_coach_token # This is now a string, not a callable
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team H", "season": "2022-2023"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.put(
            f"/teams/{team_id}",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"name": "Attempt Update", "season": "2023-2024"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_deactivate_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team I", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.delete(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 204

        # Verify team is deactivated (not found in active list)
        get_response = await async_client.get(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert get_response.status_code == 404

        all_teams_response = await async_client.get(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert all_teams_response.status_code == 200
        data = all_teams_response.json()
        assert not any(t["id"] == team_id for t in data)

    @pytest.mark.asyncio
    async def test_deactivate_team_coach_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, _ = await create_coach_user(async_session, email="forbidden_coach@example.com")
        coach_token = get_coach_token # This is now a string, not a callable
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team J", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.delete(
            f"/teams/{team_id}", headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_add_player_to_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        player_user, player_profile = await create_player_user(async_session, email="player_to_add@example.com")
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team K", "season": "2023-2023"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.post(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert any(p["id"] == player_profile.id for p in data["players"])

    @pytest.mark.asyncio
    async def test_add_player_to_team_coach_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_token = get_coach_token # This is now a string, not a callable
        player_user, player_profile = await create_player_user(async_session, email="player_to_add_coach@example.com")
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team L", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.post(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_remove_player_from_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        player_user, player_profile = await create_player_user(async_session, email="player_to_remove@example.com")
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team M", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )

        response = await async_client.delete(
            f"/teams/{team_id}/players/{player_profile.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert not any(p["id"] == player_profile.id for p in data["players"])

    @pytest.mark.asyncio
    async def test_add_coach_to_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_to_add@example.com")
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team N", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        response = await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert any(c["id"] == coach_profile.id for c in data["coaches"])

    @pytest.mark.asyncio
    async def test_remove_coach_from_team_admin(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_to_remove@example.com")
        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team O", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )

        response = await async_client.delete(
            f"/teams/{team_id}/coaches/{coach_profile.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert not any(c["id"] == coach_profile.id for c in data["coaches"])

    @pytest.mark.asyncio
    async def test_get_players_in_team_coach_assigned(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_players_assigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable
        player_user, player_profile = await create_player_user(async_session, email="player_in_team@example.com")

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team P", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )
        await async_client.post(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )

        response = await async_client.get(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == player_profile.id

    @pytest.mark.asyncio
    async def test_get_players_in_team_coach_unassigned_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, _ = await create_coach_user(async_session, email="coach_players_unassigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable
        player_user, player_profile = await create_player_user(async_session, email="player_not_in_team@example.com")

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team Q", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )

        response = await async_client.get(
            f"/teams/{team_id}/players",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_coaches_in_team_coach_assigned(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_coaches_assigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable
        coach_user_other, coach_profile_other = await create_coach_user(async_session, email="another_coach@example.com")

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team R", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile.id},
            follow_redirects=True
        )
        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile_other.id},
            follow_redirects=True
        )

        response = await async_client.get(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(c["id"] == coach_profile.id for c in data)
        assert any(c["id"] == coach_profile_other.id for c in data)

    @pytest.mark.asyncio
    async def test_player_can_belong_to_multiple_teams(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session, email="player_multi_team@example.com")

        team1_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Multi Team 1", "season": "2023-2024"},
            follow_redirects=True
        )
        team1_id = team1_response.json()["id"]

        team2_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Multi Team 2", "season": "2023-2024"},
            follow_redirects=True
        )
        team2_id = team2_response.json()["id"]

        # Add player to Team 1
        await async_client.post(
            f"/teams/{team1_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )
        # Add player to Team 2
        await async_client.post(
            f"/teams/{team2_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"player_id": player_profile.id},
            follow_redirects=True
        )

        # Verify player is in Team 1
        response1 = await async_client.get(
            f"/teams/{team1_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert any(p["id"] == player_profile.id for p in data1)

        # Verify player is in Team 2
        response2 = await async_client.get(
            f"/teams/{team2_id}/players",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert any(p["id"] == player_profile.id for p in data2)



    @pytest.mark.asyncio
    async def test_get_coaches_in_team_coach_unassigned_forbidden(self, async_client: AsyncClient, async_session: AsyncSession, get_admin_token: str, get_coach_token: str):
        admin_token = get_admin_token # This is now a string, not a callable
        coach_user, _ = await create_coach_user(async_session, email="coach_coaches_unassigned@example.com")
        coach_token = get_coach_token # This is now a string, not a callable
        coach_user_other, coach_profile_other = await create_coach_user(async_session, email="another_coach@example.com")

        team_response = await async_client.post(
            "/teams",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Team S", "season": "2023-2024"},
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"coach_id": coach_profile_other.id},
            follow_redirects=True
        )

        response = await async_client.get(
            f"/teams/{team_id}/coaches",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403