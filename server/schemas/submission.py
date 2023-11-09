from pydantic import BaseModel, Extra
from datetime import datetime
from typing import List, Optional
from schemas.user import ClientInfo
from models import StatusEnum
from .service import RepairType, ServiceTypeInfo, Device


class OrderIn(BaseModel):
    client_message: str
    client_price: float
    master_username: str
    repairs_id: List[int]


class Order(BaseModel):
    id: int
    client_id: int
    master_username: str
    client_message: str
    status: StatusEnum
    repairs: List[RepairType]
    created_at: datetime
    client_price: float
    master_message: Optional[str] = None
    master_time: Optional[str] = None


class OrderEdit(BaseModel):
    status: Optional[StatusEnum] = None
    master_message: Optional[str] = None
    master_time: Optional[str] = None


class RequestIn(BaseModel):
    title: str
    description: str
    client_price: float
    service_type_id: Optional[int]


class Request(BaseModel):
    id: int
    client_id: int
    client: ClientInfo
    title: str
    description: str
    pictures: Optional[List[str]] = None
    client_price: float
    service_type_id: Optional[int]
    service_type: ServiceTypeInfo
    status: StatusEnum
    created_at: datetime
    expires_at: datetime
    number_of_offers: int
    views: int


class RequestEdit(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    client_price: Optional[float] = None
    service_type_id: Optional[int] = None
    status: Optional[StatusEnum] = None


class Offer(BaseModel):
    id: int
    master_username: str
    message: str
    price: float
    time: str
    request_id: Optional[int] = None
    is_accepted: Optional[bool] = None
    created_at: datetime


class OfferIn(BaseModel):
    message: str
    request_id: Optional[int] = None
    price: float
    time: str


class OfferEdit(BaseModel):
    message: Optional[str] = None
    price: Optional[float] = None
    time: Optional[str] = None


class FeedbackIn(BaseModel):
    master_username: str
    rating: int
    description: str


class Feedback(BaseModel):
    id: int
    client_id: int
    master_username: str
    rating: int
    description: str
    pictures: Optional[List[str]] = None
    created_at: datetime
    client_avatar: Optional[str] = None
    client_name: Optional[str] = None
    client_lastname: Optional[str] = None
    master_response: Optional[str] = None
    master_name: Optional[str] = None
    master_lastname: Optional[str] = None
    master_avatar: Optional[str] = None


class FeedbackEdit(BaseModel):
    master_response: str
