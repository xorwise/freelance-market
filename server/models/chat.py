import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime, ARRAY, String, PickleType
)
from sqlalchemy.orm import Mapped, relationship
from starlette.requests import Request
from sqlalchemy.ext.mutable import MutableList
from config.database import Base


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dialog_id = Column(Integer, ForeignKey('dialog.id', ondelete='CASCADE'), nullable=False)
    dialog: Mapped['Dialog'] = relationship('Dialog', back_populates='messages')
    sender_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    sender: Mapped['Client'] = relationship('Client')
    message = Column(Text, nullable=False)
    files = Column(MutableList.as_mutable(PickleType), default=[])
    is_read = Column(Boolean, default=False)
    is_modified = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    async def __admin_repr__(self, request: Request):
        return self.message[:25]


class Dialog(Base):
    __tablename__ = 'dialog'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=True, unique=True)
    order = relationship('Order')
    request_id = Column(Integer, ForeignKey('service_request.id', ondelete='CASCADE'), nullable=True, unique=True)
    request = relationship('ServiceRequest')
    sender1_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    sender1 = relationship('Client', foreign_keys=[sender1_id])
    sender2_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    sender2 = relationship('Client', foreign_keys=[sender2_id])
    messages: Mapped[List['Message']] = relationship('Message', back_populates='dialog', cascade='all,delete-orphan')

    async def __admin_repr__(self, request: Request):
        return f'{self.sender1.name} {self.sender1.lastname} - {self.sender2.name} {self.sender2.lastname}'
