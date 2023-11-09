from fastapi import WebSocket, WebSocketDisconnect

from cruds.chat import ChatCRUD
from models.user import Client
from schemas.chat import DialogIn, Message
from services.main import AppService
from utils.app_exceptions import AppException
from utils.service_result import ServiceResult
from utils.socket_managers import SocketChatManager


class ChatService(AppService):
    async def handle_chat(
        self, websocket: WebSocket, dialog_id: int, sender: Client, receiver_id: int
    ):
        if not ChatCRUD(self.db).is_user_in_dialog(
            dialog_id, sender.id
        ) or not ChatCRUD(self.db).is_user_in_dialog(dialog_id, receiver_id):
            raise AppException.ForbiddenException("Нет доступа!")
        manager = SocketChatManager()
        await manager.connect(websocket, sender.id, dialog_id)
        try:
            while True:
                data = await websocket.receive_json()
                final_data = dict()
                match data.get("type"):
                    case 1:
                        message = ChatCRUD(self.db).create_message(
                            data.get("message", ""),
                            data.get("files", []),
                            dialog_id,
                            sender.id,
                        )
                        final_data["type"] = 1
                        final_data["message"] = Message(**message.__dict__).model_dump(
                            mode="json"
                        )
                    case 2:
                        if data.get("message_id"):
                            message = ChatCRUD(self.db).get_message(
                                data["message_id"], sender.id
                            )
                            new_data = ChatCRUD(self.db).update_message(
                                message, data.get("message"), data.get("files", [])
                            )
                            final_data["type"] = 2
                            final_data["message"] = Message(
                                **new_data.__dict__
                            ).model_dump(mode="json")
                    case 3:
                        if data.get("messages"):
                            messages = ChatCRUD(self.db).make_read(
                                data["messages"], sender.id
                            )
                            final_data["type"] = 3
                            final_data["messages"] = list()
                            for message in messages:
                                final_data["messages"].append(
                                    Message(**message.__dict__).model_dump(mode="json")
                                )
                    case 4:
                        final_data["type"] = 4
                        final_data["user"] = sender.id
                        final_data["is_typing"] = True
                    case 5:
                        final_data["type"] = 5
                        final_data["user"] = sender.id
                        final_data["is_typing"] = False
                    case _:
                        raise AppException.NotFoundException(
                            "Некорректный тип запроса!"
                        )
                await websocket.send_json(final_data)
                await manager.send_direct_message(final_data, receiver_id, dialog_id)
        except WebSocketDisconnect:
            manager.disconnect(sender.id, dialog_id)


class DialogService(AppService):
    def create_dialog(self, data: DialogIn, user_id: int) -> ServiceResult:
        dialog = ChatCRUD(self.db).create_dialog(data, user_id)
        return ServiceResult(dialog)

    def get_dialogs(self, user_id: int):
        dialogs = ChatCRUD(self.db).get_dialogs_by_user_id(user_id)
        return ServiceResult(dialogs)

    def get_unread_messages(self, user_id: int):
        unread_messages = ChatCRUD(self.db).get_unread_messages_by_user_id(user_id)
        return ServiceResult(unread_messages)


class MessageService(AppService):
    def get_messages(self, dialog_id: int, user_id: int) -> ServiceResult:
        if not ChatCRUD(self.db).is_user_in_dialog(dialog_id, user_id):
            return ServiceResult(AppException.ForbiddenException("Нет доступа!"))
        messages = ChatCRUD(self.db).get_messages_by_dialog_id(dialog_id)
        return ServiceResult(messages)
