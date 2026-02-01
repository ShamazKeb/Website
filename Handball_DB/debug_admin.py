import asyncio
import sys
import os
import logging

# Disable SQLAlchemy logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Add the parent directory to sys.path
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models import User, Role
from app.security import verify_password
from sqlalchemy.future import select

async def debug_users():
    async with AsyncSessionLocal() as db:
        print("--- Debugging Admin User ---")
        result = await db.execute(select(User).filter(User.role == Role.admin))
        admin = result.scalars().first()
        
        if not admin:
            print("NO ADMIN FOUND!")
        else:
            print(f"Admin Found: {admin.email}")
            print(f"Testing 'admin123': {verify_password('admin123', admin.password_hash)}")
            print(f"Testing 'admin': {verify_password('admin', admin.password_hash)}")

if __name__ == "__main__":
    asyncio.run(debug_users())
