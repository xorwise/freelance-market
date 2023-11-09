from fastapi import Depends, HTTPException, APIRouter
from starlette.websockets import WebSocket, WebSocketState

from config.database import get_db
from services.chat import ChatService
from services.user import UserNotificationService
from utils.app_exceptions import AppExceptionCase
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/ws",
    tags=["websockets"],
    responses={404: {"description": "Not found"}},
)


@router.websocket("/notifications")
async def notifications(ws: WebSocket, token: str, db: get_db = Depends()):
    try:
        user = await get_current_user(db, token)
        await UserNotificationService(db).handle_notifications(ws, user)
    except AppExceptionCase as error:
        data = {"error": {"status_code": error.status_code, "detail": error.detail}}
        if ws.application_state == WebSocketState.CONNECTING:
            await ws.accept()
        await ws.send_json(data)
    except HTTPException as error:
        data = {"error": {"status_code": error.status_code, "detail": error.detail}}
        if ws.application_state == WebSocketState.CONNECTING:
            await ws.accept()
        await ws.send_json(data)
    return


@router.websocket("/chat/{dialog_id}")
async def chat(
    websocket: WebSocket,
    dialog_id: int,
    receiver_id: int,
    token: str,
    db: get_db = Depends(),
):
    try:
        user = await get_current_user(db, token)
        await ChatService(db).handle_chat(websocket, dialog_id, user, receiver_id)
    except AppExceptionCase as error:
        data = {"error": {"status_code": error.status_code, "detail": error.detail}}
        if websocket.application_state == WebSocketState.CONNECTING:
            await websocket.accept()
        await websocket.send_json(data)
    except HTTPException as error:
        data = {"error": {"status_code": error.status_code, "detail": error.detail}}
        if websocket.application_state == WebSocketState.CONNECTING:
            await websocket.accept()
        await websocket.send_json(data)
    return
