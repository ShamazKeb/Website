from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, Base, engine
from app.security import get_current_admin
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    dependencies=[Depends(get_current_admin)], # Protected by admin auth in dev
    responses={status.HTTP_403_FORBIDDEN: {"detail": "Operation forbidden"}},
)

@router.delete("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_database(db: AsyncSession = Depends(get_db)):
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This endpoint is only available in development environment.")

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # You might want to add some initial data seeding here for development

    return {}
