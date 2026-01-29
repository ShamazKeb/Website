import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User, Role
from app.security import hash_password

async def reset_admin_password():
    async with AsyncSessionLocal() as session:
        # Find admin user
        result = await session.execute(select(User).filter(User.email == "admin@handball.de"))
        admin = result.scalars().first()
        
        if not admin:
            print("Admin user not found. Creating one...")
            admin = User(
                email="admin@handball.de",
                role=Role.admin,
                password_hash=hash_password("strunzadmin") # Setting explicit password
            )
            session.add(admin)
        else:
            print(f"Admin found: {admin.email}. Resetting password...")
            admin.password_hash = hash_password("strunzadmin")
            session.add(admin)
        
        await session.commit()
        print("Admin password reset to: strunzadmin")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
