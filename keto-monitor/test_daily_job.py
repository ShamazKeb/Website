from app.db import init_db, get_session
from app.models import Company, Article, Topic, Summary
from daily_job import run_daily_job

def main():
    print("--- Test: Running Daily Job ---")
    
    # Ensure DB is ready
    init_db()
    
    # Run the job
    run_daily_job()
    
    # Verify results
    print("\n--- Verification Results ---")
    session = get_session()
    
    company_count = session.query(Company).count()
    article_count = session.query(Article).count()
    topic_count = session.query(Topic).count()
    summary_count = session.query(Summary).count()
    
    print(f"Companies: {company_count}")
    print(f"Articles:  {article_count}")
    print(f"Topics:    {topic_count}")
    print(f"Summaries: {summary_count}")
    
    session.close()

if __name__ == "__main__":
    main()
