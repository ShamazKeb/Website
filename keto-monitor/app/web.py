from flask import Flask, render_template, request
from datetime import datetime
from app.db import get_session, init_db, sync_companies_from_yaml
from app.models import Company, Topic, Summary, Article, TopicArticle
from sqlalchemy.orm import joinedload
from sqlalchemy import func, select

app = Flask(__name__, template_folder='../templates')

# Initialize DB and sync companies on startup
with app.app_context():
    init_db()
    session = get_session()
    try:
        sync_companies_from_yaml(session)
    finally:
        session.close()

def get_companies(session):
    return session.query(Company).order_by(Company.name).all()

def get_topics_with_summaries(session, company_slug=None, date_from=None, date_to=None):
    # Subquery to find the latest article date for each topic
    latest_article_date = (
        select(func.max(Article.published_at))
        .join(TopicArticle, TopicArticle.article_id == Article.id)
        .where(TopicArticle.topic_id == Topic.id)
        .correlate(Topic)
        .scalar_subquery()
    )

    query = session.query(Topic).options(
        joinedload(Topic.summaries),
        joinedload(Topic.topic_articles).joinedload(TopicArticle.article)
    ).order_by(latest_article_date.desc())

    if company_slug:
        query = query.join(Company).filter(Company.slug == company_slug)

    # Filter by Date (Article Published Date)
    if date_from or date_to:
        # Join with Articles if we are filtering by date
        query = query.join(Topic.topic_articles).join(TopicArticle.article)

    def parse_date(date_str):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    if date_from:
        dt_from = parse_date(date_from)
        if dt_from:
            query = query.filter(Article.published_at >= dt_from)

    if date_to:
        dt_to = parse_date(date_to)
        if dt_to:
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Article.published_at <= dt_to)
            
    if date_from or date_to:
        query = query.distinct()

    return query.all()

@app.route('/')
def index():
    session = get_session()
    try:
        # Get Filter Params
        company_slug = request.args.get('company')
        date_from = request.args.get('from')
        date_to = request.args.get('to')

        # Fetch Data
        companies = get_companies(session)
        topics = get_topics_with_summaries(session, company_slug, date_from, date_to)

        return render_template(
            'index.html', 
            companies=companies, 
            topics=topics,
            selected_company=company_slug,
            selected_from=date_from,
            selected_to=date_to
        )
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)
