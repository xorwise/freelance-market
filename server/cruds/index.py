from typing import List

from models import Order, ServiceRequest
from models.user import Master
from models.index import Article, Review, CoverPicture, City, ArticleComment
from models.relationship import ArticleLike, ArticleCommentLike
from schemas.index import ReviewIn, ArticleCommentIn
from services.main import AppCRUD
from utils.app_exceptions import AppException


class IndexCRUD(AppCRUD):
    def get_article_by_id(self, id: int) -> Article | Exception:
        article = self.db.query(Article).filter(Article.id == id).first()
        if not article:
            return AppException.NotFoundException("Статья не найдена!")
        article.views += 1
        self.db.commit()
        return article

    def get_articles(self) -> List[Article]:
        articles = self.db.query(Article).order_by(Article.created_at).all()
        return list(articles)[::-1]

    def like_article_by_id(self, id: int, user_id: int) -> str | Exception:
        article = self.db.query(Article).filter(Article.id == id).first()
        if not article:
            return AppException.NotFoundException("Статья не найдена!")
        if (
            not self.db.query(ArticleLike)
            .filter(
                ArticleLike.article_id == article.id, ArticleLike.client_id == user_id
            )
            .first()
        ):
            article.likes += 1
            article_like = ArticleLike(article_id=article.id, client_id=user_id)
            self.db.add(article_like)
            self.db.commit()
            return "Success!"
        return "Failed!"

    def dislike_article_by_id(self, id: int, user_id: int) -> str | Exception:
        article = self.db.query(Article).filter(Article.id == id).first()
        if not article:
            return AppException.NotFoundException("Статья не найдена!")
        article_like = (
            self.db.query(ArticleLike)
            .filter(ArticleLike.article_id == id, ArticleLike.client_id == user_id)
            .first()
        )
        if article_like:
            article.likes -= 1
            self.db.delete(article_like)
            self.db.commit()
            return "Success!"
        return "Failed!"

    def create_review(self, data: ReviewIn) -> Review:
        review = Review(sender=data.sender, rating=data.rating, message=data.message)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_review_by_id(self, id: int) -> Review | Exception:
        review = self.db.query(Review).filter(Review.id == id).first()
        if not review:
            return AppException.NotFoundException("Отзыв не найден!")
        if not review.is_active:
            return AppException.ForbiddenException("Отзыв не прошел проверку!")
        return review

    def get_reviews(self) -> List[Review]:
        reviews = self.db.query(Review).filter(Review.is_active == True).all()
        return list(reviews)

    def get_all_cover_pictures(self) -> List[CoverPicture]:
        cover_pictures = self.db.query(CoverPicture).all()
        return list(cover_pictures)

    def get_all_cities(self) -> List[City]:
        cities = self.db.query(City).all()
        return list(cities)

    def get_all_counters(self) -> dict:
        masters = self.db.query(Master).count()
        orders = self.db.query(Order).count()
        requests = self.db.query(ServiceRequest).count()
        return {"masters": masters, "submissions": orders + requests}

    def create_article_comment(
        self, article_id: int, data: ArticleCommentIn, client_id: int
    ) -> ArticleComment:
        comment = ArticleComment(
            article_id=article_id, sender_id=client_id, text=data.text
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments_by_article_id(self, article_id: int) -> List[ArticleComment]:
        comments = (
            self.db.query(ArticleComment)
            .filter(ArticleComment.article_id == article_id)
            .all()
        )
        return list(comments)

    def like_comment_by_id(self, comment_id: int, client_id: int) -> dict | Exception:
        comment_like = (
            self.db.query(ArticleCommentLike)
            .filter(
                ArticleCommentLike.comment_id == comment_id,
                ArticleCommentLike.client_id == client_id,
            )
            .first()
        )
        if comment_like:
            return AppException.ForbiddenException(
                "Вы уже поставили лайк на этот комментарий!"
            )
        comment = (
            self.db.query(ArticleComment)
            .filter(ArticleComment.id == comment_id)
            .first()
        )
        if not comment:
            return AppException.NotFoundException("Комментарий не найден!")
        comment.likes += 1
        new_comment_like = ArticleCommentLike(
            comment_id=comment_id, client_id=client_id
        )
        self.db.add(new_comment_like)
        self.db.commit()
        return {"result": "Success!"}

    def dislike_comment_by_id(
        self, comment_id: int, client_id: int
    ) -> dict | Exception:
        comment_like = (
            self.db.query(ArticleCommentLike)
            .filter(
                ArticleCommentLike.comment_id == comment_id,
                ArticleCommentLike.client_id == client_id,
            )
            .first()
        )
        if not comment_like:
            return AppException.NotFoundException(
                "Вы не ставили лайк этому комментарию!"
            )
        comment = (
            self.db.query(ArticleComment)
            .filter(ArticleComment.id == comment_id)
            .first()
        )
        comment.likes -= 1
        self.db.delete(comment_like)
        self.db.commit()
        return {"result": "Success!"}
