import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Company

# Define the database file path in the project root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keto.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

_engine = None
_Session = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False)
    return _engine

def get_session():
    global _Session
    if _Session is None:
        engine = get_engine()
        _Session = sessionmaker(bind=engine)
    return _Session()

def init_db():
    """Creates all tables defined in models."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_PATH}")

def sync_companies_from_yaml(session):
    """
    Reads config/companies.yaml and updates the database.
    Adds new companies and updates existing ones based on slug.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'companies.yaml')
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    companies_data = config.get('companies', [])
    
    print(f"Syncing {len(companies_data)} companies from YAML...")
    
    for data in companies_data:
        slug = data['slug']
        name = data['name']
        search_query = data['search_query']
        
        # Check if company exists
        company = session.query(Company).filter_by(slug=slug).first()
        
        if company:
            # Update existing
            company.name = name
            company.search_query = search_query
            print(f"Updated: {name} ({slug})")
        else:
            # Create new
            company = Company(name=name, slug=slug, search_query=search_query)
            session.add(company)
            print(f"Added: {name} ({slug})")
    
    session.commit()
    print("Sync complete.")
