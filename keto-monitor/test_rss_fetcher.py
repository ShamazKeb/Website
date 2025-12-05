from app.db import init_db, get_session
from app.news_fetcher import store_rss_articles
from app.models import Article, Company

def main():
    print("--- Test: RSS Fetcher ---")
    init_db()
    session = get_session()
    
    # Ensure companies exist
    if session.query(Company).count() == 0:
        print("No companies found. Please run daily_job.py or sync companies first.")
        return

    # Run RSS Fetcher
    print("Running store_rss_articles()...")
    store_rss_articles(session)
    
    # Verify
    print("\n--- Verification ---")
    articles = session.query(Article).order_by(Article.fetched_at.desc()).limit(10).all()
    for art in articles:
        print(f"[{art.company.name}] {art.title} ({art.source_name})")
        
    session.close()

if __name__ == "__main__":
    main()
