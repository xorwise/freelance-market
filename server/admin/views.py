from typing import Optional, List, Any, Dict
import os
from models.user import GenderEnum, BusinessEnum, NotificationTypeEnum
from starlette.requests import Request
from starlette_admin import (
    StringField,
    IntegerField,
    BooleanField,
    EmailField,
    PasswordField,
    PhoneField,
    HasOne,
    HasMany,
    EnumField,
    TimeField,
    DateTimeField,
    FloatField,
    TextAreaField,
    ListField,
)
from starlette_admin.contrib.sqla import ModelView
from models.submission import StatusEnum
from schemas.user import Master
from utils.auth import get_hashed_password, password_context
from starlette.datastructures import UploadFile

from utils.validators import upload_file


class ClientView(ModelView):
    fields = [
        "id",
        PhoneField("phone", "Телефон", required=True),
        StringField("name", "Имя", required=True),
        StringField("lastname", "Фамилия", required=True),
        EmailField("email", "Почта", required=True),
        PasswordField("password", "Пароль", required=True),
        StringField(
            "avatar",
            "Аватарка",
            display_template="/admin/display-image.html",
            form_template="/admin/input-image.html",
        ),
        BooleanField("is_superuser", "Админ"),
        BooleanField("is_email_verified", "Почта подтверждена"),
        StringField("email_verification_code", "Код подтверждения почты"),
        BooleanField("is_phone_verified", "Телефон подтвержден"),
        StringField("phone_verification_code", "Код подтверждения телефона"),
        HasMany("master", "Мастер", identity="master"),
        HasMany("orders", "Заказы", identity="order"),
        HasMany("service_requests", "Кастомные заказы", identity="request"),
        HasMany("notifications", "Уведомления", identity="notification"),
        IntegerField("number_of_submissions", "Количество заказов"),
        StringField("password_recovery_code", "Код восстановления пароля"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "avatar", "client", entity_id, False)
        if not password_context.identify(data["password"]):
            new_password = get_hashed_password(data["password"])
            data["password"] = new_password
        return await super().validate(request, data)


class MasterView(ModelView):
    fields = [
        "id",
        StringField("username", "Имя пользователя", required=True),
        HasOne("client", "Клиент", identity="client", required=True),
        StringField("address", "Адрес", required=True),
        FloatField("address_latitude", "Широта"),
        FloatField("address_longitude", "Долгота"),
        BooleanField("is_active", "Активен"),
        BooleanField("mailing", "Email рассылка"),
        EnumField("gender", "Пол", enum=GenderEnum),
        EnumField("business_model", "Бизнес модель", enum=BusinessEnum),
        StringField("organization_name", "Название организации"),
        StringField("specialty", "Вид деятельности"),
        StringField("main_business", "Основной бизнес"),
        StringField("Status", "Статус"),
        TextAreaField("bio", "О себе"),
        TimeField("avaialability_from", "Свободен с..."),
        TimeField("avaialability_to", "Свободен до..."),
        StringField("webmoney", "WebMoney"),
        StringField("qiwi", "Qiwi"),
        StringField("credit_card", "Банковская карта"),
        HasMany("orders", "Заказы", identity="order"),
        HasMany("offers", "Предложения", identity="offer"),
        IntegerField("number_of_feedbacks", "Количество отзывов"),
        FloatField("rating", "Рейтинг"),
        HasMany("repairs", "Виды ремонта", identity="repair_type"),
        FloatField("balance", "Баланс"),
        HasMany("payments", "Платежи", identity="payment"),
        ListField(
            StringField(
                "pictures",
                label="Изображения",
                form_template="admin/input-image.html",
                display_template="admin/display-image.html",
            )
        ),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "pictures", "master", entity_id, True)
        return await super().validate(request, data)


class NotificationView(ModelView):
    fields = [
        "id",
        EnumField("type", "Тип", enum=NotificationTypeEnum, required=True),
        IntegerField("entity", "Объект", required=True),
    ]


class OrderView(ModelView):
    fields = [
        "id",
        HasOne("client", "Клиент", identity="client", required=True),
        HasOne("master", "Мастер", identity="master", required=True),
        TextAreaField("client_message", "Сообщение клиента", required=True),
        FloatField("client_price", "Цена клиента", required=True),
        EnumField("status", "Статус", enum=StatusEnum),
        DateTimeField("created_at", "Создан"),
        HasMany("repairs", "Виды ремонта", identity="repair_type", required=True),
        TextAreaField("master_message", "Сообщение мастера"),
        StringField("master_time", "Время выполнения"),
    ]


class RequestView(ModelView):
    fields = [
        "id",
        HasOne("client", "Клиент", identity="client", required=True),
        StringField("title", "Заголовок", required=True),
        TextAreaField("description", "Описание", required=True),
        ListField(
            StringField(
                "pictures",
                label="Изображения",
                form_template="admin/input-image.html",
                display_template="admin/display-image.html",
            )
        ),
        HasOne("service_type", "Вид услуги", identity="service_type", required=True),
        FloatField("client_price", "Цена клиента", required=True),
        EnumField("status", "Статус", enum=StatusEnum),
        DateTimeField("created_at", "Создан"),
        DateTimeField("expires_at", "Истекает"),
        IntegerField("number_of_offers", "Количество предложений"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "pictures", "service_request", entity_id, True)
        return await super().validate(request, data)


class OfferView(ModelView):
    fields = [
        "id",
        HasOne("master", "Мастер", identity="master", required=True),
        TextAreaField("message", "Сообщение мастера", required=True),
        HasOne("request", "Кастомный заказ", identity="request", required=True),
        FloatField("price", "Цена", required=True),
        StringField("time", "Время выполнения", required=True),
        BooleanField("is_accepted", "Принято"),
        DateTimeField("created_at", "Создано"),
    ]


class FeedbackView(ModelView):
    fields = [
        "id",
        HasOne("client", "Клиент", identity="client", required=True),
        HasOne("master", "Мастер", identity="master", required=True),
        FloatField("rating", "Оценка", required=True),
        TextAreaField("description", "Описание"),
        ListField(
            StringField(
                "pictures",
                label="Изображения",
                form_template="admin/input-image.html",
                display_template="admin/display-image.html",
            )
        ),
        DateTimeField("created_at", "Создан"),
        StringField("master_response", "Ответ мастера"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(
            data, "pictures", "submission_feedback", entity_id, True
        )
        return await super().validate(request, data)


class CategoryView(ModelView):
    fields = [
        "id",
        StringField("name", "Название", required=True),
        HasMany("services", "Услуги", identity="service_type"),
    ]


class ServiceTypeView(ModelView):
    fields = [
        "id",
        StringField("name", "Название", required=True),
        HasOne("category", "Категория", identity="category", required=True),
        HasMany("devices", "Устройства", identity="device"),
    ]


class DeviceView(ModelView):
    fields = [
        "id",
        StringField("name", "Название", required=True),
        StringField(
            "picture",
            label="Изображениe",
            form_template="admin/input-image.html",
            display_template="admin/display-image.html",
        ),
        HasOne("service", "Услуга", identity="service_type", required=True),
        HasMany("repair_types", "Виды ремонта", identity="repair_type"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "picture", "device", entity_id, False)
        return await super().validate(request, data)


class RepairTypeView(ModelView):
    fields = [
        "id",
        StringField("name", "Название", required=True),
        StringField("description", "Описание", required=True),
        FloatField("price", "Цена", required=True),
        HasOne("device", "Устройство", identity="device", required=True),
        BooleanField("is_custom", "Кастомный"),
        HasOne("master", "Создан", identity="master"),
        HasMany("masters", "Мастера", identity="master"),
    ]


class ArticleView(ModelView):
    fields = [
        "id",
        StringField("title", "Заголовок", required=True),
        TextAreaField("text", "Текст", required=True),
        StringField(
            "cover_image",
            label="Обложка",
            form_template="admin/input-image.html",
            display_template="admin/display-image.html",
        ),
        IntegerField("views", "Просмотры"),
        IntegerField("likes", "Лайки"),
        DateTimeField("created_at", "Создана"),
        HasMany("comments", "Комментарии", identity="article_comment"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "cover_image", "article", entity_id, False)
        return await super().validate(request, data)


class ArticleCommentView(ModelView):
    fields = [
        "id",
        HasOne("article", "Статья", identity="article"),
        HasOne("sender", "Отправитель", identity="client"),
        StringField("text", "Текст"),
        IntegerField("likes", "Кол-во лайков"),
        DateTimeField("created_at", "Создан"),
    ]


class ReviewView(ModelView):
    fields = [
        "id",
        StringField("sender", "Отправитель", required=True),
        IntegerField("rating", "Оценка", required=True),
        TextAreaField("message", "Сообщение"),
        DateTimeField("created_at", "Создан"),
        BooleanField("is_active", "Активно"),
    ]


class DialogView(ModelView):
    fields = [
        "id",
        HasOne("sender1", "Первый отправитель", identity="client", required=True),
        HasOne("sender2", "Второй отправитель", identity="client", required=True),
        HasOne("order", "Заказ", identity="order"),
        HasOne("request", "Кастомный заказ", identity="request"),
        HasMany("messages", "Сообщения", identity="message"),
    ]


class MessageView(ModelView):
    fields = [
        "id",
        HasOne("dialog", "Диалог", identity="dialog", required=True),
        TextAreaField("message", "Текст сообщения"),
        HasOne("sender", "Отправитель", identity="client", required=True),
        ListField(
            StringField(
                "files",
                "Файлы",
                display_template="/admin/display-image.html",
                form_template="/admin/input-file.html",
            )
        ),
        BooleanField("is_read", "Прочитано"),
        BooleanField("is_modified", "Изменено"),
        DateTimeField("sent_at", "Отправлено"),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "files", "message", entity_id, True)
        return await super().validate(request, data)


class CoverPictureView(ModelView):
    fields = [
        "id",
        StringField(
            "image",
            "Изображение",
            display_template="/admin/display-image.html",
            form_template="/admin/input-file.html",
            required=True,
        ),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        try:
            entity_id = int(str(request.url).split("/")[-1])
        except ValueError:
            entity_id = None
        data = await upload_file(data, "image", "cover_picture", entity_id, False)
        return await super().validate(request, data)


class SettingsView(ModelView):
    fields = [
        FloatField(
            "commission",
            "Комиссия",
            placeholder="Комиссия в процентах %",
            required=True,
            display_template="/admin/display-percentage.html",
            form_template="/admin/input-percentage.html",
        )
    ]

    def can_create(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        data["commission"] /= 100
        return await super().validate(request, data)


class PaymentView(ModelView):
    fields = [
        "id",
        "payment_id",
        HasOne("master", "Мастер", identity="master", required=True),
        StringField("status", "Статус"),
        BooleanField("paid", "Оплачен"),
        FloatField("amount", "Сумма", required=True),
        DateTimeField("created_at", "Создан"),
        StringField("description", "Описание"),
    ]

    def can_create(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False


class CityView(ModelView):
    fields = [
        "id",
        StringField("name", "Название", required=True),
        FloatField("latitude", "Широта", required=True),
        FloatField("longitude", "Долгота", required=True),
    ]
