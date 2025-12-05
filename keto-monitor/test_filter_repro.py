from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.models import Base, Company, Topic, Article, TopicArticle, Summary
from app.web import get_topics_with_summaries

# Mock get_session to use our in-memory DB
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def test_repro():
    session = Session()
    try:
        print("--- Reproduction Test ---")
        
        # Setup Data
        c = Company(name="Test Co", slug="test", search_query="test")
        session.add(c)
        session.flush()
        
        t = Topic(company_id=c.id, topic_key="t1", title="Topic A", updated_at=datetime(2025, 12, 5))
        session.add(t)
        session.flush()
        
        a1 = Article(company_id=c.id, url="u1", title="Art 1 (Dec 1)", source_name="S", hash="h1", published_at=datetime(2025, 12, 1))
        a2 = Article(company_id=c.id, url="u2", title="Art 2 (Dec 3)", source_name="S", hash="h2", published_at=datetime(2025, 12, 3))
        session.add_all([a1, a2])
        session.flush()
        
        session.add(TopicArticle(topic_id=t.id, article_id=a1.id))
        session.add(TopicArticle(topic_id=t.id, article_id=a2.id))
        session.commit()
        
        # Test Filter
        print("Filtering for Dec 2 - Dec 4...")
        # We need to monkeypatch get_session in app.web or pass the session if possible.
        # app.web.get_topics_with_summaries takes 'session' as arg! Perfect.
        
        topics = get_topics_with_summaries(session, date_from="2025-12-02", date_to="2025-12-04")
        
        if topics:
            print(f"SUCCESS: Found {len(topics)} topics.")
            print(f"Topic: {topics[0].title}")
        else:
            print("FAILURE: No topics found.")
            
    finally:
        session.close()

if __name__ == "__main__":
    test_repro()
