from app.db import init_db, get_session
from app.models import Article, Topic, TopicArticle
from app.topic_grouper import assign_topics_to_new_articles
from app.news_fetcher import generate_fake_articles, store_new_articles
from app.models import Company

def main():
    print("--- Test: Real AI Topic Grouper (Refined) ---")
    
    # 1. Setup
    init_db()
    session = get_session()
    
    # 2. Ensure we have unassigned articles
    print("Checking for unassigned articles...")
    unassigned = session.query(Article).outerjoin(TopicArticle).filter(TopicArticle.id == None).count()
    
    if unassigned == 0:
        print("No unassigned articles found. Generating fresh articles...")
        companies = session.query(Company).all()
        for company in companies:
            fake = generate_fake_articles(company)
            store_new_articles(session, company, fake)
        unassigned = session.query(Article).outerjoin(TopicArticle).filter(TopicArticle.id == None).count()
    
    print(f"Unassigned articles in DB: {unassigned}")
    
    # 3. Run Grouper
    print("\nRunning assign_topics_to_new_articles()...")
    assign_topics_to_new_articles(session)
    
    # 4. Verify Results
    print("\n--- Verification Results ---")
    topics = session.query(Topic).all()
    for t in topics:
        print(f"Topic: \"{t.title}\" (Key: {t.topic_key})")
        for link in t.topic_articles:
            print(f"  -> Article {link.article.id}: \"{link.article.title}\"")
            
    session.close()

if __name__ == "__main__":
    main()
