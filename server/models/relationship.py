from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    PickleType
)
from sqlalchemy.ext.mutable import MutableList

from sqlalchemy.orm import Mapped, relationship

from config.database import Base


class MasterRepair(Base):
    __tablename__ = 'master_repair'
    __table_args__ = {'extend_existing': True}

    master_id = Column(String, ForeignKey('master.username', ondelete='CASCADE'), primary_key=True)
    address_latitude = Column(Float, nullable=False)
    address_longitude = Column(Float, nullable=False)
    repair_id = Column(Integer, ForeignKey('repair_type.id', ondelete='CASCADE'), primary_key=True)
    price = Column(Float, nullable=True)
    time = Column(String, nullable=True)


class ArticleLike(Base):
    __tablename__ = 'article_like'
    __table_args__ = {'extend_existing': True}

    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'), primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)


class ArticleCommentLike(Base):
    __tablename__ = 'article_comment_like'
    __table_args__ = {'extend_existing': True}

    comment_id = Column(Integer, ForeignKey('article_comment.id', ondelete='CASCADE'), primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)


class OrderRepair(Base):
    __tablename__ = 'order_repair'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    repair_id = Column(Integer, ForeignKey('repair_type.id'), primary_key=True)


class UnreadMessage(Base):
    __tablename__ = 'unread_message'

    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    dialog_id = Column(Integer, ForeignKey('dialog.id', ondelete='CASCADE'), primary_key=True)
    messages = Column(MutableList.as_mutable(PickleType), default=[])
