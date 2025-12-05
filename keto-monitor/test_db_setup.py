from app.db import init_db, get_session, sync_companies_from_yaml
from app.models import Company

def main():
    print("--- 1. Initialize Database ---")
    init_db()
    
    print("\n--- 2. Sync Companies from YAML ---")
    session = get_session()
    try:
        sync_companies_from_yaml(session)
        
        print("\n--- 3. Verify Companies in DB ---")
        companies = session.query(Company).all()
        for c in companies:
            print(f"ID: {c.id} | Name: {c.name} | Slug: {c.slug} | Query: {c.search_query}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
