from datetime import datetime

from sqlalchemy.ext.mutable import MutableList
from starlette.requests import Request
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Time,
    Enum,
    Text,
    ForeignKey,
    Float,
    DateTime, PickleType,

)
import enum
from config.database import Base
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column("phone", String(15), unique=True, nullable=False)
    name = Column("name", String(50), nullable=False)
    lastname = Column("lastname", String(50), nullable=False)
    email = Column("email", String(200), unique=True, nullable=False)
    password = Column("password", String(), nullable=False)
    avatar = Column("avatar", String(), nullable=True, default='files/user.png')
    is_superuser = Column("is_superuser", Boolean(), nullable=False, server_default='False')
    is_email_verified = Column('is_active', Boolean, default=False)
    email_verification_code = Column('email_verification_code', String, nullable=True, default=None)
    is_phone_verified = Column('is_phone_verified', Boolean, default=False)
    phone_verification_code = Column('phone_verification_code', String, nullable=True, default=None)
    master: Mapped['Master'] = relationship('Master', back_populates='client', cascade='all,delete-orphan')
    orders: Mapped[List['Order']] = relationship('Order', back_populates='client')
    service_requests: Mapped[List['ServiceRequest']] = relationship('ServiceRequest', back_populates='client')
    notifications: Mapped[List['Notification']] = relationship('Notification', cascade='all,delete-orphan')
    number_of_submissions = Column(Integer, default=0)
    password_recovery_code = Column(String, nullable=True)

    async def __admin_repr__(self, request: Request):
        return f'{self.name} {self.lastname}'

    async def __admin_select2_repr__(self, request: Request) -> str:
        return f'<div><img src="http://localhost:8000/{self.avatar}" width="35" height="35"><span>' \
               f'{self.name} {self.lastname}</span></div>'


class GenderEnum(str, enum.Enum):
    male = 'Мужской'
    female = 'Женский'
    other = 'Другой'


class BusinessEnum(str, enum.Enum):
    individual = 'Частный мастер'
    service = 'Сервис'


class NotificationTypeEnum(enum.Enum):
    get_online_users = 1
    sent_message = 2
    accepted_order = 3
    new_offer = 4
    accepted_offer = 5


class Master(Base):
    __tablename__ = "master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), unique=True)
    client: Mapped['Client'] = relationship('Client', back_populates='master')
    username = Column("username", String(50), nullable=False, unique=True)
    address = Column("address", String(), nullable=False)
    address_latitude = Column("address_latitude", Float(), nullable=True)
    address_longitude = Column('address_longitude', Float(), nullable=True)
    is_active = Column("is_active", Boolean, default=True)
    mailing = Column('mailing', Boolean, default=False)
    gender = Column("gender", Enum(GenderEnum), nullable=True, default=GenderEnum.other)
    business_model = Column("service_type", Enum(BusinessEnum), nullable=True, default=BusinessEnum.individual)
    organization_name = Column("organization_name", String(50), nullable=True, server_default='')
    specialty = Column("specialty", String(100), nullable=True, server_default='')
    main_business = Column("main_business", String(100), nullable=True, server_default='')
    status = Column("status", String(40), nullable=True, server_default='')
    bio = Column("bio", Text(), nullable=True, server_default='')
    availability_from = Column("availability_from", Time(), nullable=True)
    availability_to = Column("availability_to", Time(), nullable=True)
    webmoney = Column("webmoney", String(100), nullable=True, server_default='')
    qiwi = Column("qiwi", String(20), nullable=True, server_default='')
    credit_card = Column("credit_card", String(20), nullable=True, server_default='')
    orders: Mapped[List['Order']] = relationship('Order', back_populates='master', cascade='all,delete-orphan')
    offers: Mapped[List['Offer']] = relationship('Offer', back_populates='master', cascade='all,delete-orphan')
    number_of_feedbacks = Column('number_of_feedbacks', Integer, default=0)
    number_of_submissions = Column(Integer, default=0)
    rating = Column('rating', Float, default=0)
    repairs: Mapped[List['RepairType']] = relationship('RepairType', back_populates='masters',
                                                       secondary='master_repair')
    balance = Column(Float, default=0)
    payments: Mapped[List['Payment']] = relationship('Payment', back_populates='master', cascade='all,delete-orphan')
    pictures = Column(MutableList.as_mutable(PickleType), default=[])


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("client.id", ondelete="CASCADE"), unique=True)
    refresh_token = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now())
    user = relationship("Client")


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(NotificationTypeEnum), nullable=False)
    receiver_id = Column(Integer, ForeignKey("client.id", ondelete="CASCADE"), nullable=False)
    entity = Column(Integer, nullable=False)


class Payment(Base):
    __tablename__ = "payment"

    master_username = Column(String, ForeignKey('master.username', ondelete="CASCADE"), nullable=False)
    master: Mapped['Master'] = relationship('Master', back_populates='payments')
    id = Column(UUID(as_uuid=True), primary_key=True)
    payment_id = Column(UUID(as_uuid=True), unique=True, nullable=True)
    status = Column(String, nullable=True)
    paid = Column(Boolean, default=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(String, nullable=True)
    is_confirmed = Column(Boolean, default=False)

