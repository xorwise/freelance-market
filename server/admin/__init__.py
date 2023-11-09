from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from config.database import engine
from models.user import Client, Notification, Master as DBMaster, Payment
from models.submission import *
from models.service import *
from models.index import *
from models.chat import *
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin import DropDown
from admin.provider import MyAuthProvider
from .views import *


admin = Admin(
    engine,
    base_url='',
    auth_provider=MyAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key='test')],
)


admin.add_view(SettingsView(Settings, label='Настройки'))

admin.add_view(
    DropDown(
        'Пользователи',
        views=[
            ClientView(Client, label='Клиенты', identity='client'),
            MasterView(DBMaster, label='Мастера', identity='master'),
            NotificationView(Notification, label='Уведомления', identity='notification'),
            PaymentView(Payment, label='Платежи', identity='payment')
        ]
    )
)

admin.add_view(DropDown(
    'Заказы',
    views=[
        OrderView(Order, label='Заказы', identity='order'),
        RequestView(ServiceRequest, label='Кастомные заказы', identity='request'),
        OfferView(Offer, label='Предложения мастеров', identity='offer'),
        FeedbackView(SubmissionFeedback, label='Отзывы о заказах')
    ]
))

admin.add_view(DropDown(
    'Услуги',
    views=[
        CategoryView(ServiceCategory, label='Категории', identity='category'),
        ServiceTypeView(ServiceType, label='Марки девайсов', identity='service_type'),
        DeviceView(Device, label='Модели девайсов', identity='device'),
        RepairTypeView(RepairType, label='Виды ремонта', identity='repair_type')
    ]
))

admin.add_view(DropDown(
    'Главная страница',
    views=[
        ArticleView(Article, label='Статьи', identity='article'),
        ArticleCommentView(ArticleComment, label='Комментарии к статьям', identity='article_comment'),
        ReviewView(Review, label='Отзывы'),
        CoverPictureView(CoverPicture, label='Изображения на обложке'),
        CityView(City, label='Города')
    ]
))

admin.add_view(DropDown(
    'Чат',
    views=[
        DialogView(Dialog, label='Диалоги', identity='dialog'),
        MessageView(Message, label='Сообщения', identity='message')
    ]
))