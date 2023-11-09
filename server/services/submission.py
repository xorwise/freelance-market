from fastapi import HTTPException, UploadFile, BackgroundTasks
from typing import List

from models import StatusEnum
from utils.app_exceptions import AppException
from cruds.submission import SubmissionCRUD
from services.main import AppService
from utils.service_result import ServiceResult
from schemas.submission import (
    OrderIn,
    OrderEdit,
    RequestIn,
    RequestEdit,
    OfferIn,
    OfferEdit,
    FeedbackIn,
    FeedbackEdit,
    Feedback,
)
import models
from cruds.user import UserCRUD


class OrderService(AppService):
    async def create_order(
        self, data: OrderIn, user: models.user.Client, bg_tasks: BackgroundTasks
    ):
        order = await SubmissionCRUD(self.db).create_order(data, user, bg_tasks)
        if not order:
            return AppException.CreationException(detail="Не удалось создать заказ!")
        return ServiceResult(order)

    def get_order(self, id: int) -> ServiceResult:
        order = SubmissionCRUD(self.db).get_order_by_id(id)
        if not order:
            return ServiceResult(
                AppException.NotFoundException(detail="Заказ не найден!")
            )
        return ServiceResult(order)

    def get_orders_by_client(self, client_id: int) -> ServiceResult:
        orders = SubmissionCRUD(self.db).get_orders_by_client_id(client_id)
        return ServiceResult(orders)

    def get_orders_by_master(self, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        if not master:
            return ServiceResult(AppException.NotFoundException("Мастер не найден!"))
        orders = SubmissionCRUD(self.db).get_orders_by_master_username(master)
        return ServiceResult(orders)

    def patch_order(
        self, id: int, data: OrderEdit, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        new_order = SubmissionCRUD(self.db).update_order_by_id(id, data, master)
        if not new_order:
            return ServiceResult(AppException.NotFoundException("Not found!"))
        return ServiceResult(new_order)

    def finish_order(
        self, id: int, status: StatusEnum, user: models.user.Client
    ) -> ServiceResult:
        response = SubmissionCRUD(self.db).finish_order_by_id(id, status, user)
        return ServiceResult(response)

    def delete_order(self, id: int, user: models.user.Client) -> ServiceResult:
        response = SubmissionCRUD(self.db).remove_order_by_id(id, user.id)
        return ServiceResult(response)


class RequestService(AppService):
    async def create_request(
        self,
        data: RequestIn,
        user: models.user.Client,
        bg_tasks: BackgroundTasks,
        files: List[UploadFile],
    ) -> ServiceResult:
        request = await SubmissionCRUD(self.db).create_request(
            data, user, bg_tasks, files
        )
        if not request:
            return ServiceResult(AppException.NotFoundException("Not found!"))
        return ServiceResult(request)

    def get_request(self, id: int) -> ServiceResult:
        request = SubmissionCRUD(self.db).get_request_by_id(id)
        if not request:
            return ServiceResult(AppException.NotFoundException("Заявка не найдена!"))
        return ServiceResult(request)

    def get_requests(self, user_id: int) -> ServiceResult:
        requests = SubmissionCRUD(self.db).get_requests(user_id)
        return ServiceResult(requests)

    def get_requests_by_master(self, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        requests = SubmissionCRUD(self.db).get_requests_by_master_username(master)
        return ServiceResult(requests)

    def get_requests_by_client_id(self, client_id: int) -> ServiceResult:
        requests = SubmissionCRUD(self.db).get_requests_by_client_id(client_id)
        return ServiceResult(requests)

    def patch_request(self, id: int, data: RequestEdit, user_id: int) -> ServiceResult:
        request = SubmissionCRUD(self.db).update_request_by_id(id, data, user_id)
        if not request:
            return ServiceResult(AppException.NotFoundException("Заявка не найдена!"))
        return ServiceResult(request)

    def complete_request(
        self, id: int, user: models.user.Client, status: StatusEnum
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        response = SubmissionCRUD(self.db).complete_request_by_id(id, master, status)
        return ServiceResult(response)

    def delete_request(self, id: int, user_id: int) -> ServiceResult:
        response = SubmissionCRUD(self.db).remove_request_by_id(id, user_id)
        return ServiceResult(response)


class OfferService(AppService):
    def create_offer(self, data: OfferIn, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        offer = SubmissionCRUD(self.db).create_offer(data, master.username)
        if not offer:
            return ServiceResult(AppException.NotFoundException("Not found!"))
        return ServiceResult(offer)

    def get_offer(self, request_id: int, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        offer = SubmissionCRUD(self.db).get_offer_by_submission(
            request_id, master.username
        )
        if not offer:
            return ServiceResult(
                AppException.NotFoundException("Предложение не найдено!")
            )
        return ServiceResult(offer)

    def get_offers_by_submission(self, request_id: int):
        offers = SubmissionCRUD(self.db).get_offers_by_submission(request_id)
        return ServiceResult(offers)

    def get_offers_by_master(self, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        offers = SubmissionCRUD(self.db).get_offers_by_master(master.username)
        return ServiceResult(offers)

    def patch_offer(
        self, id: int, data: OfferEdit, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        offer = SubmissionCRUD(self.db).update_offer_by_id(id, data, master.username)
        if not offer:
            return ServiceResult(
                AppException.NotFoundException("Предложение не найдено!")
            )
        return ServiceResult(offer)

    def accept_offer(self, id: int, user: models.user.Client) -> ServiceResult:
        response = SubmissionCRUD(self.db).accept_offer(id, user)
        return ServiceResult(response)

    def delete_offer(self, id: int, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        response = SubmissionCRUD(self.db).delete_offer_by_id(id, master.username)
        return ServiceResult(response)


class FeedbackService(AppService):
    def create_feedback(
        self, data: FeedbackIn, user_id: int, pictures: List[UploadFile] = None
    ) -> ServiceResult:
        feedback = SubmissionCRUD(self.db).create_feedback(data, user_id, pictures)
        if not feedback:
            return ServiceResult(AppException.NotFoundException("Not found!"))
        return ServiceResult(feedback)

    def get_feedback(
        self, offer_id: int | None, order_id: int | None, user: models.user.Client
    ) -> ServiceResult:
        try:
            master = UserCRUD(self.db).get_master_by_client(user)
            master_username = master.username
        except HTTPException:
            master_username = None
        feedback = SubmissionCRUD(self.db).get_feedback_by_offer(
            offer_id, order_id, user.id, master_username
        )
        return ServiceResult(feedback)

    def get_feedbacks(self, master_username: str) -> ServiceResult:
        feedbacks = SubmissionCRUD(self.db).get_feedbacks_by_master(master_username)
        new_feedbacks = list()
        for feedback in feedbacks:
            pydantic_feedback = Feedback(**feedback.__dict__)
            pydantic_feedback.client_avatar = feedback.client.avatar
            pydantic_feedback.client_name = feedback.client.name
            pydantic_feedback.client_lastname = feedback.client.lastname
            pydantic_feedback.master_name = feedback.master.client.name
            pydantic_feedback.master_lastname = feedback.master.client.lastname
            pydantic_feedback.master_avatar = feedback.master.client.avatar

            new_feedbacks.append(pydantic_feedback)
        return ServiceResult(new_feedbacks)

    def patch_feedback(
        self, id: int, data: FeedbackEdit, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        new_feedback = SubmissionCRUD(self.db).update_feedback_by_id(id, data, master)
        return ServiceResult(new_feedback)

    def delete_feedback(self, id: int, user_id: int) -> ServiceResult:
        response = SubmissionCRUD(self.db).delete_feedback_by_id(id, user_id)
        return ServiceResult(response)
