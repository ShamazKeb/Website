from app.db import init_db, get_session, sync_companies_from_yaml
from app.models import Company
from app.news_fetcher import generate_fake_articles, store_new_articles
from app.topic_grouper import assign_topics_to_new_articles
from app.summary_generator import update_summaries_for_recent_topics

def run_daily_job():
    print("=== Starting Daily Job ===")
    
    # 1. Initialize DB & Sync Companies
    init_db()
    session = get_session()
    sync_companies_from_yaml(session)
    
    try:
        # 2. Load Companies
        companies = session.query(Company).all()
        print(f"Loaded {len(companies)} companies.")
        
        # 3. Fetch & Store Articles (RSS)
        print("Step 3: Fetching Articles (RSS)...")
        from app.news_fetcher import store_rss_articles
        store_rss_articles(session)
        
        # 4. Group Topics
        print("Running Topic Grouper...")
        assign_topics_to_new_articles(session)
        
        # 5. Generate Summaries
        print("Running Summary Generator...")
        update_summaries_for_recent_topics(session)
        
        print("=== Daily Job Complete ===")
        
    except Exception as e:
        print(f"ERROR in Daily Job: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_daily_job()
