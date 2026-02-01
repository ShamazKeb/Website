import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models import User
from app.security import verify_password, hash_password
from sqlalchemy.future import select

async def debug_users():
    async with AsyncSessionLocal() as db:
        print("--- Debugging Users ---")
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("NO USERS FOUND IN DATABASE!")
            return

        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}")
            
            # Test 'admin123'
            is_valid = verify_password("admin123", user.password_hash)
            print(f"  Password 'admin123' valid? {is_valid}")
            
            # Test 'admin' (from create_test_users.py)
            is_valid_simple = verify_password("admin", user.password_hash)
            print(f"  Password 'admin' valid? {is_valid_simple}")

            # Test 'password' (generic default)
            is_valid_generic = verify_password("password", user.password_hash)
            print(f"  Password 'password' valid? {is_valid_generic}")

        print("-----------------------")

if __name__ == "__main__":
    asyncio.run(debug_users())
