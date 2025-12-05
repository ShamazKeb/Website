import os
from app.db import init_db, get_session, Base, get_engine
from app.models import Article, Topic, TopicArticle, Company, Summary
from app.summary_generator import update_summaries_for_recent_topics
from app.topic_grouper import assign_topics_to_new_articles
from app.news_fetcher import generate_fake_articles, store_new_articles
from datetime import datetime

def main():
    print("--- Test: Real AI Summary Generator (with Refresh) ---")
    
    # 1. Clean Slate (Drop DB to ensure schema update for new column)
    print("Resetting Database...")
    engine = get_engine()
    Base.metadata.drop_all(engine)
    init_db()
    session = get_session()
    
    # 2. Setup Data (Company + 2 Articles)
    print("Creating initial data...")
    company = Company(name="Test Corp", slug="testcorp", search_query="Test Corp news")
    session.add(company)
    session.commit()
    
    # Create 2 Articles
    art1 = Article(company_id=company.id, url="http://test1.com", title="Test Corp launches Product A", source_name="TechNews", content="Test Corp announced Product A today. It is great.", hash="hash1")
    art2 = Article(company_id=company.id, url="http://test2.com", title="Product A details", source_name="BizDaily", content="More details on Product A. It has AI.", hash="hash2")
    session.add_all([art1, art2])
    session.commit()
    
    # Group them (using Real AI Grouper)
    print("Grouping articles...")
    assign_topics_to_new_articles(session)
    
    # 3. Generate Initial Summary
    print("\n--- Run 1: Initial Summary Generation ---")
    update_summaries_for_recent_topics(session)
    
    # Verify
    topic = session.query(Topic).first()
    summary = session.query(Summary).filter_by(topic_id=topic.id).first()
    print(f"Topic: {topic.title}")
    print(f"Summary (v1): {summary.summary_text[:100]}...")
    print(f"Article Count at Gen: {summary.article_count_at_generation}")
    
    # 4. Add New Article to SAME Topic
    print("\n--- Adding new article to trigger refresh ---")
    art3 = Article(company_id=company.id, url="http://test3.com", title="Market reaction to Product A", source_name="MarketWatch", content="Stock went up after Product A launch.", hash="hash3")
    session.add(art3)
    session.commit()
    
    # Manually link it to the existing topic (to simulate Grouper adding it)
    link = TopicArticle(topic_id=topic.id, article_id=art3.id)
    session.add(link)
    session.commit()
    
    # 5. Run Generator Again
    print("\n--- Run 2: Refresh Summary ---")
    update_summaries_for_recent_topics(session)
    
    # Verify Refresh
    session.refresh(summary)
    print(f"Summary (v2): {summary.summary_text[:100]}...")
    print(f"Article Count at Gen: {summary.article_count_at_generation}")
    
    if summary.article_count_at_generation == 3:
        print("\nSUCCESS: Summary was refreshed with new article count.")
    else:
        print("\nFAILURE: Summary article count did not update.")

    session.close()

if __name__ == "__main__":
    main()
