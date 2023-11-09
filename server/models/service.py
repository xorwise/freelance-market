from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float, Boolean
)
from sqlalchemy.orm import relationship
from config.database import Base
from typing import List
from starlette.requests import Request
from sqlalchemy.orm import Mapped


class ServiceCategory(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    services: Mapped[List['ServiceType']] = relationship('ServiceType', back_populates='category')

    async def __admin_repr__(self, request: Request):
        return self.name


class ServiceType(Base):
    __tablename__ = 'service_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    category_id = Column("category", Integer, ForeignKey('category.id'), nullable=False)
    category: Mapped['ServiceCategory'] = relationship('ServiceCategory', back_populates='services')
    devices = relationship('Device', back_populates='service')

    async def __admin_repr__(self, request: Request):
        return self.name


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    picture = Column("picture", String(), nullable=True)
    service_id = Column("service_id", Integer, ForeignKey('service_type.id', ondelete='CASCADE'), nullable=False)
    service: Mapped['ServiceType'] = relationship('ServiceType', back_populates='devices')
    repair_types = relationship('RepairType', back_populates='device')

    async def __admin_repr__(self, request: Request):
        return self.name


class RepairType(Base):
    __tablename__ = 'repair_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    description = Column("description", Text)
    price = Column("price", Float)
    device_id = Column("device_id", Integer, ForeignKey('device.id', ondelete='CASCADE'), nullable=False)
    device: Mapped['Device'] = relationship('Device', back_populates='repair_types')
    is_custom = Column('is_custom', Boolean, default=False)
    created_by = Column(String, ForeignKey('master.username', ondelete='CASCADE'), nullable=True)
    master = relationship('Master')
    masters: Mapped[List['Master']] = relationship('Master', back_populates='repairs', secondary='master_repair')

    async def __admin_repr__(self, request: Request):
        return self.name
