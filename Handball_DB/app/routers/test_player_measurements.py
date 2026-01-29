import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, get_db
from main import app
from app.models import User, Role, Player, Coach, Team, Exercise, MeasurementType, ExerciseCategoryLink, MeasurementTypeLink
from app.security import (
    create_access_token,
    ALGORITHM,
    SECRET_KEY,
)
from datetime import timedelta, datetime
from typing import List, Optional
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select

from conftest import ( # Import from conftest
    async_session,
    async_client,
    create_admin_user, # Now helper function
    create_coach_user, # Now helper function
    create_player_user, # Now helper function
    get_admin_token,
    get_coach_token,
    get_player_token,
)

async def create_exercise(db: AsyncSession, coach_user_id: int, name: str = "Test Exercise", measurement_types: List[MeasurementType] = None):
    if measurement_types is None:
        measurement_types = [MeasurementType.repetitions] # Default

    exercise = Exercise(owner_coach_id=coach_user_id, name=name, description="A test exercise")
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)

    for mt in measurement_types:
        mt_link = MeasurementTypeLink(exercise_id=exercise.id, measurement_type=mt, is_required=True)
        db.add(mt_link)
    await db.commit()
    await db.refresh(exercise)
    return exercise


class TestPlayerMeasurements:
    @pytest.mark.asyncio
    async def test_record_measurement_player_self_access(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session)
        player_token = get_player_token

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Good performance",
            "values": [{"measurement_type": "repetitions", "value": "10"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {player_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 201
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert data["exercise_id"] == exercise.id
        assert any(v["measurement_type"] == "repetitions" and v["value"] == "10" for v in data["values"])

    @pytest.mark.asyncio
    async def test_record_measurement_player_other_player_forbidden(self, async_client, async_session, get_player_token: str):
        player_user1, _ = await create_player_user(async_session, email="player1@example.com")
        player_token1 = get_player_token
        player_user2, player_profile2 = await create_player_user(async_session, email="player2@example.com")

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile2.id, # Player 1 trying to record for Player 2
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Attempt for another player",
            "values": [{"measurement_type": "repetitions", "value": "5"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {player_token1}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_record_measurement_coach_for_team_player(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_user = await create_admin_user(async_session)
        coach_user, coach_profile = await create_coach_user(async_session)
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session)

        # Create a team and assign coach and player
        team_data = {"name": "Coach Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {get_admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {get_admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {get_admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.kilograms])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach recorded",
            "values": [{"measurement_type": "kilograms", "value": "100"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {coach_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 201
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert data["exercise_id"] == exercise.id
        assert any(v["measurement_type"] == "kilograms" and v["value"] == "100" for v in data["values"])

    @pytest.mark.asyncio
    async def test_record_measurement_coach_for_non_team_player_forbidden(self, async_client, async_session, get_coach_token: str):
        coach_user, _ = await create_coach_user(async_session, email="coach_no_access@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_no_access@example.com")

        coach_other, _ = await create_coach_user(async_session, email="other_coach@example.com")
        exercise = await create_exercise(async_session, coach_other.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach recorded",
            "values": [{"measurement_type": "repetitions", "value": "10"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {coach_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_record_measurement_admin_for_any_player(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session)

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Admin recorded",
            "values": [{"measurement_type": "seconds", "value": "60"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_record_measurement_missing_required_type(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session)

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions, MeasurementType.kilograms])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Missing type",
            "values": [{"measurement_type": "repetitions", "value": "10"}], # Missing kilograms
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 400
        assert "Missing required measurement types: kilograms" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_record_measurement_unknown_type(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session)

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Unknown type",
            "values": [{"measurement_type": "repetitions", "value": "10"}, {"measurement_type": "unknown", "value": "5"}],
        }

        response = await async_client.post(
            "/measurements",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 400
        assert "Unknown measurement types for this exercise: unknown" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_measurements_admin(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session)
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Admin lists",
            "values": [{"measurement_type": "repetitions", "value": "10"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(d["player_id"] == player_profile.id for d in data)

    @pytest.mark.asyncio
    async def test_list_measurements_coach_assigned_player(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session)
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session)

        team_data = {"name": "Coach Team List", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach list test",
            "values": [{"measurement_type": "repetitions", "value": "15"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get(
            f"/measurements?player_id={player_profile.id}",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(d["player_id"] == player_profile.id for d in data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_my_measurements_player_access(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_me_access@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Player's own measurement",
            "values": [{"measurement_type": "repetitions", "value": "10"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {player_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get(
            "/players/me/measurements",
            headers={"Authorization": f"Bearer {player_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(d["player_id"] == player_profile.id for d in data)

    @pytest.mark.asyncio
    async def test_record_my_measurement_player_access(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_record_me@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Player recording own measurement",
            "values": [{"measurement_type": "repetitions", "value": "12"}],
        }

        response = await async_client.post(
            "/players/me/measurements",
            headers={"Authorization": f"Bearer {player_token}"},
            json=measurement_data,
            follow_redirects=True
        )
        assert response.status_code == 201
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert data["exercise_id"] == exercise.id
        assert any(v["measurement_type"] == "repetitions" and v["value"] == "12" for v in data["values"])

    @pytest.mark.asyncio
    async def test_get_player_stats_across_exercises_player_self_access(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_stats_me@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, name="Running", measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Stats test",
            "values": [{"measurement_type": "seconds", "value": "60"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {player_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get(
            f"/players/{player_profile.id}/stats",
            headers={"Authorization": f"Bearer {player_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert str(exercise.id) in data["stats_by_exercise"]
        assert data["stats_by_exercise"][str(exercise.id)]["exercise_name"] == "Running"
        assert data["stats_by_exercise"][str(exercise.id)]["measurement_type_stats"]["seconds"]["average"] == 60.0

    @pytest.mark.asyncio
    async def test_get_player_stats_across_exercises_player_other_forbidden(self, async_client, async_session, get_player_token: str):
        player_user1, _ = await create_player_user(async_session, email="player_stats_forbidden1@example.com")
        player_token1 = get_player_token
        player_user2, player_profile2 = await create_player_user(async_session, email="player_stats_forbidden2@example.com")

        response = await async_client.get(
            f"/players/{player_profile2.id}/stats",
            headers={"Authorization": f"Bearer {player_token1}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_player_stats_across_exercises_coach_access(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_stats_access@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_stats_access_by_coach@example.com")

        team_data = {"name": "Stats Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        coach_other, _ = await create_coach_user(async_session, email="other_coach_for_exercise@example.com")
        exercise = await create_exercise(async_session, coach_other.id, name="Pushups", measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach access stats test",
            "values": [{"measurement_type": "repetitions", "value": "20"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {coach_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get(
            f"/players/{player_profile.id}/stats",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert str(exercise.id) in data["stats_by_exercise"]
        assert data["stats_by_exercise"][str(exercise.id)]["exercise_name"] == "Pushups"
        assert data["stats_by_exercise"][str(exercise.id)]["measurement_type_stats"]["repetitions"]["average"] == 20.0

    @pytest.mark.asyncio
    async def test_get_player_stats_across_exercises_admin_access(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session, email="player_stats_admin_access@example.com")

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, name="Jumps", measurement_types=[MeasurementType.centimeters])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Admin access stats test",
            "values": [{"measurement_type": "centimeters", "value": "180"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)

        response = await async_client.get(
            f"/players/{player_profile.id}/stats",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_profile.id
        assert str(exercise.id) in data["stats_by_exercise"]
        assert data["stats_by_exercise"][str(exercise.id)]["exercise_name"] == "Jumps"
        assert data["stats_by_exercise"][str(exercise.id)]["measurement_type_stats"]["centimeters"]["average"] == 180.0

    @pytest.mark.asyncio
    async def test_get_single_measurement_player_access(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_get_single@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Single measurement test",
            "values": [{"measurement_type": "seconds", "value": "30"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {player_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.get(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {player_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == measurement_id
        assert data["player_id"] == player_profile.id

    @pytest.mark.asyncio
    async def test_get_single_measurement_player_other_forbidden(self, async_client, async_session, get_player_token: str, get_admin_token: str):
        player_user1, player_profile1 = await create_player_user(async_session, email="player_get_single_forbidden1@example.com")
        player_token1 = get_player_token
        player_user2, player_profile2 = await create_player_user(async_session, email="player_get_single_forbidden2@example.com")
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile2.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Single measurement test forbidden",
            "values": [{"measurement_type": "seconds", "value": "45"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {get_admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.get(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {player_token1}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_single_measurement_coach_access(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_get_single@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_get_single_by_coach@example.com")

        team_data = {"name": "Single Meas Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        coach_other, _ = await create_coach_user(async_session, email="other_coach_single_meas@example.com")
        exercise = await create_exercise(async_session, coach_other.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach gets single measurement",
            "values": [{"measurement_type": "repetitions", "value": "25"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.get(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == measurement_id
        assert data["player_id"] == player_profile.id

    @pytest.mark.asyncio
    async def test_update_single_measurement_coach_access(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_update_access@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_update_by_coach@example.com")

        team_data = {"name": "Update Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        coach_other, _ = await create_coach_user(async_session, email="other_coach_update_meas@example.com")
        exercise = await create_exercise(async_session, coach_other.id, measurement_types=[MeasurementType.kilograms])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Original note",
            "values": [{"measurement_type": "kilograms", "value": "50"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        update_data = {
            "notes": "Updated note by coach",
            "values": [{"measurement_type": "kilograms", "value": "55"}],
        }
        response = await async_client.put(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {coach_token}"},
            json=update_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == measurement_id
        assert data["notes"] == "Updated note by coach"
        assert any(v["measurement_type"] == "kilograms" and v["value"] == "55" for v in data["values"])

    @pytest.mark.asyncio
    async def test_update_single_measurement_admin_access(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session, email="player_update_by_admin@example.com")
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Original note admin",
            "values": [{"measurement_type": "seconds", "value": "70"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        update_data = {
            "notes": "Updated note by admin",
            "values": [{"measurement_type": "seconds", "value": "65"}],
        }
        response = await async_client.put(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == measurement_id
        assert data["notes"] == "Updated note by admin"
        assert any(v["measurement_type"] == "seconds" and v["value"] == "65" for v in data["values"])

    @pytest.mark.asyncio
    async def test_update_single_measurement_player_forbidden(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_update_forbidden@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Original note player",
            "values": [{"measurement_type": "repetitions", "value": "8"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {player_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        update_data = {
            "notes": "Player trying to update",
            "values": [{"measurement_type": "repetitions", "value": "9"}],
        }
        response = await async_client.put(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {player_token}"},
            json=update_data,
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_single_measurement_admin_access(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session, email="player_delete_by_admin@example.com")
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.kilograms])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "To be deleted",
            "values": [{"measurement_type": "kilograms", "value": "120"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.delete(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 204

        # Verify soft delete
        get_response = await async_client.get(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert get_response.status_code == 404 # Should not be found if soft deleted and not specifically requested to include inactive

    @pytest.mark.asyncio
    async def test_delete_single_measurement_coach_forbidden(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_delete_forbidden@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_delete_forbidden_by_coach@example.com")

        team_data = {"name": "Delete Forbidden Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        coach_other, _ = await create_coach_user(async_session, email="other_coach_delete_meas@example.com")
        exercise = await create_exercise(async_session, coach_other.id, measurement_types=[MeasurementType.repetitions])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Coach trying to delete",
            "values": [{"measurement_type": "repetitions", "value": "30"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.delete(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_single_measurement_player_forbidden(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_delete_forbidden@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.seconds])

        measurement_data = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Player trying to delete",
            "values": [{"measurement_type": "seconds", "value": "40"}],
        }
        post_response = await async_client.post("/measurements", headers={"Authorization": f"Bearer {player_token}"}, json=measurement_data, follow_redirects=True)
        measurement_id = post_response.json()["id"]

        response = await async_client.delete(
            f"/measurements/{measurement_id}",
            headers={"Authorization": f"Bearer {player_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_measurement_stats_endpoint_coach_access(self, async_client, async_session, get_coach_token: str, get_admin_token: str):
        admin_token = get_admin_token
        coach_user, coach_profile = await create_coach_user(async_session, email="coach_stats_endpoint_access@example.com")
        coach_token = get_coach_token
        player_user, player_profile = await create_player_user(async_session, email="player_stats_endpoint_by_coach@example.com")

        team_data = {"name": "Stats Endpoint Team", "season": "2024"}
        team_response = await async_client.post(
            "/teams", headers={"Authorization": f"Bearer {admin_token}"}, json=team_data,
            follow_redirects=True
        )
        team_id = team_response.json()["id"]

        await async_client.post(f"/teams/{team_id}/coaches", headers={"Authorization": f"Bearer {admin_token}"}, json={"coach_id": coach_profile.id}, follow_redirects=True)
        await async_client.post(f"/teams/{team_id}/players", headers={"Authorization": f"Bearer {admin_token}"}, json={"player_id": player_profile.id}, follow_redirects=True)

        coach_other, _ = await create_coach_user(async_session, email="other_coach_for_exercise_stats@example.com")
        exercise = await create_exercise(async_session, coach_other.id, name="Sprint", measurement_types=[MeasurementType.seconds])

        measurement_data_1 = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Stat 1",
            "values": [{"measurement_type": "seconds", "value": "10"}],
        }
        measurement_data_2 = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Stat 2",
            "values": [{"measurement_type": "seconds", "value": "9"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data_1, follow_redirects=True)
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data_2, follow_redirects=True)

        response = await async_client.get(
            f"/measurements/stats?player_id={player_profile.id}&exercise_id={exercise.id}&measurement_type=seconds",
            headers={"Authorization": f"Bearer {coach_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["average"] == 9.5
        assert data["best"] == 9.0 # Lower is better for seconds
        assert data["trend"] == "improving"

    @pytest.mark.asyncio
    async def test_get_measurement_stats_endpoint_admin_access(self, async_client, async_session, get_admin_token: str):
        admin_token = get_admin_token
        player_user, player_profile = await create_player_user(async_session, email="player_stats_endpoint_by_admin@example.com")

        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, name="Weightlift", measurement_types=[MeasurementType.kilograms])

        measurement_data_1 = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Stat A",
            "values": [{"measurement_type": "kilograms", "value": "100"}],
        }
        measurement_data_2 = {
            "player_id": player_profile.id,
            "exercise_id": exercise.id,
            "recorded_at": datetime.now().isoformat(),
            "notes": "Stat B",
            "values": [{"measurement_type": "kilograms", "value": "110"}],
        }
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data_1, follow_redirects=True)
        await async_client.post("/measurements", headers={"Authorization": f"Bearer {admin_token}"}, json=measurement_data_2, follow_redirects=True)

        response = await async_client.get(
            f"/measurements/stats?player_id={player_profile.id}&exercise_id={exercise.id}&measurement_type=kilograms",
            headers={"Authorization": f"Bearer {admin_token}"},
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert data["average"] == 105.0
        assert data["best"] == 110.0 # Higher is better for kilograms
        assert data["trend"] == "improving"

    @pytest.mark.asyncio
    async def test_get_measurement_stats_endpoint_player_forbidden(self, async_client, async_session, get_player_token: str):
        player_user, player_profile = await create_player_user(async_session, email="player_stats_endpoint_forbidden@example.com")
        player_token = get_player_token
        coach_user, _ = await create_coach_user(async_session)
        exercise = await create_exercise(async_session, coach_user.id, measurement_types=[MeasurementType.repetitions])

        response = await async_client.get(
            f"/measurements/stats?player_id={player_profile.id}&exercise_id={exercise.id}&measurement_type=repetitions",
            headers={"Authorization": f"Bearer {player_token}"},
            follow_redirects=True
        )
        assert response.status_code == 403
