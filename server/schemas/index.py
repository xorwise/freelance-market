from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from schemas.user import ClientInfo


class Article(BaseModel):
    id: int
    title: str
    text: str
    views: int
    likes: int
    cover_image: Optional[str] = None
    created_at: datetime


class Review(BaseModel):
    id: int
    sender: str
    rating: int
    message: str
    created_at: datetime
    is_active: bool


class ReviewIn(BaseModel):
    sender: str
    rating: int
    message: str


class CoverPicture(BaseModel):
    id: int
    image: str


class City(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float


class Counters(BaseModel):
    masters: int
    submissions: int


class ArticleComment(BaseModel):
    id: int
    article_id: int
    sender_id: int
    sender: ClientInfo
    text: str
    likes: int
    created_at: datetime


class ArticleCommentIn(BaseModel):
    text: str
