from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    search_query = Column(String, nullable=False)
    
    articles = relationship("Article", back_populates="company")
    topics = relationship("Topic", back_populates="company")

    def __repr__(self):
        return f"<Company(name='{self.name}', slug='{self.slug}')>"

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=True)
    hash = Column(String, unique=True, nullable=False)

    company = relationship("Company", back_populates="articles")
    topic_articles = relationship("TopicArticle", back_populates="article")

    def __repr__(self):
        return f"<Article(title='{self.title}', url='{self.url}')>"

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    topic_key = Column(String, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="topics")
    topic_articles = relationship("TopicArticle", back_populates="topic")
    summaries = relationship("Summary", back_populates="topic")

    def __repr__(self):
        return f"<Topic(title='{self.title}', key='{self.topic_key}')>"

class TopicArticle(Base):
    __tablename__ = 'topic_articles'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)

    topic = relationship("Topic", back_populates="topic_articles")
    article = relationship("Article", back_populates="topic_articles")

class Summary(Base):
    __tablename__ = 'summaries'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    summary_text = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    article_count_at_generation = Column(Integer, default=0)

    topic = relationship("Topic", back_populates="summaries")
