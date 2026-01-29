import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        with open("users.txt", "w") as f:
            f.write(f"Found {len(users)} users:\n")
            for user in users:
                f.write(f"ID: {user.id}, Email: {user.email}, Role: {user.role}\n")

if __name__ == "__main__":
    asyncio.run(list_users())
