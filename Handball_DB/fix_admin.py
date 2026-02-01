import asyncio
import sys
import os
import logging

# Disable SQLAlchemy logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models import User, Role
from app.security import hash_password, verify_password
from sqlalchemy.future import select

async def fix_admin():
    async with AsyncSessionLocal() as db:
        print("--- Fixing Admin Password ---")
        # Find admin
        result = await db.execute(select(User).filter(User.role == Role.admin))
        admin = result.scalars().first()
        
        if not admin:
            print("Admin not found, creating one.")
            admin = User(email="admin@handball.de", role=Role.admin)
            db.add(admin)
        else:
            print(f"Found admin: {admin.email}")
        
        # Set password
        new_pwd = "admin123"
        hashed = hash_password(new_pwd)
        admin.password_hash = hashed
        await db.commit()
        await db.refresh(admin)
        
        # Verify immediately
        print("Password updated.")
        print(f"Verify 'admin123': {verify_password('admin123', admin.password_hash)}")
        print(f"Hash in DB: {admin.password_hash}")

if __name__ == "__main__":
    asyncio.run(fix_admin())
