from pydantic import BaseModel
from datetime import time, datetime
from typing import List, Optional
from models.user import GenderEnum, BusinessEnum


class ClientRegister(BaseModel):
    name: str
    lastname: str
    email: str
    phone: str
    password1: str
    password2: str


class Master(BaseModel):
    username: str
    address: str
    is_active: bool
    mailing: bool
    gender: GenderEnum
    business_model: BusinessEnum
    organization_name: str
    specialty: str
    main_business: str
    status: str
    bio: str
    availability_from: Optional[time] = None
    availability_to: Optional[time] = None
    webmoney: str
    qiwi: str
    credit_card: str
    rating: float
    number_of_feedbacks: int
    balance: float
    pictures: Optional[List[str]]
    number_of_submissions: int


class MasterWithName(BaseModel):
    username: str
    name: str
    avatar: str
    lastname: str
    address: str
    gender: GenderEnum
    business_model: BusinessEnum
    organization_name: str
    specialty: str
    main_business: str
    status: str
    bio: str
    availability_from: Optional[time] = None
    availability_to: Optional[time] = None
    rating: float
    number_of_feedbacks: int
    pictures: Optional[List[str]] = None
    number_of_submissions: int


class Client(BaseModel):
    id: int
    name: str
    lastname: str
    email: str
    phone: str
    avatar: str
    is_superuser: bool
    is_email_verified: bool
    is_phone_verified: bool
    number_of_submissions: int
    master: Optional[List[Master]] = None


class ClientEdit(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    old_password: Optional[str] = None
    new_password1: Optional[str] = None
    new_password2: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class MasterEdit(BaseModel):
    username: Optional[str] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    gender: Optional[GenderEnum] = None
    business_model: Optional[BusinessEnum] = None
    organization_name: Optional[str] = None
    specialty: Optional[str] = None
    main_business: Optional[str] = None
    status: Optional[str] = None
    bio: Optional[str] = None
    availability_from: Optional[time] = None
    availability_to: Optional[time] = None
    webmoney: Optional[str] = None
    qiwi: Optional[str] = None
    credit_card: Optional[str] = None


class MasterRegister(BaseModel):
    username: str
    name: str
    lastname: str
    email: str
    phone: str
    password1: str
    password2: str
    address: str
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    devices: List[int]


class MasterIn(BaseModel):
    username: str
    address: str
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    devices: List[int]


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserEdit(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    old_password: Optional[str] = None
    new_password1: Optional[str] = None
    new_password2: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    is_active: Optional[bool] = None
    mailing: Optional[bool] = None
    gender: Optional[GenderEnum] = None
    business_model: Optional[BusinessEnum] = None
    organization_name: Optional[str] = None
    specialty: Optional[str] = None
    main_business: Optional[str] = None
    status: Optional[str] = None
    bio: Optional[str] = None
    availability_from: Optional[time] = None
    availability_to: Optional[time] = None
    webmoney: Optional[str] = None
    qiwi: Optional[str] = None
    credit_card: Optional[str] = None


class RefreshToken(BaseModel):
    token: str


class EmailToken(BaseModel):
    token: str


class ClientInfo(BaseModel):
    id: int
    phone: str
    name: str
    lastname: str
    avatar: str
    number_of_submissions: int


class UnreadMessageOut(BaseModel):
    client_id: int
    dialog_id: int
    messages: List[int]


class PaymentOut(BaseModel):
    amount: float
    status: str
    created_at: datetime
    description: str


class RecoverPasswordIn(BaseModel):
    phone: str


class ChangePasswordIn(BaseModel):
    user_id: int
    code: str
    password: str
