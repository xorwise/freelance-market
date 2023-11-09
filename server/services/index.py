import models.user
from schemas.index import ReviewIn, Counters, ArticleCommentIn
from cruds.index import IndexCRUD
from services.main import AppService
from utils.service_result import ServiceResult


class ArticleService(AppService):
    def get_article(self, id: int) -> ServiceResult:
        article = IndexCRUD(self.db).get_article_by_id(id)
        return ServiceResult(article)

    def get_articles(self) -> ServiceResult:
        articles = IndexCRUD(self.db).get_articles()
        return ServiceResult(articles)

    def like_article(self, id: int, user_id: int) -> ServiceResult:
        article = IndexCRUD(self.db).like_article_by_id(id, user_id)
        return ServiceResult(article)

    def dislike_article(self, id: int, user_id: int) -> ServiceResult:
        article = IndexCRUD(self.db).dislike_article_by_id(id, user_id)
        return ServiceResult(article)

    def create_article_comment(
        self, article_id: int, data: ArticleCommentIn, client: models.user.Client
    ) -> ServiceResult:
        comment = IndexCRUD(self.db).create_article_comment(article_id, data, client.id)
        return ServiceResult(comment)

    def get_comments_by_article(self, article_id: int) -> ServiceResult:
        comments = IndexCRUD(self.db).get_comments_by_article_id(article_id)
        return ServiceResult(comments)

    def like_comment(self, comment_id: int, user: models.user.Client) -> ServiceResult:
        response = IndexCRUD(self.db).like_comment_by_id(comment_id, user.id)
        return ServiceResult(response)

    def dislike_comment(
        self, comment_id: int, user: models.user.Client
    ) -> ServiceResult:
        response = IndexCRUD(self.db).dislike_comment_by_id(comment_id, user.id)
        return ServiceResult(response)


class ReviewService(ArticleService):
    def create_review(self, data: ReviewIn) -> ServiceResult:
        review = IndexCRUD(self.db).create_review(data)
        return ServiceResult(review)

    def get_review(self, id: int) -> ServiceResult:
        review = IndexCRUD(self.db).get_review_by_id(id)
        return ServiceResult(review)

    def get_reviews(self) -> ServiceResult:
        reviews = IndexCRUD(self.db).get_reviews()
        return ServiceResult(reviews)


class CoverPictureService(AppService):
    def get_cover_pictures(self) -> ServiceResult:
        pictures = IndexCRUD(self.db).get_all_cover_pictures()
        return ServiceResult(pictures)


class CityService(AppService):
    def get_cities(self) -> ServiceResult:
        cities = IndexCRUD(self.db).get_all_cities()
        return ServiceResult(cities)


class CounterService(AppService):
    def get_counters(self) -> ServiceResult:
        counters = IndexCRUD(self.db).get_all_counters()
        new_counters = Counters(**counters)
        return ServiceResult(new_counters)
