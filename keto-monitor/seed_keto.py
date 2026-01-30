from app.db import init_db, get_session, sync_companies_from_yaml
from app import models
from datetime import datetime, timedelta
import random
import hashlib

def get_hash(s):
    return hashlib.md5(s.encode()).hexdigest()

def seed_keto():
    print("🌱 Seeding Keto Monitor with sample data...")
    init_db()
    session = get_session()
    
    # 1. Sync companies first
    sync_companies_from_yaml(session)
    
    companies = session.query(models.Company).all()
    if not companies:
        print("❌ No companies found in YAML. Exiting.")
        return

    # Sample Topics and Articles
    data_map = {
        "nvidia": [
            {
                "topic": "Nvidia Blackwell Architecture",
                "summary": "Nvidia's new Blackwell GPU architecture is set to revolutionize AI processing with significantly higher efficiency and performance benchmarks than previous generations.",
                "articles": [
                    {"title": "Blackwell: The Next Frontier of AI Computing", "source": "TechCrunch", "url": "https://example.com/nvidia-1"},
                    {"title": "Nvidia CEO Unveils Blackwell at GTC 2024", "source": "The Verge", "url": "https://example.com/nvidia-2"},
                    {"title": "Why Blackwell Changes Everything for Data Centers", "source": "Reuters", "url": "https://example.com/nvidia-3"}
                ]
            }
        ],
        "mckinsey": [
            {
                "topic": "Future of GenAI in Business",
                "summary": "McKinsey's latest report highlights that Generative AI could add up to $4.4 trillion annually to the global economy, primarily through productivity gains in marketing and R&D.",
                "articles": [
                    {"title": "The Economic Potential of GenAI", "source": "McKinsey Insights", "url": "https://example.com/mck-1"},
                    {"title": "How Companies are Adopting AI in 2024", "source": "Forbes", "url": "https://example.com/mck-2"}
                ]
            }
        ],
        "keto": [
            {
                "topic": "Keto Monitor 3.0 Launch",
                "summary": "The new Intelligence Platform 'Keto Monitor 3.0' introduces a sleek Emerald design and improved AI clustering for media analysis.",
                "articles": [
                    {"title": "Redesigning the Future of Media Intelligence", "source": "Design Insider", "url": "https://example.com/keto-1"},
                    {"title": "Keto Monitor 3.0: Now with GPT-4 Integration", "source": "AI Weekly", "url": "https://example.com/keto-2"}
                ]
            }
        ]
    }

    for company in companies:
        topics = data_map.get(company.slug, [])
        for t_data in topics:
            # Create Topic
            topic = models.Topic(
                company_id=company.id,
                topic_key=get_hash(t_data["topic"]),
                title=t_data["topic"],
                updated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            session.add(topic)
            session.flush()

            # Create Summary
            summary = models.Summary(
                topic_id=topic.id,
                summary_text=t_data["summary"],
                article_count_at_generation=len(t_data["articles"])
            )
            session.add(summary)

            # Create Articles
            for a_data in t_data["articles"]:
                article = models.Article(
                    company_id=company.id,
                    title=a_data["title"],
                    url=a_data["url"],
                    source_name=a_data["source"],
                    published_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
                    hash=get_hash(a_data["url"] + str(random.random()))
                )
                session.add(article)
                session.flush()

                # Link Article to Topic
                link = models.TopicArticle(topic_id=topic.id, article_id=article.id)
                session.add(link)

    session.commit()
    print("✅ Keto Monitor seeded successfully!")

if __name__ == "__main__":
    seed_keto()
