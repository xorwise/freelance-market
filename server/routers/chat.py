from fastapi import APIRouter, Depends

from schemas.chat import Dialog, DialogIn, Message, UnreadMessage
from services.chat import DialogService, MessageService
from utils.dependencies import get_current_user, is_user_active
from utils.service_result import handle_result
from config.database import get_db
from typing import List

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/dialog", response_model=Dialog)
async def create_dialog(
    data: DialogIn,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = DialogService(db).create_dialog(data, user.id)
    return handle_result(result)


@router.get("/dialogs", response_model=List[Dialog])
async def get_dialogs(user=Depends(get_current_user), db: get_db = Depends()):
    result = DialogService(db).get_dialogs(user.id)
    return handle_result(result)


@router.get("/messages/{dialog_id}", response_model=List[Message])
async def get_messages(
    dialog_id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = MessageService(db).get_messages(dialog_id, user.id)
    return handle_result(result)


@router.get("/messages/unread", response_model=List[UnreadMessage])
async def get_unread_messages(user=Depends(get_current_user), db: get_db = Depends()):
    result = DialogService(db).get_unread_messages(user.id)
    return handle_result(result)
