from app.db import init_db, get_session
from app.models import Topic, TopicArticle, Summary
from app.topic_grouper import assign_topics_to_new_articles
from app.summary_generator import update_summaries_for_recent_topics

def main():
    print("--- 1. Initialize Database (Update Schema) ---")
    init_db()
    session = get_session()

    print("\n--- 2. Run Topic Grouper (Stub) ---")
    count = assign_topics_to_new_articles(session)
    print(f"Created {count} new topics.")
    
    print("\n--- 3. Verify Topics ---")
    topics = session.query(Topic).all()
    for t in topics:
        print(f"Topic ID: {t.id} | Key: {t.topic_key} | Title: {t.title}")
        
    print("\n--- 4. Run Summary Generator (Stub) ---")
    count_sum = update_summaries_for_recent_topics(session)
    print(f"Created {count_sum} new summaries.")
    
    print("\n--- 5. Verify Summaries ---")
    summaries = session.query(Summary).all()
    for s in summaries:
        print(f"Summary ID: {s.id} | Topic ID: {s.topic_id} | Text: {s.summary_text}")

    session.close()

if __name__ == "__main__":
    main()
