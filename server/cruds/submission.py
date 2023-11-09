import datetime
import os
from typing import List

from fastapi import BackgroundTasks

from worker import delete_request
from fastapi import UploadFile
import models.user
from cruds.user import UserCRUD
from models.service import ServiceType
from models.submission import (
    Order,
    ServiceRequest,
    Offer,
    SubmissionFeedback,
    StatusEnum,
)
from models.user import Master
from models.relationship import OrderRepair
from services.main import AppCRUD
from utils.app_exceptions import AppException
from schemas.submission import (
    OrderIn,
    OrderEdit,
    RequestIn,
    RequestEdit,
    OfferIn,
    OfferEdit,
    FeedbackIn,
    FeedbackEdit,
)


class SubmissionCRUD(AppCRUD):
    async def create_order(
        self, data: OrderIn, user: models.user.Client, bg_tasks: BackgroundTasks
    ) -> Order:
        order = Order(
            client_id=user.id,
            client_message=data.client_message,
            client_price=data.client_price,
            master_username=data.master_username,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        for repair in data.repairs_id:
            order_repair = (
                self.db.query(OrderRepair)
                .filter(
                    OrderRepair.repair_id == repair, OrderRepair.order_id == order.id
                )
                .first()
            )
            if order_repair:
                continue
            order_repair = OrderRepair(repair_id=repair, order_id=order.id)
            self.db.add(order_repair)
        user.number_of_submissions += 1
        self.db.commit()

        bg_tasks.add_task(
            UserCRUD(self.db).send_mailing,
            data.master_username,
            order_id=order.id,
            request_id=None,
        )
        return order

    def get_order_by_id(self, id: int) -> Order:
        order = self.db.query(Order).filter(Order.id == id).first()
        return order

    def get_orders_by_client_id(self, client_id: int) -> List[Order]:
        orders = (
            self.db.query(Order)
            .filter(Order.client_id == client_id)
            .order_by(Order.created_at)
            .all()
        )
        return list(orders)[::-1]

    def get_orders_by_master_username(self, master: Master) -> List[Order]:
        orders = (
            self.db.query(Order)
            .filter(Order.master_username == master.username)
            .order_by(Order.created_at)
            .all()
        )
        return list(orders)[::-1]

    def update_order_by_id(
        self, id: int, data: OrderEdit, user: Master
    ) -> Order | Exception:
        order = self.db.query(Order).filter(Order.id == id).first()
        if not order:
            return AppException.NotFoundException("Заказ не найден!")
        if order.master_username != user.username:
            return AppException.ForbiddenException("Нет доступа!")
        if order.status == StatusEnum.processing:
            if data.status != StatusEnum.completed:
                return AppException.ForbiddenException("Неправильный статус!")
            order.status = data.status
        elif order.status != StatusEnum.active:
            return AppException.ForbiddenException("Заказ уже нельзя изменить!")
        if data.status:
            if data.status == StatusEnum.processing:
                user.number_of_submissions += 1
                order.master_time = data.master_time
                order.master_message = data.master_message
                UserCRUD(self.db).write_commission_off(user, order.client_price)
            order.status = data.status
        self.db.commit()
        self.db.refresh(order)
        return order

    def finish_order_by_id(
        self, id: int, status: StatusEnum, user: models.user.Client
    ) -> dict | Exception:
        order = self.db.query(Order).filter(Order.id == id).first()
        if not order:
            return AppException.NotFoundException("Заказ не найден!")
        if order.client_id != user.id:
            return AppException.ForbiddenException("Нет доступа!")

        if status not in (StatusEnum.canceled, StatusEnum.submitted):
            return AppException.ValidationException("Неправильный статус!")
        if status == StatusEnum.canceled:
            if order.status not in (StatusEnum.processing, StatusEnum.completed):
                return AppException.ValidationException("Заказ уже нельзя отменить!")
            order.status = status
            master = UserCRUD(self.db).get_master_by_username(order.master_username)
            UserCRUD(self.db).charge_commission(
                master.get("username"), order.client_price
            )
        elif status == StatusEnum.submitted:
            if order.status != StatusEnum.completed:
                return AppException.ValidationException(
                    "Дождитесь подтверждения выполнения работы мастером!"
                )
            order.status = status

        self.db.commit()
        return {"result": "Success!"}

    def remove_order_by_id(self, id: int, user_id: int) -> str | Exception:
        order = self.db.query(Order).filter(Order.id == id).first()
        if not order:
            return AppException.NotFoundException("Заказ не найден!")
        if order.client_id != user_id:
            return AppException.ForbiddenException("Нет доступа!")
        self.db.query(OrderRepair).filter(OrderRepair.order_id == order.id).delete()
        self.db.delete(order)
        self.db.commit()
        return "Success!"

    async def create_request(
        self,
        data: RequestIn,
        user: models.user.Client,
        bg_tasks: BackgroundTasks,
        files: List[UploadFile] = list,
    ) -> ServiceRequest | Exception:
        if (
            self.db.query(ServiceType)
            .filter(ServiceType.id == data.service_type_id)
            .first()
            is None
        ):
            return AppException.NotFoundException("Неверная категория услуг!")
        request = ServiceRequest(
            client_id=user.id,
            title=data.title,
            description=data.description,
            client_price=data.client_price,
            service_type_id=data.service_type_id,
            expires_at=datetime.datetime.now() + datetime.timedelta(days=1),
        )
        new_files = list()
        if files:
            for file in files:
                if os.path.exists(f"media/files/{file.filename}"):
                    i = 1
                    paths_parts = [
                        file.filename[: file.filename.rindex(".")],
                        file.filename[file.filename.rindex(".") + 1 :],
                    ]
                    while os.path.exists(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                    ):
                        i += 1
                    with open(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                    ) as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                else:
                    with open(f"media/files/{file.filename}", "wb") as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                new_files.append(link)
            request.pictures = new_files
        self.db.add(request)
        user.number_of_submissions += 1
        self.db.commit()
        self.db.refresh(request)
        delete_request.apply_async(kwargs={"request_id": request.id}, countdown=86400)

        bg_tasks.add_task(
            UserCRUD(self.db).send_mailing,
            "__all__",
            order_id=None,
            request_id=request.id,
        )
        return request

    def get_request_by_id(self, id: int) -> ServiceRequest:
        request = self.db.query(ServiceRequest).filter(ServiceRequest.id == id).first()
        request.views += 1
        self.db.commit()
        self.db.refresh(request)
        return request

    def get_requests(self, user_id: int) -> List[ServiceRequest]:
        requests = (
            self.db.query(ServiceRequest)
            .filter(
                ServiceRequest.status != "В процессе",
                ServiceRequest.client_id != user_id,
            )
            .order_by(ServiceRequest.created_at)
            .all()
        )
        return list(requests)[::-1]

    def get_requests_by_client_id(self, client_id) -> List[ServiceRequest]:
        requests = (
            self.db.query(ServiceRequest)
            .filter(ServiceRequest.client_id == client_id)
            .order_by(ServiceRequest.created_at)
            .all()
        )
        return list(requests)[::-1] if len(requests) else []

    def update_request_by_id(
        self, id: int, data: RequestEdit, user_id: int
    ) -> ServiceRequest | Exception:
        request = self.db.query(ServiceRequest).filter(ServiceRequest.id == id).first()
        if not request:
            return AppException.NotFoundException("Заявка не найдена!")
        if request.client_id != user_id:
            return AppException.ForbiddenException("Нет доступа!")
        if request.status == StatusEnum.completed:
            if data.status not in (StatusEnum.submitted, StatusEnum.canceled):
                return AppException.ValidationException("Неправильный статус!")
            request.status = data.status
            self.db.commit()
            self.db.refresh(request)
            return request

        if request.status == StatusEnum.processing:
            if data.status != StatusEnum.canceled:
                return AppException.ValidationException("Неправильный статус!")
            if data.status == StatusEnum.submitted:
                return AppException.ValidationException(
                    "Дождитесь, пока мастер подтвердит выполнение заказа!"
                )
            request.status = StatusEnum.canceled
            offer = (
                self.db.query(Offer)
                .filter(Offer.request_id == request.id, Offer.is_accepted is True)
                .first()
            )
            if not offer:
                return AppException.NotFoundException("Предложение не найдено!")
            UserCRUD(self.db).charge_commission(offer.master_username, offer.price)
            self.db.commit()
            self.db.refresh(request)
            return request

        if request.status not in (StatusEnum.active, StatusEnum.paused):
            return AppException.ForbiddenException("Заявка уже выполняется!")

        dict_data = data.model_dump(exclude_unset=True)
        for attr in dict_data:
            if hasattr(request, attr):
                setattr(request, attr, dict_data[attr])
        self.db.commit()
        self.db.refresh(request)
        return request

    def complete_request_by_id(self, id: int, master: Master, status: StatusEnum):
        request = self.db.query(ServiceRequest).filter(ServiceRequest.id == id).first()
        if not request:
            return AppException.NotFoundException("Кастомный заказ не найден!")
        offer = (
            self.db.query(Offer)
            .filter(
                Offer.request_id == request.id,
                Offer.master_username == master.username,
                Offer.is_accepted == True,
            )
            .first()
        )
        if not offer:
            return AppException.ForbiddenException("Вы не можете изменять этот заказ!")

        if status != StatusEnum.completed:
            return AppException.ValidationException("Неправильный статус!")
        request.status = status
        self.db.commit()
        return {"result": "Success!"}

    def remove_request_by_id(self, id: int, user_id: int) -> str | Exception:
        request = self.db.query(ServiceRequest).filter(ServiceRequest.id == id).first()
        if not request:
            return AppException.NotFoundException("Заявка не найдена!")
        if request.status not in ("Активно", "Приостановлено"):
            return AppException.ValidationException("Заявка уже выполняется!")
        if request.client_id != user_id:
            return AppException.ForbiddenException("Нет доступа!")

        self.db.delete(request)
        self.db.commit()
        return "Success!"

    def create_offer(self, data: OfferIn, master_username: str) -> Offer | Exception:
        offer = (
            self.db.query(Offer)
            .filter(
                Offer.request_id == data.request_id,
                Offer.master_username == master_username,
            )
            .first()
        )
        if offer is not None:
            return AppException.AlreadyExistsException("Предложение уже создано!")

        offer = Offer(
            master_username=master_username,
            message=data.message,
            request_id=data.request_id,
            price=data.price,
            time=data.time,
        )
        self.db.add(offer)
        request = (
            self.db.query(ServiceRequest)
            .filter(ServiceRequest.id == data.request_id)
            .first()
        )
        if not request:
            return AppException.NotFoundException("Заказ не найден!")
        request.number_of_offers += 1
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_offer_by_submission(self, request_id: int | None, username: str) -> Offer:
        offer = (
            self.db.query(Offer)
            .filter(Offer.request_id == request_id, Offer.master_username == username)
            .first()
        )
        return offer

    def get_offers_by_submission(self, request_id: int | None) -> List[Offer]:
        offers = self.db.query(Offer).filter(Offer.request_id == request_id).all()
        return list(offers) if len(offers) else []

    def get_offers_by_master(self, master_username: str) -> List[Offer]:
        offers = (
            self.db.query(Offer).filter(Offer.master_username == master_username).all()
        )
        return list(offers) if len(offers) else []

    def update_offer_by_id(
        self, id: int, data: OfferEdit, master_username: str
    ) -> Offer | Exception:
        offer = self.db.query(Offer).filter(Offer.id == id).first()
        if not offer:
            return AppException.NotFoundException("Предложение не найдено!")
        if offer.master_username != master_username:
            return AppException.ForbiddenException("Нет доступа!")
        if offer.is_accepted:
            return AppException.ForbiddenException("Предложение уже принято!")

        dict_data = data.model_dump(exclude_unset=True)
        for attr in dict_data:
            if hasattr(offer, attr):
                setattr(offer, attr, dict_data[attr])
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def accept_offer(self, id: int, client: models.user.Client) -> Exception | dict:
        offer = self.db.query(Offer).filter(Offer.id == id).first()
        if not offer:
            return AppException.NotFoundException("Предложение не найдено!")
        if offer.request.client_id != client.id:
            return AppException.ForbiddenException("Нет доступа!")
        UserCRUD(self.db).write_commission_off(offer.master, offer.price)
        offer.request.status = StatusEnum.processing
        offer.is_accepted = True
        offer.master.number_of_submissions += 1
        self.db.commit()
        return {"result": "Success!", "master_id": offer.master.client_id}

    def delete_offer_by_id(self, id: int, master_username: str) -> str | Exception:
        offer = self.db.query(Offer).filter(Offer.id == id).first()
        if not offer:
            return AppException.NotFoundException("Предложение не найдено!")
        if offer.master_username != master_username:
            return AppException.ForbiddenException("Нет доступа!")

        self.db.delete(offer)
        self.db.commit()
        return "Success!"

    def create_feedback(
        self, data: FeedbackIn, user_id: int, pictures: List[UploadFile] = None
    ) -> SubmissionFeedback | Exception:
        feedback = (
            self.db.query(SubmissionFeedback)
            .filter(
                SubmissionFeedback.client_id == user_id,
                SubmissionFeedback.master_username == data.master_username,
            )
            .first()
        )
        if feedback:
            return AppException.AlreadyExistsException("Отзыв уже существует!")

        new_feedback = SubmissionFeedback(
            client_id=user_id,
            rating=data.rating,
            description=data.description,
            master_username=data.master_username,
        )
        if pictures:
            new_files = list()
            for file in pictures:
                if os.path.exists(f"media/files/{file.filename}"):
                    i = 1
                    paths_parts = [
                        file.filename[: file.filename.rindex(".")],
                        file.filename[file.filename.rindex(".") + 1 :],
                    ]
                    while os.path.exists(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                    ):
                        i += 1
                    with open(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                    ) as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                else:
                    with open(f"media/files/{file.filename}", "wb") as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                new_files.append(link)
            new_feedback.pictures = new_files
        self.db.add(new_feedback)

        master = (
            self.db.query(Master)
            .filter(Master.username == new_feedback.master_username)
            .first()
        )
        if not master:
            return AppException.NotFoundException("Мастер не найден!")
        sum_of_ratings = master.rating * master.number_of_feedbacks
        sum_of_ratings += new_feedback.rating
        master.number_of_feedbacks += 1
        master.rating = sum_of_ratings / master.number_of_feedbacks

        self.db.commit()
        self.db.refresh(new_feedback)
        return new_feedback

    def get_feedback_by_offer(
        self,
        offer_id: int | None,
        order_id: int | None,
        user_id: int = None,
        master_username: str = None,
    ) -> SubmissionFeedback | Exception:
        feedback = (
            self.db.query(SubmissionFeedback)
            .filter(
                SubmissionFeedback.offer_id == offer_id,
                SubmissionFeedback.order_id == order_id,
            )
            .first()
        )
        if not feedback:
            return AppException.NotFoundException("Отзыв не найден!")
        if not (
            feedback.client_id == user_id or feedback.master_username == master_username
        ):
            return AppException.ForbiddenException("Нет доступа!")
        return feedback

    def get_feedbacks_by_master(self, master_username: str) -> List[SubmissionFeedback]:
        feedbacks = (
            self.db.query(SubmissionFeedback)
            .filter(SubmissionFeedback.master_username == master_username)
            .all()
        )
        return list(feedbacks)

    def update_feedback_by_id(
        self, id: int, data: FeedbackEdit, master: Master
    ) -> SubmissionFeedback | Exception:
        feedback = (
            self.db.query(SubmissionFeedback)
            .filter(SubmissionFeedback.id == id)
            .first()
        )
        if not feedback:
            return AppException.NotFoundException("Отзыв не найден!")
        if feedback.master_username != master.username:
            return AppException.ForbiddenException("Нет доступа!")
        feedback.master_response = data.master_response

        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def delete_feedback_by_id(self, id: int, user_id: int) -> str | Exception:
        feedback = (
            self.db.query(SubmissionFeedback)
            .filter(SubmissionFeedback.id == id)
            .first()
        )
        if not feedback:
            return AppException.NotFoundException("Отзыв не найден!")
        if feedback.client_id != user_id:
            return AppException.ForbiddenException("Нет доступа!")

        master = (
            self.db.query(Master)
            .filter(Master.username == feedback.master_username)
            .first()
        )

        sum_of_ratings = master.rating * master.number_of_feedbacks
        sum_of_ratings -= feedback.rating
        master.number_of_feedbacks -= 1
        master.rating = sum_of_ratings / master.number_of_feedbacks

        self.db.delete(feedback)
        self.db.commit()
        return "Success!"

    def get_requests_by_master_username(self, master: Master) -> List[ServiceRequest]:
        offers = (
            self.db.query(Offer).filter(Offer.master_username == master.username).all()
        )
        new_requests = list()
        for offer in offers:
            new_requests.append(offer.request)
        return sorted(new_requests, key=lambda req: req.created_at, reverse=True)
