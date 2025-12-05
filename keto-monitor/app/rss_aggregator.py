import feedparser
import yaml
import os
from datetime import datetime
from time import mktime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/rss_feeds.yaml')

def load_rss_config():
    """Loads the RSS configuration from yaml."""
    if not os.path.exists(CONFIG_PATH):
        print(f"WARNING: RSS config not found at {CONFIG_PATH}")
        return {"global_feeds": [], "company_specific_feeds": {}}
        
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def parse_published_date(entry):
    """Helper to parse date from feed entry."""
    if hasattr(entry, 'published_parsed'):
        return datetime.fromtimestamp(mktime(entry.published_parsed))
    elif hasattr(entry, 'updated_parsed'):
        return datetime.fromtimestamp(mktime(entry.updated_parsed))
    return datetime.utcnow()

def fetch_feed(url):
    """Fetches and parses a single RSS feed."""
    print(f"Fetching RSS: {url}")
    feed = feedparser.parse(url)
    articles = []
    
    if feed.bozo:
        print(f"  -> Warning: Feed might be malformed: {feed.bozo_exception}")
        
    for entry in feed.entries:
        try:
            content = ""
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            else:
                content = entry.title

            article = {
                "url": entry.link,
                "title": entry.title,
                "source_name": feed.feed.title if hasattr(feed.feed, 'title') else "RSS Feed",
                "published_at": parse_published_date(entry),
                "content": content
            }
            articles.append(article)
        except Exception as e:
            print(f"  -> Error parsing entry: {e}")
            continue
            
    print(f"  -> Found {len(articles)} articles.")
    return articles

def fetch_all_global_feeds():
    """Fetches all global feeds defined in config."""
    config = load_rss_config()
    all_articles = []
    for url in config.get('global_feeds', []):
        all_articles.extend(fetch_feed(url))
    return all_articles

def fetch_company_feeds(company_slug):
    """Fetches feeds specific to a company."""
    config = load_rss_config()
    urls = config.get('company_specific_feeds', {}).get(company_slug, [])
    all_articles = []
    for url in urls:
        all_articles.extend(fetch_feed(url))
    return all_articles
