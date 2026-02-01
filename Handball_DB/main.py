import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base
from app.routers import auth, test_rbac, teams, exercises, measurements, player_measurements, players, activity_logs, admin, debug, dev


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enable automatic table creation for initialization
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(test_rbac.router)
app.include_router(teams.router)
app.include_router(exercises.router)
app.include_router(measurements.router)
app.include_router(player_measurements.router)
app.include_router(players.router)
app.include_router(activity_logs.router)
app.include_router(admin.router)

if os.getenv("ENVIRONMENT") == "development":
    app.include_router(debug.router)
    app.include_router(dev.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}