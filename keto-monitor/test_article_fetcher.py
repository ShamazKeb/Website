from app.db import init_db, get_session
from app.models import Company, Article
from app.news_fetcher import generate_fake_articles, store_new_articles

def main():
    print("--- 1. Initialize Database & Load Companies ---")
    init_db()
    session = get_session()
    
    companies = session.query(Company).all()
    if not companies:
        print("No companies found. Please run test_db_setup.py first.")
        return

    print(f"Found {len(companies)} companies.")

    print("\n--- 2. Fetch & Store Fake Articles ---")
    total_new = 0
    for company in companies:
        print(f"Processing {company.name}...")
        fake_articles = generate_fake_articles(company)
        added_articles = store_new_articles(session, company, fake_articles)
        total_new += len(added_articles)
        print(f"  -> Generated {len(fake_articles)}, Stored {len(added_articles)} new.")

    print(f"\nTotal new articles stored: {total_new}")

    print("\n--- 3. Verify Articles in DB ---")
    all_articles = session.query(Article).all()
    for a in all_articles:
        print(f"ID: {a.id} | Company: {a.company.name} | Title: {a.title}")

    session.close()

if __name__ == "__main__":
    main()
