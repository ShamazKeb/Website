import sys
from app.db import init_db, get_session, Base, get_engine, sync_companies_from_yaml
from app.models import Article, Topic, Summary, Company
from app.topic_grouper import assign_topics_to_new_articles
from app.summary_generator import update_summaries_for_recent_topics
from datetime import datetime

def main():
    print("--- SYSTEM TEST: Guidecom AG Scenarios ---")
    
    # 1. Reset Database
    print("Resetting Database...")
    engine = get_engine()
    Base.metadata.drop_all(engine)
    init_db()
    session = get_session()
    
    # 2. Sync Companies
    print("Syncing Companies...")
    sync_companies_from_yaml(session)
    
    # 3. Get Guidecom AG
    guidecom = session.query(Company).filter_by(slug="guidecom").first()
    if not guidecom:
        print("ERROR: Guidecom AG not found in DB.")
        return

    print(f"Injecting articles for {guidecom.name}...")
    
    # 4. Inject Specific Articles
    # Topic A: HR Restructuring
    a1 = Article(
        company_id=guidecom.id,
        url="http://guidecom-news.com/hr-change",
        title="Guidecom AG kündigt Umstrukturierung im Personalwesen an",
        source_name="HR Weekly",
        content="Die Guidecom AG plant umfassende Änderungen in der Personalabteilung. Ziel ist eine effizientere Verwaltung und schnellere Prozesse. Der Vorstand betonte die Notwendigkeit der Modernisierung.",
        hash="hash_hr_1",
        published_at=datetime.utcnow()
    )
    a2 = Article(
        company_id=guidecom.id,
        url="http://guidecom-news.com/new-hr-model",
        title="Neues HR-Modell bei Guidecom",
        source_name="Business Insider",
        content="Im Rahmen der Umstrukturierung setzt Guidecom auf flachere Hierarchien im HR-Bereich. Teams sollen eigenverantwortlicher arbeiten. Dies ist Teil der Strategie 2025.",
        hash="hash_hr_2",
        published_at=datetime.utcnow()
    )
    
    # Topic B: New Software Product
    b1 = Article(
        company_id=guidecom.id,
        url="http://guidecom-news.com/guideflow-launch",
        title="Guidecom launcht 'GuideFlow' Software",
        source_name="TechCrunch",
        content="Mit 'GuideFlow' bringt Guidecom eine neue Lösung für Prozessmanagement auf den Markt. Die Software soll Arbeitsabläufe automatisieren und vereinfachen.",
        hash="hash_prod_1",
        published_at=datetime.utcnow()
    )
    b2 = Article(
        company_id=guidecom.id,
        url="http://guidecom-news.com/guideflow-innovation",
        title="Innovation: GuideFlow revolutioniert den Markt",
        source_name="IT News",
        content="Die neue Software GuideFlow bietet KI-gestützte Analysen für Unternehmen. Erste Kunden berichten von enormen Zeitersparnissen. Guidecom hofft auf großen Marktanteil.",
        hash="hash_prod_2",
        published_at=datetime.utcnow()
    )
    
    session.add_all([a1, a2, b1, b2])
    session.commit()
    print("Articles injected.")
    
    # 5. Run Topic Grouper
    print("\n--- Running Topic Grouper (OpenAI) ---")
    assign_topics_to_new_articles(session)
    
    # 6. Run Summary Generator
    print("\n--- Running Summary Generator (OpenAI) ---")
    update_summaries_for_recent_topics(session)
    
    # 7. Verify Results
    print("\n--- Verification Results ---")
    topics = session.query(Topic).filter_by(company_id=guidecom.id).all()
    
    for t in topics:
        print(f"\nTOPIC: {t.title}")
        print(f"Key: {t.topic_key}")
        
        # Articles
        print(f"Articles ({len(t.topic_articles)}):")
        for link in t.topic_articles:
            print(f" - {link.article.title}")
            
        # Summary
        summary = session.query(Summary).filter_by(topic_id=t.id).first()
        if summary:
            print(f"SUMMARY:\n{summary.summary_text}")
        else:
            print("SUMMARY: [Missing]")
            
    session.close()

if __name__ == "__main__":
    main()
