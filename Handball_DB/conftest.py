import sys
import os
import pytest
import pytest_asyncio
from app import models
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base, get_db
from main import app
from app.models import User, Role
from app.security import create_access_token
from datetime import timedelta

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Use in-memory database
test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingAsyncSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def async_session():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestingAsyncSessionLocal() as session:
        yield session

from httpx import ASGITransport, AsyncClient

@pytest_asyncio.fixture(scope="function")
async def async_client(async_session: AsyncSession):
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


from app.security import hash_password # Import hash_password
from app.models import Player, Coach, Team # Import necessary models


async def create_test_user_token(user_id: int, email: str, role: Role):
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": email, "id": user_id, "role": role.value},
        expires_delta=access_token_expires,
    )

# Helper functions for creating users and getting tokens
async def create_admin_user(db: AsyncSession, email: str = "admin@test.com", password: str = "testpassword") -> User:
    hashed_password = hash_password(password)
    user = User(email=email, password_hash=hashed_password, role=Role.admin)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_coach_user(db: AsyncSession, email: str = "coach@test.com", password: str = "testpassword", first_name: str = "Test", last_name: str = "Coach") -> (User, Coach):
    hashed_password = hash_password(password)
    user = User(email=email, password_hash=hashed_password, role=Role.coach)
    db.add(user)
    await db.flush() # Flush to get user.id
    coach = Coach(user_id=user.id, first_name=first_name, last_name=last_name)
    db.add(coach)
    await db.commit()
    await db.refresh(user)
    await db.refresh(coach)
    user.coach = coach # Establish relationship
    return user, coach

async def create_player_user(db: AsyncSession, email: str = "player@test.com", password: str = "testpassword", first_name: str = "Test", last_name: str = "Player", birth_year: int = 2000) -> (User, Player):
    hashed_password = hash_password(password)
    user = User(email=email, password_hash=hashed_password, role=Role.player)
    db.add(user)
    await db.flush() # Flush to get user.id
    player = Player(user_id=user.id, first_name=first_name, last_name=last_name, birth_year=birth_year)
    db.add(player)
    await db.commit()
    await db.refresh(user)
    await db.refresh(player)
    user.player = player # Establish relationship
    return user, player

@pytest_asyncio.fixture(scope="function")
async def get_admin_token(async_session: AsyncSession) -> str:
    admin_user = await create_admin_user(async_session, email="get_admin_token@example.com")
    return await create_test_user_token(admin_user.id, admin_user.email, admin_user.role)

@pytest_asyncio.fixture(scope="function")
async def get_coach_token(async_session: AsyncSession, email: str = "get_coach_token@example.com", first_name: str = "Test", last_name: str = "Coach") -> str:
    coach_user, _ = await create_coach_user(async_session, email=email, first_name=first_name, last_name=last_name)
    return await create_test_user_token(coach_user.id, coach_user.email, coach_user.role)

@pytest_asyncio.fixture(scope="function")
async def get_player_token(async_session: AsyncSession, email: str = "get_player_token@example.com", first_name: str = "Test", last_name: str = "Player") -> str:
    player_user, _ = await create_player_user(async_session, email=email, first_name=first_name, last_name=last_name)
    return await create_test_user_token(player_user.id, player_user.email, player_user.role)



@pytest_asyncio.fixture(scope="function")
async def headers_admin(async_session: AsyncSession):
    user = await async_session.execute(User.__table__.select().where(User.email == "admin@test.com"))
    user = user.first()
    token = await create_test_user_token(user.id, user.email, user.role)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def headers_coach_1(async_session: AsyncSession):
    user = await async_session.execute(User.__table__.select().where(User.email == "coach1@test.com"))
    user = user.first()
    token = await create_test_user_token(user.id, user.email, user.role)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def headers_coach_2(async_session: AsyncSession):
    user = await async_session.execute(User.__table__.select().where(User.email == "coach2@test.com"))
    user = user.first()
    token = await create_test_user_token(user.id, user.email, user.role)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def headers_player_1(async_session: AsyncSession):
    user = await async_session.execute(User.__table__.select().where(User.email == "player1@test.com"))
    user = user.first()
    token = await create_test_user_token(user.id, user.email, user.role)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def headers_player_2(async_session: AsyncSession):
    user = await async_session.execute(User.__table__.select().where(User.email == "player2@test.com"))
    user = user.first()
    token = await create_test_user_token(user.id, user.email, user.role)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def player_1_id(async_session: AsyncSession):
    user = await async_session.execute(select(models.User).where(models.User.email == "player1@test.com"))
    user = user.scalars().first()
    player = await async_session.execute(select(models.Player).where(models.Player.user_id == user.id))
    player = player.scalars().first()
    return player.id

@pytest_asyncio.fixture(scope="function")
async def player_2_id(async_session: AsyncSession):
    user = await async_session.execute(select(models.User).where(models.User.email == "player2@test.com"))
    user = user.scalars().first()
    player = await async_session.execute(select(models.Player).where(models.Player.user_id == user.id))
    player = player.scalars().first()
    return player.id