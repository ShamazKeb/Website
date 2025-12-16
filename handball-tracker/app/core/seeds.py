from sqlalchemy.orm import Session
from app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Schnelligkeit", "description": "Sprints, Antritte, Reaktionsschnelligkeit"},
    {"name": "Kraft", "description": "Maximalkraft, Schnellkraft, Kraftausdauer"},
    {"name": "Ausdauer", "description": "Grundlagenausdauer, Tempohärte"},
    {"name": "Koordination", "description": "Lauf-ABC, Sprungkoordination, Gewandtheit"},
    {"name": "Taktik", "description": "Spielzüge, Abwehrformationen, Angriffskonzeptionen"},
    {"name": "Technik", "description": "Wurftechnik, Passtechnik, Täuschungen"}
]

def seed_categories(db: Session):
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(name=cat_data["name"], description=cat_data["description"])
            db.add(category)
    db.commit()
