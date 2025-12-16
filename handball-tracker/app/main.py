from fastapi import FastAPI

from app.api import auth

from app.api.routes import admin_teams, admin_users

app = FastAPI(title="Handball-Tracker")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin_teams.router)
app.include_router(admin_users.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
