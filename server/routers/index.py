from fastapi import APIRouter, Depends
from schemas.index import (
    Article,
    Review,
    ReviewIn,
    CoverPicture,
    City,
    Counters,
    ArticleComment,
    ArticleCommentIn,
)
from services.index import (
    ArticleService,
    ReviewService,
    CoverPictureService,
    CityService,
    CounterService,
)
from utils.dependencies import get_current_user
from utils.service_result import handle_result
from config.database import get_db
from typing import List


router = APIRouter(
    prefix="/index",
    tags=["main-page"],
    responses={404: {"description": "Not found"}},
)


@router.get("/article/{id}", response_model=Article)
async def get_article(id: int, db: get_db = Depends()):
    result = ArticleService(db).get_article(id)
    return handle_result(result)


@router.get("/articles", response_model=List[Article])
async def get_articles(db: get_db = Depends()):
    result = ArticleService(db).get_articles()
    return handle_result(result)


@router.patch("/article/{id}/like", response_model=str)
async def like_article(id: int, user=Depends(get_current_user), db: get_db = Depends()):
    result = ArticleService(db).like_article(id, user.id)
    return handle_result(result)


@router.patch("/article/{id}/dislike", response_model=str)
async def dislike_article(
    id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = ArticleService(db).dislike_article(id, user.id)
    return handle_result(result)


@router.post("/review", response_model=Review)
async def create_review(data: ReviewIn, db: get_db = Depends()):
    result = ReviewService(db).create_review(data)
    return handle_result(result)


@router.get("/review/{id}", response_model=Review)
async def get_review(id: int, db: get_db = Depends()):
    result = ReviewService(db).get_review(id)
    return handle_result(result)


@router.get("/reviews", response_model=List[Review])
async def get_reviews(db: get_db = Depends()):
    result = ReviewService(db).get_reviews()
    return handle_result(result)


@router.get("/cover-pictures", response_model=List[CoverPicture])
async def get_cover_pictures(db: get_db = Depends()):
    result = CoverPictureService(db).get_cover_pictures()
    return handle_result(result)


@router.get("/cities", response_model=List[City])
async def get_cities(db: get_db = Depends()):
    result = CityService(db).get_cities()
    return handle_result(result)


@router.get("/counters", response_model=Counters)
async def get_counters(db: get_db = Depends()):
    result = CounterService(db).get_counters()
    return handle_result(result)


@router.post("/article/{id}/comment", response_model=ArticleComment)
async def create_article_comment(
    id: int,
    data: ArticleCommentIn,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = ArticleService(db).create_article_comment(id, data, user)
    return handle_result(result)


@router.get("/article/{id}/comments", response_model=List[ArticleComment])
async def get_comments_by_article(id: int, db: get_db = Depends()):
    result = ArticleService(db).get_comments_by_article(id)
    return handle_result(result)


@router.post("/article/comment/{id}/like")
async def like_comment(id: int, user=Depends(get_current_user), db: get_db = Depends()):
    result = ArticleService(db).like_comment(id, user)
    return handle_result(result)


@router.delete("/article/comment/{id}/dislike")
async def dislike_comment(
    id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = ArticleService(db).dislike_comment(id, user)
    return handle_result(result)
