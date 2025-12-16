from app.core.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

def debug_db():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Found {len(users)} users.")
    for u in users:
        print(f"User: {u.email}, Role: '{u.role}', Hash: {u.password_hash[:10]}...")
        
        # Verify direct SQL value (to be sure it's not some Enum object representation issue)
        result = db.execute(text(f"SELECT role FROM users WHERE id = {u.id}"))
        raw_role = result.scalar()
        print(f" > Raw DB Role Value: '{raw_role}' (Type: {type(raw_role)})")
        
    db.close()

if __name__ == "__main__":
    debug_db()
