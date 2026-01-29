import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.models import User, Player, Coach, Team, Exercise, PlayerMeasurement, MeasurementValue, Role, MeasurementType
from app.tests.test_data import create_test_data

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio





@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_data(async_session: AsyncSession):
    await create_test_data(async_session)


async def test_get_player_stats_as_self(async_client: AsyncClient, headers_player_1: dict, player_1_id: int):
    response = await async_client.get(f"/players/{player_1_id}/stats", headers=headers_player_1)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_1_id
    assert "stats_by_exercise" in data


async def test_get_player_stats_as_other_player(async_client: AsyncClient, headers_player_2: dict, player_1_id: int):
    response = await async_client.get(f"/players/{player_1_id}/stats", headers=headers_player_2)
    assert response.status_code == 403


async def test_get_player_stats_as_coach_of_team(async_client: AsyncClient, headers_coach_1: dict, player_1_id: int):
    response = await async_client.get(f"/players/{player_1_id}/stats", headers=headers_coach_1)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_1_id


async def test_get_player_stats_as_coach_not_of_team(async_client: AsyncClient, headers_coach_2: dict, player_1_id: int):
    response = await async_client.get(f"/players/{player_1_id}/stats", headers=headers_coach_2)
    assert response.status_code == 403


async def test_get_player_stats_as_admin(async_client: AsyncClient, headers_admin: dict, player_1_id: int):
    response = await async_client.get(f"/players/{player_1_id}/stats", headers=headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_1_id
