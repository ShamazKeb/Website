import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, get_db
from main import app
from app.models import User, Role, Player, Coach, Team
from app.security import (
    create_access_token,
    ALGORITHM,
    SECRET_KEY,
    verify_player_self_access,
    get_current_user,
)
from datetime import timedelta, datetime
import os
from typing import Optional
from fastapi import Depends, APIRouter
from app import schemas # Added this import

# Set environment variables for testing. These should ideally be in a .env.test file or managed by pytest-dotenv
os.environ["SECRET_KEY"] = "super-secret-test-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1" # Set to 1 minute for expired token test

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:" # Use in-memory database
test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingAsyncSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestingAsyncSessionLocal() as session:
        yield session
        await session.close() # Ensure session is closed after use

@pytest.fixture(name="client")
def client_fixture(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


async def create_test_user_token(user_id: int, email: str, role: Role, expires_delta: Optional[timedelta] = None):
    # Ensure SECRET_KEY and ALGORITHM are set for the token creation in tests
    if not os.getenv("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "super-secret-test-key"
    if not os.getenv("ALGORITHM"):
        os.environ["ALGORITHM"] = "HS256"

    return create_access_token(
        data={"sub": email, "id": user_id, "role": role.value},
        expires_delta=expires_delta,
    )

async def create_admin_user(db: AsyncSession):
    admin_user = User(email="admin@example.com", password_hash="hashed_password", role=Role.admin)
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    return admin_user


async def create_coach_user(db: AsyncSession, email: str = "coach1@example.com", first_name="Coach", last_name="One"):
    coach_user = User(email=email, password_hash="hashed_password", role=Role.coach)
    db.add(coach_user)
    await db.commit()
    await db.refresh(coach_user)
    coach_profile = Coach(user_id=coach_user.id, first_name=first_name, last_name=last_name)
    db.add(coach_profile)
    await db.commit()
    await db.refresh(coach_profile)
    return coach_user, coach_profile


async def create_player_user(db: AsyncSession, email: str = "player1@example.com", first_name="Player", last_name="One"):
    player_user = User(email=email, password_hash="hashed_password", role=Role.player)
    db.add(player_user)
    await db.commit()
    await db.refresh(player_user)
    player_profile = Player(user_id=player_user.id, first_name=first_name, last_name=last_name, birth_year=2000)
    db.add(player_profile)
    await db.commit()
    await db.refresh(player_profile)
    return player_user, player_profile


async def get_admin_token(db_session: AsyncSession):
    admin_user = await create_admin_user(db_session)
    return await create_test_user_token(admin_user.id, admin_user.email, admin_user.role)


async def get_coach_token(db_session: AsyncSession, email: str = "coach1@example.com", first_name="Coach", last_name="One"):
    coach_user, _ = await create_coach_user(db_session, email, first_name, last_name)
    return await create_test_user_token(coach_user.id, coach_user.email, coach_user.role)


async def get_player_token(db_session: AsyncSession, email: str = "player1@example.com", first_name="Player", last_name="One"):
    player_user, _ = await create_player_user(db_session, email, first_name, last_name)
    return await create_test_user_token(player_user.id, player_user.email, player_user.role)


# Temporarily add the test_rbac router to the main app for testing
from app.routers import test_rbac
class TestRBACSecurity:
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client):
        response = client.get("/test_rbac/admin") # Any protected endpoint
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated" # FastAPI default

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        response = client.get("/test_rbac/admin", headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, client, db_session):
        admin_user = await create_admin_user(db_session)
        # Create a token that expires immediately
        expired_token = await create_test_user_token(admin_user.id, admin_user.email, admin_user.role, expires_delta=timedelta(seconds=-1))
        response = client.get("/test_rbac/admin", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_admin_success(self, client, db_session):
        admin_token = await get_admin_token(db_session)
        response = client.get("/test_rbac/admin", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "admin@example.com"

    @pytest.mark.asyncio
    async def test_get_current_admin_forbidden_coach(self, client, db_session):
        coach_token = await get_coach_token(db_session)
        response = client.get("/test_rbac/admin", headers={"Authorization": f"Bearer {coach_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not an admin"

    @pytest.mark.asyncio
    async def test_get_current_admin_forbidden_player(self, client, db_session):
        player_token = await get_player_token(db_session)
        response = client.get("/test_rbac/admin", headers={"Authorization": f"Bearer {player_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not an admin"

    @pytest.mark.asyncio
    async def test_get_current_coach_success(self, client, db_session):
        coach_token = await get_coach_token(db_session)
        response = client.get("/test_rbac/coach", headers={"Authorization": f"Bearer {coach_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "coach1@example.com"

    @pytest.mark.asyncio
    async def test_get_current_coach_forbidden_admin(self, client, db_session):
        admin_token = await get_admin_token(db_session)
        response = client.get("/test_rbac/coach", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not a coach"

    @pytest.mark.asyncio
    async def test_get_current_coach_forbidden_player(self, client, db_session):
        player_token = await get_player_token(db_session)
        response = client.get("/test_rbac/coach", headers={"Authorization": f"Bearer {player_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not a coach"

    @pytest.mark.asyncio
    async def test_get_current_coach_or_admin_success_admin(self, client, db_session):
        admin_token = await get_admin_token(db_session)
        response = client.get("/test_rbac/coach_or_admin", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "admin@example.com"

    @pytest.mark.asyncio
    async def test_get_current_coach_or_admin_success_coach(self, client, db_session):
        coach_token = await get_coach_token(db_session)
        response = client.get("/test_rbac/coach_or_admin", headers={"Authorization": f"Bearer {coach_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "coach1@example.com"

    @pytest.mark.asyncio
    async def test_get_current_coach_or_admin_forbidden_player(self, client, db_session):
        player_token = await get_player_token(db_session)
        response = client.get("/test_rbac/coach_or_admin", headers={"Authorization": f"Bearer {player_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not a coach or an admin"

    @pytest.mark.asyncio
    async def test_get_current_player_success(self, client, db_session):
        player_user, _ = await create_player_user(db_session)
        player_token = await create_test_user_token(player_user.id, player_user.email, player_user.role)
        response = client.get("/test_rbac/player", headers={"Authorization": f"Bearer {player_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "player1@example.com"

    @pytest.mark.asyncio
    async def test_get_current_player_forbidden_admin(self, client, db_session):
        admin_token = await get_admin_token(db_session)
        response = client.get("/test_rbac/player", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not a player"

    @pytest.mark.asyncio
    async def test_get_current_player_forbidden_coach(self, client, db_session):
        coach_token = await get_coach_token(db_session)
        response = client.get("/test_rbac/player", headers={"Authorization": f"Bearer {coach_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "The user is not a player"

    @pytest.mark.asyncio
    async def test_verify_player_self_access_success(self, client, db_session):
        player_user, player_profile = await create_player_user(db_session, email="self_access_player@example.com")
        player_token = await create_test_user_token(player_user.id, player_user.email, player_user.role)

        response = client.get(f"/test_rbac/player_self_access/{player_profile.id}", headers={"Authorization": f"Bearer {player_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "self_access_player@example.com"

    @pytest.mark.asyncio
    async def test_verify_player_self_access_forbidden(self, client, db_session):
        player_user_1, player_profile_1 = await create_player_user(db_session, email="player_1@example.com")
        player_token_1 = await create_test_user_token(player_user_1.id, player_user_1.email, player_user_1.role)

        player_user_2, player_profile_2 = await create_player_user(db_session, email="player_2@example.com")

        response = client.get(f"/test_rbac/player_self_access/{player_profile_2.id}", headers={"Authorization": f"Bearer {player_token_1}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Player can only access their own data"

    @pytest.mark.asyncio
    async def test_verify_player_self_access_admin_can_access_any_player(self, client, db_session):
        admin_token = await get_admin_token(db_session)
        player_user, player_profile = await create_player_user(db_session, email="any_player@example.com")

        # Admin user is passed to get_current_user, which does not restrict based on player_id.
        # verify_player_self_access *only* raises an exception if the role is 'player'
        # and the IDs don't match. So for an admin, it should pass.
        response = client.get(f"/test_rbac/player_self_access/{player_profile.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "admin@example.com"

