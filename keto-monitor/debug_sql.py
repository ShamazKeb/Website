from app.db import get_session
from app.models import Topic, Article, TopicArticle, Company
from sqlalchemy.orm import joinedload
from datetime import datetime

def debug_sql():
    session = get_session()
    try:
        print("--- Debugging SQL ---")
        
        # Reconstruct the query from web.py
        query = session.query(Topic).options(
            joinedload(Topic.summaries),
            joinedload(Topic.topic_articles).joinedload(TopicArticle.article)
        ).order_by(Topic.updated_at.desc())

        query = query.join(Company).filter(Company.slug == 'nvidia')

        # Filter Params
        date_from = "03.12.2025"
        date_to = "04.12.2025"

        # Apply Join
        query = query.join(Topic.topic_articles).join(TopicArticle.article)

        # Parse Logic
        def parse_date(date_str):
            for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None

        dt_from = parse_date(date_from)
        if dt_from:
            print(f"Parsed From: {dt_from}")
            query = query.filter(Article.published_at >= dt_from)
        else:
            print("Failed to parse From date!")

        dt_to = parse_date(date_to)
        if dt_to:
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            print(f"Parsed To: {dt_to}")
            query = query.filter(Article.published_at <= dt_to)
        else:
            print("Failed to parse To date!")
            
        query = query.distinct()

        # Print SQL
        print("\nGenerated SQL:")
        print(query.statement.compile(compile_kwargs={"literal_binds": True}))
        
        # Execute
        results = query.all()
        print(f"\nFound {len(results)} topics.")
        for t in results:
            print(f"Topic: {t.title}")
            for ta in t.topic_articles:
                print(f"  - Article: {ta.article.title} ({ta.article.published_at})")

    finally:
        session.close()

if __name__ == "__main__":
    debug_sql()
