import logging
import sys
from sqlalchemy.orm import Session

# Add project root to sys.path to allow imports
sys.path.append(".")

from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Tables are created by alembic or manually, but let's ensure they exist for safety
    # Base.metadata.create_all(bind=engine) 
    # (Commented out to rely on previous steps or future migrations, but for now safe to verify)
    
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} created.")
    else:
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists.")

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    db.close()
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
