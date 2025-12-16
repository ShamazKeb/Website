from app.core.database import SessionLocal
from app.models.user import User
from app.core import security

def check_admin():
    db = SessionLocal()
    email = "admin@test.com"
    password = "password123"
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"❌ User {email} NOT FOUND in database!")
    else:
        print(f"✅ User {email} found.")
        print(f"   Role: {user.role}")
        print(f"   Hash: {user.password_hash[:10]}...")
        
        is_valid = security.verify_password(password, user.password_hash)
        if is_valid:
            print(f"✅ Password '{password}' is VALID.")
        else:
            print(f"❌ Password '{password}' is INVALID.")

    db.close()

if __name__ == "__main__":
    check_admin()
