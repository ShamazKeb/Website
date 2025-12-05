import hashlib
from datetime import datetime
from app.models import Article, Company
from app.rss_aggregator import fetch_all_global_feeds, fetch_company_feeds

def generate_article_hash(url, title):
    """Generates a unique hash for an article."""
    data = f"{url}|{title}"
    return hashlib.md5(data.encode('utf-8')).hexdigest()

from app.article_filter import filter_articles_batch

def store_new_articles(session, company, articles_data):
    """
    Stores a list of article dicts for a specific company.
    Checks for duplicates using hash and URL.
    Filters for relevance using AI (Batch Mode).
    Returns the number of new articles stored.
    """
    # 1. Deduplicate locally first
    potential_articles = []
    
    for art_data in articles_data:
        # Generate Hash
        art_hash = generate_article_hash(art_data['url'], art_data['title'])
        art_data['hash'] = art_hash # Store for later
        
        # Check Duplicates in DB
        existing = session.query(Article).filter(
            (Article.hash == art_hash) | (Article.url == art_data['url'])
        ).first()
        
        if not existing:
            potential_articles.append(art_data)
            
    if not potential_articles:
        return 0
        
    print(f"  -> Found {len(potential_articles)} potential new articles. Filtering...")

    # 2. Batch Filter (AI)
    relevant_articles = filter_articles_batch(potential_articles, company.name)
    
    # 3. Store Relevant Articles
    new_count = 0
    for art_data in relevant_articles:
        new_article = Article(
            company_id=company.id,
            url=art_data['url'],
            title=art_data['title'],
            source_name=art_data['source_name'],
            published_at=art_data.get('published_at', datetime.utcnow()),
            fetched_at=datetime.utcnow(),
            content=art_data.get('content', ''),
            hash=art_data['hash']
        )
        session.add(new_article)
        new_count += 1
        
    session.commit()
    
    dropped_count = len(potential_articles) - new_count
    if dropped_count > 0:
        print(f"  -> Filtered out {dropped_count} irrelevant articles.")
        
    return new_count

def store_rss_articles(session):
    """
    Fetches articles from RSS feeds and stores them if they match a company.
    1. Fetch global feeds.
    2. Filter by company name.
    3. Fetch company-specific feeds.
    4. Store new articles.
    """
    print("--- RSS Fetcher Started ---")
    companies = session.query(Company).all()
    total_stored = 0
    
    # 1. Global Feeds
    print("Fetching global feeds...")
    global_articles = fetch_all_global_feeds()
    print(f"  -> {len(global_articles)} articles from global feeds.")
    
    for company in companies:
        company_articles = []
        
        # Filter Global Articles
        for art in global_articles:
            # Simple keyword matching (case-insensitive)
            if company.name.lower() in art['title'].lower() or \
               company.name.lower() in art['content'].lower():
                company_articles.append(art)
        
        # 2. Company Specific Feeds
        specific_articles = fetch_company_feeds(company.slug)
        if specific_articles:
            print(f"  -> {len(specific_articles)} articles from specific feeds for {company.name}.")
            company_articles.extend(specific_articles)
            
        # Store
        if company_articles:
            stored = store_new_articles(session, company, company_articles)
            if stored > 0:
                print(f"  -> Stored {stored} new RSS articles for {company.name}.")
                total_stored += stored
                
    print(f"--- RSS Fetcher Finished. Total new: {total_stored} ---")
    return total_stored

def generate_fake_articles(company):
    """Generates dummy articles for testing."""
    articles = []
    base_time = datetime.utcnow()
    
    for i in range(1, 5): # Generate 4 articles
        title = f"New update for {company.name} - Part {i}"
        url = f"http://fake-news.com/{company.slug}/news-{i}"
        content = f"This is a fake article about {company.name}. It contains important information about their latest products and financial results. (Part {i})"
        
        articles.append({
            "url": url,
            "title": title,
            "source_name": "Fake News Corp",
            "published_at": base_time,
            "content": content
        })
    return articles
