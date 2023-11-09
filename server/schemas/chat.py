from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from schemas.submission import Order, Request
from schemas.user import Client


class Message(BaseModel):
    id: int
    dialog_id: int
    sender_id: int
    message: str
    files: Optional[List[str]] = None
    is_read: bool
    is_modified: bool
    sent_at: datetime


class MessageEdit(BaseModel):
    message: Optional[str] = None
    is_read: Optional[bool] = None
    is_modified: Optional[bool] = None


class DialogIn(BaseModel):
    sender1_id: int
    sender2_id: int
    order_id: Optional[int] = None
    request_id: Optional[int] = None


class Dialog(BaseModel):
    id: int
    sender1_id: int
    sender1: Client
    sender2_id: int
    sender2: Client
    order_id: Optional[int] = None
    order: Optional[Order] = None
    request_id: Optional[int] = None
    request: Optional[Request] = None


class UnreadMessage(BaseModel):
    client_id: int
    dialog_id: int
    quantity: int