import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,
    DateTime,
    Boolean, PickleType
)
from starlette.requests import Request
from sqlalchemy.orm import relationship
from config.database import Base
from sqlalchemy.orm import Mapped
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.types import ARRAY
from sqlalchemy.ext.mutable import MutableList


class StatusEnum(str, enum.Enum):
    active = 'Активно'
    paused = 'Приостановлено'
    processing = 'В процессе'
    declined = 'Отказано'
    completed = 'Выполнено'
    submitted = 'Подтверждено'
    canceled = 'Отменено'


# noinspection PyUnresolvedReferences
class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    client: Mapped['Client'] = relationship('Client', back_populates='orders')
    master_username = Column(String, ForeignKey('master.username', ondelete='CASCADE'), nullable=False)
    master: Mapped['Master'] = relationship('Master', back_populates='orders')
    client_message = Column(Text, nullable=False)
    client_price = Column(Float, nullable=False)
    status = Column(String, default='Активно')
    repairs: Mapped[List['RepairType']] = relationship('RepairType', secondary='order_repair')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    master_message = Column(Text, nullable=True)
    master_time = Column(String, nullable=True)

    async def __admin_repr__(self, request: Request):
        return f'Заказ №{self.id}'


# noinspection PyUnresolvedReferences
class ServiceRequest(Base):
    __tablename__ = 'service_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    client: Mapped['Client'] = relationship('Client', back_populates='service_requests')
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    pictures = Column(MutableList.as_mutable(PickleType), default=[])
    service_type_id = Column(Integer, ForeignKey('service_type.id'), nullable=True)
    service_type: Mapped['ServiceType'] = relationship('ServiceType')
    client_price = Column(Float, nullable=False)
    status = Column(String, default='Активно')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)
    number_of_offers = Column(Integer, default=0)
    views = Column(Integer, default=0)

    async def __admin_repr__(self, request: Request):
        return self.title


# noinspection PyUnresolvedReferences
class Offer(Base):
    __tablename__ = 'offer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_username = Column(String, ForeignKey('master.username'), nullable=False)
    master: Mapped['Master'] = relationship('Master')
    message = Column(Text, nullable=False, default='')
    request_id = Column(Integer, ForeignKey('service_request.id', ondelete='CASCADE'), nullable=True)
    request: Mapped['ServiceRequest'] = relationship('ServiceRequest')
    price = Column(Float, nullable=False)
    time = Column(String, nullable=False)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    async def __admin_repr__(self, request: Request):
        return f'Предложение №{self.id}'


# noinspection PyUnresolvedReferences
class SubmissionFeedback(Base):
    __tablename__ = 'submission_feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    client: Mapped['Client'] = relationship('Client')
    master_username = Column(String, ForeignKey('master.username', ondelete='CASCADE'), nullable=False)
    master: Mapped['Master'] = relationship('Master')
    rating = Column(Integer, nullable=False, default=3)
    description = Column(Text, nullable=True)
    pictures = Column(MutableList.as_mutable(PickleType), default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    master_response = Column(String, nullable=True)

    async def __admin_repr__(self, request: Request):
        return f'Отзыв №{self.id}'
