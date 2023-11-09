import uuid
from typing import List

from cruds.user import UserCRUD
from schemas.user import (
    ClientRegister,
    MasterRegister,
    RefreshToken,
    MasterIn,
    RecoverPasswordIn,
    ChangePasswordIn,
)
from utils.app_exceptions import AppException
import models
from services.main import AppService
from utils.auth import refresh_token
from utils.service_result import ServiceResult
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import (
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
    HTTPException,
)

from utils.socket_managers import SocketManager

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/user/login", scheme_name="JWT")


class UserService(AppService):
    def auth_user(self, user: OAuth2PasswordRequestForm) -> ServiceResult:
        tokens = UserCRUD(self.db).get_jwt_tokens(user)
        if not tokens:
            return ServiceResult(
                AppException.NotFoundException(detail="Пользователь не был найден!")
            )
        return ServiceResult(tokens)

    @classmethod
    def refresh(cls, token: RefreshToken) -> ServiceResult:
        new_access_token = refresh_token(token)
        return ServiceResult(new_access_token)

    def patch_user(
        self,
        id: int,
        data: dict,
        file: UploadFile,
        pictures: List[UploadFile],
        user: models.user.Client,
    ) -> ServiceResult:
        if id != user.id:
            return ServiceResult(AppException.ForbiddenException(detail="Нет доступа!"))
        if file:
            if file.size > 10 * 1024 * 1024:
                return ServiceResult(
                    AppException.TooLargeException(
                        "Изображение превышает размер в 10МБ"
                    )
                )
        try:
            master = UserCRUD(self.db).get_master_by_client(user)
        except HTTPException:
            new_user = UserCRUD(self.db).update_client_by_id(id, data, file)
            return ServiceResult(new_user)
        UserCRUD(self.db).update_master_by_username(master.username, data, pictures)
        new_user = UserCRUD(self.db).update_client_by_id(id, data, file)
        return ServiceResult(new_user)

    def update_balance(self, user: models.user.Client, amount: float) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        response = UserCRUD(self.db).replenish_balance(master, amount)
        return ServiceResult(response)

    def confirm_payment(self, payment_id: uuid.UUID):
        response = UserCRUD(self.db).confirm_payment(payment_id)
        return ServiceResult(response)

    def get_unread_messages(self, user: models.user.Client) -> ServiceResult:
        unread_messages = UserCRUD(self.db).get_unread_messages(user.id)
        return ServiceResult(unread_messages)

    def get_deposit_history(self, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        history = UserCRUD(self.db).get_deposit_history_by_master(master)
        return ServiceResult(history)

    async def recover_password(self, data: RecoverPasswordIn) -> ServiceResult:
        response = await UserCRUD(self.db).recover_password(data)
        return ServiceResult(response)

    def verify_password_recovery(self, code: str, user_id: int) -> ServiceResult:
        response = UserCRUD(self.db).verify_password_recovery(code, user_id)
        return ServiceResult(response)

    def change_password(self, data: ChangePasswordIn) -> ServiceResult:
        response = UserCRUD(self.db).change_password(data)
        return ServiceResult(response)

    def delete_account(self, user: models.user.Client) -> ServiceResult:
        response = UserCRUD(self.db).delete_account(user)
        return ServiceResult(response)


class ClientService(UserService):
    async def create_client(self, client: ClientRegister) -> ServiceResult:
        dbclient = await UserCRUD(self.db).create_client(client)
        if not dbclient:
            return ServiceResult(
                AppException.RegistrationException(detail="Ошибка регистрации!")
            )
        return ServiceResult(dbclient)

    async def send_email_code(self, user: models.user.Client) -> ServiceResult:
        response = await UserCRUD(self.db).send_email_verification_code(user)
        if not response:
            return ServiceResult(
                AppException.NotFoundException("Ошибка подтверждения почты!")
            )
        return ServiceResult(response)

    def verify_email(self, user: models.user.Client, code: str) -> ServiceResult:
        response = UserCRUD(self.db).verify_email(user, code)
        return ServiceResult(response)

    async def send_phone_code(
        self, user: models.user.Client, bg_tasks: BackgroundTasks
    ) -> ServiceResult:
        response = await UserCRUD(self.db).send_phone_verification_code(user, bg_tasks)
        return ServiceResult(response)

    def verify_phone(self, user: models.user.Client, code: str) -> ServiceResult:
        response = UserCRUD(self.db).verify_phone(user, code)
        return ServiceResult(response)

    def get_all_clients(self) -> ServiceResult:
        clients = UserCRUD(self.db).get_all_clients()
        if not clients:
            return ServiceResult(AppException.NotFoundException(detail="Not found"))
        return ServiceResult(clients)

    def get_client(self, id: int) -> ServiceResult:
        client = UserCRUD(self.db).get_client_by_id(id)
        if not client:
            return ServiceResult(
                AppException.NotFoundException(detail="Пользователь не найден!")
            )
        return ServiceResult(client)

    def patch_client(self, id: int, data: dict, file: UploadFile) -> ServiceResult:
        new_client = UserCRUD(self.db).update_client_by_id(id, data, file)
        if not new_client:
            return ServiceResult(
                AppException.NotFoundException(detail="Пользователь не найден!")
            )
        return ServiceResult(new_client)


class MasterService(UserService):
    async def create_master(
        self, id: int | None, master: MasterIn | MasterRegister
    ) -> ServiceResult:
        dbmaster = await UserCRUD(self.db).create_master(id, master)
        if not dbmaster:
            return ServiceResult(
                AppException.RegistrationException(detail="Ошибка регистрации!")
            )
        return ServiceResult(dbmaster)

    def get_all_masters(self) -> ServiceResult:
        masters = UserCRUD(self.db).get_all_masters()
        if not masters:
            return ServiceResult(AppException.NotFoundException(detail="Not found"))
        return ServiceResult(masters)

    def get_master(self, user: models.user.Client) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        if not master:
            return ServiceResult(
                AppException.NotFoundException(detail="Пользователь не найден!")
            )
        return ServiceResult(master)

    def get_master_by_username(self, username: str) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_username(username)
        return ServiceResult(master)

    def patch_master(
        self, username: str, data: dict, user: models.user.Client
    ) -> ServiceResult:
        if username != user.master[0].username:
            return ServiceResult(
                AppException.ForbiddenException(detail="Доступ запрещен!")
            )
        new_master = UserCRUD(self.db).update_master_by_username(username, data)
        if not new_master:
            return ServiceResult(
                AppException.NotFoundException(detail="Пользователь не найден!")
            )
        return ServiceResult(new_master)


class UserNotificationService(AppService):
    async def handle_notifications(self, ws: WebSocket, user: models.user.Client):
        manager = SocketManager()
        await manager.connect(ws, user.id)
        try:
            while True:
                data = await ws.receive_json()
                new_data, receiver = UserCRUD(self.db).notification_handler(data, user)
                if new_data and receiver:
                    if receiver in manager.active_connections:
                        await manager.send_direct_message(new_data, receiver)
        except WebSocketDisconnect:
            manager.disconnect(user.id)
