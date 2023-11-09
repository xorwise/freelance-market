import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float
)
from config.database import Base
from sqlalchemy.orm import relationship
from config.settings import COMMISSION


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    cover_image = Column(String, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    comments = relationship('ArticleComment', back_populates='article')


class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String, nullable=False)
    rating = Column(Integer, nullable=False, default=5)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    is_active = Column(Boolean, default=False)


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class CoverPicture(Base):
    __tablename__ = 'cover_picture'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String, nullable=False)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    commission = Column(Float, nullable=False, default=COMMISSION)


class ArticleComment(Base):
    __tablename__ = 'article_comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    article = relationship('Article', back_populates='comments')
    sender_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    sender = relationship('Client')
    text = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)

