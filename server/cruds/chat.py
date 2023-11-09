import os
import base64
from typing import List
from models.relationship import UnreadMessage
from schemas.chat import DialogIn
from services.main import AppCRUD
from utils.app_exceptions import AppException
from models.chat import Message, Dialog
from sqlalchemy import or_


class ChatCRUD(AppCRUD):
    def is_user_in_dialog(self, dialog_id: int, user_id: int) -> bool:
        dialog = self.db.query(Dialog).filter(Dialog.id == dialog_id).first()
        if not dialog:
            raise AppException.NotFoundException("Диалог не найден!")
        if dialog.sender1_id == user_id or dialog.sender2_id == user_id:
            return True
        return False

    def create_message(self, text: str, files, dialog_id: int, user_id: int) -> Message:
        message = Message(dialog_id=dialog_id, sender_id=user_id, message=text)
        if files:
            new_files = list()

            for file in files:
                if type(file) == dict:
                    filename = file["name"]
                    file_data = base64.b64decode(file["data"])
                    if os.path.exists(f"media/files/{filename}"):
                        i = 1
                        paths_parts = [
                            filename[: filename.rindex(".")],
                            filename[filename.rindex(".") + 1 :],
                        ]
                        print(paths_parts)
                        while os.path.exists(
                            f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                        ):
                            i += 1
                        with open(
                            f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                        ) as f:
                            f.write(file_data)
                            new_files.append(f.name[6:])
                    else:
                        with open(f"media/files/{filename}", "wb") as f:
                            f.write(file_data)
                            new_files.append(f.name[6:])
            message.files = new_files

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def create_dialog(self, data: DialogIn, user_id: int) -> Dialog | Exception:
        if user_id != data.sender1_id and user_id != data.sender2_id:
            return AppException.ForbiddenException("Нет доступа!")
        dialog = Dialog(
            order_id=data.order_id,
            request_id=data.request_id,
            sender1_id=data.sender1_id,
            sender2_id=data.sender2_id,
        )
        self.db.add(dialog)
        self.db.commit()
        self.db.refresh(dialog)
        return dialog

    def get_dialogs_by_user_id(self, user_id: int) -> List[dict]:
        dialogs = (
            self.db.query(Dialog)
            .filter(or_(Dialog.sender1_id == user_id, Dialog.sender2_id == user_id))
            .all()
        )
        return list(dialogs)

    def get_messages_by_dialog_id(self, dialog_id: int) -> List[Message]:
        messages = (
            self.db.query(Message)
            .filter(Message.dialog_id == dialog_id)
            .order_by(Message.sent_at)
            .all()
        )
        return list(messages)

    def get_message(self, id: int, user_id: int) -> Message:
        message = self.db.query(Message).filter(Message.id == id).first()
        if not message:
            raise AppException.NotFoundException("Сообщение не найдено!")
        return message

    def make_read(self, messages: List[int], sender: int) -> List[Message]:
        new_messages = list()
        db_messages = self.db.query(Message).filter(Message.id.in_(messages)).all()
        if len(db_messages) > 0:
            unread_message = (
                self.db.query(UnreadMessage)
                .filter(
                    UnreadMessage.client_id == sender,
                    UnreadMessage.dialog_id == db_messages[0].dialog_id,
                )
                .first()
            )
            if not unread_message:
                unread_message = UnreadMessage(
                    client_id=sender, dialog_id=db_messages[0].dialog_id
                )
                self.db.add(unread_message)
                self.db.commit()
        for message in db_messages:
            if (
                sender == message.dialog.sender1_id
                and message.dialog.sender1_id != message.sender_id
            ) or (
                sender == message.dialog.sender2_id
                and message.dialog.sender2_id != message.sender_id
            ):
                message.is_read = True
                new_messages.append(message)
            else:
                raise AppException.ForbiddenException(
                    "Вы не можете просматривать это сообщение!"
                )
        unread_message.messages.clear()
        self.db.commit()
        for i in range(len(new_messages)):
            self.db.refresh(new_messages[i])
        return new_messages

    def update_message(
        self, message: Message, text: str, files: list | None
    ) -> Message:
        if text:
            message.message = text
        if files:
            new_files = list()
            for file in files:
                if type(file) == str:
                    new_files.append(file)
                elif type(file) == dict:
                    filename = file["name"]
                    file_data = base64.b64decode(file["data"])
                    if os.path.exists(f"media/files/{filename}"):
                        i = 1
                        paths_parts = [
                            filename[: filename.rindex(".")],
                            filename[filename.rindex(".") + 1 :],
                        ]
                        while os.path.exists(
                            f"media/files/{paths_parts[0]}({i}){paths_parts[1]}"
                        ):
                            i += 1
                        with open(
                            f"media/files/{paths_parts[0]}({i}){paths_parts[1]}", "wb"
                        ) as f:
                            f.write(file_data)
                        new_files.append(f"{paths_parts[0]}({i}){paths_parts[1]}")
                    else:
                        with open(f"media/files/{filename}", "wb") as f:
                            f.write(file_data)
                        new_files.append(filename)
            message.files = new_files
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_unread_messages_by_user_id(self, client_id: int) -> List[UnreadMessage]:
        unread_messages = (
            self.db.query(UnreadMessage)
            .filter(UnreadMessage.client_id == client_id)
            .all()
        )
        return list(unread_messages)
