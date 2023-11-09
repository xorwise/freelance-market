import datetime
from random import randint
from typing import List
from fastapi import UploadFile
import os
from models.relationship import UnreadMessage
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, BackgroundTasks
from utils.phone import SMSTransport
import models
from cruds.service import ServiceCRUD
from models import Master, MasterRepair, NotificationTypeEnum
from models.user import Client, RefreshToken, Notification, Payment as DBPayment
from schemas.user import (
    ClientRegister,
    MasterRegister,
    MasterIn,
    UnreadMessageOut,
    RecoverPasswordIn,
    ChangePasswordIn,
)
from services.main import AppCRUD
from utils.app_exceptions import AppException
from utils.auth import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from utils.email import Email
from utils.socket_managers import SocketManager, SocketChatManager
from utils.validators import email_validator, password_validator, phone_validator
from config.settings import SMS_API_ID, REFRESH_TOKEN_EXPIRE_MINUTES
from models.index import Settings

from yookassa import Payment
import uuid


class UserCRUD(AppCRUD):
    async def create_client(self, client: ClientRegister) -> dict | Exception:
        is_valid_email = email_validator(client.email)
        if not is_valid_email:
            return AppException.ValidationException(detail="Некорректный e-mail!")
        if (
            self.db.query(Client).filter(Client.email == client.email).first()
            is not None
        ):
            return AppException.AlreadyExistsException(
                detail="Пользователь с такой почтой уже существует!"
            )

        validated_phone = phone_validator(client.phone)
        if not validated_phone:
            return AppException.ValidationException("Некорректный номер телефона!")
        if (
            self.db.query(Client).filter(Client.phone == str(client.phone)).first()
            is not None
        ):
            return AppException.AlreadyExistsException(
                detail="Пользователь с таким номером телефона уже существует!"
            )

        is_valid_password = password_validator(client.password1, client.password2)
        if not is_valid_password:
            return AppException.ValidationException(detail="Некорректный пароль!")

        user = Client(
            name=client.name,
            lastname=client.lastname,
            email=client.email,
            phone=validated_phone,
            password=get_hashed_password(client.password1),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self.db.commit()
        return {"result": "Success!", "user_id": user.id}

    async def send_email_verification_code(self, user: Client) -> dict | Exception:
        if user.is_email_verified:
            return AppException.AlreadyExistsException("Почта уже подтверждена!")
        code = "".join(["{}".format(randint(0, 9)) for num in range(0, 6)])
        user.email_verification_code = code
        await Email(user, code=code, email=[user.email]).send_verification_code()
        self.db.commit()
        return {"result": "Success!"}

    def verify_email(self, user: Client, code: str) -> dict | Exception:
        if user.is_email_verified:
            return {"result": "Success!"}
        if user.email_verification_code != code:
            return AppException.ValidationException("Неправильный код!")
        user.is_email_verified = True
        user.email_verification_code = None
        self.db.commit()
        return {"result": "Success!"}

    async def send_phone_verification_code(
        self, user: Client, bg_tasks: BackgroundTasks
    ) -> dict | Exception:
        if user.is_phone_verified:
            return AppException.AlreadyExistsException("Телефон уже подтвержден!")
        code = "".join(["{}".format(randint(0, 9)) for num in range(0, 6)])
        sms = SMSTransport(api_id=SMS_API_ID)
        print(sms)
        user.phone_verification_code = code
        print(code)
        sms.send(user.phone[1:], f"Ваш код подтверждения: {code}")
        self.db.commit()
        return {"result": "Success!"}

    def verify_phone(self, user: Client, code: str) -> dict | Exception:
        if user.is_phone_verified:
            return {"result": "Success!"}
        if user.phone_verification_code != code:
            return AppException.ValidationException("Неправильный код!")
        user.is_phone_verified = True
        user.phone_verification_code = None
        self.db.commit()
        return {"result": "Success!"}

    def get_jwt_tokens(self, data: OAuth2PasswordRequestForm) -> dict | Exception:
        parsed_phone = phone_validator(data.username)
        if not parsed_phone:
            return AppException.ValidationException("Некорректный номер телефона!")
        user = self.db.query(Client).filter(Client.phone == parsed_phone).first()
        if user is None:
            return AppException.NotFoundException(detail="Пользователь не был найден!")
        hashed_password = user.password
        if not verify_password(data.password, hashed_password):
            return AppException.ValidationException(detail="Неправильный пароль!")

        refresh_token_check = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id
        )
        if refresh_token_check.first():
            if (
                refresh_token_check.first().date_created
                + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
                < datetime.datetime.now()
            ):
                return AppException.UnauthorizedException(detail="Refresh token истёк!")
            refresh_token_check.delete()
            self.db.commit()

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        refresh_token_dict = {
            "user_id": user.id,
            "refresh_token": refresh_token,
        }
        refresh_token_db_data = RefreshToken(**refresh_token_dict)
        self.db.add(refresh_token_db_data)
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def create_master(
        self, id: int, master: MasterRegister | MasterIn
    ) -> dict | Exception:
        if (
            self.db.query(Master)
            .filter(Master.username == str(master.username))
            .first()
            is not None
        ):
            return AppException.AlreadyExistsException(
                detail="Пользователь с таким именем пользователя уже существует!"
            )
        if id is None:
            client = await self.create_client(ClientRegister(**master.model_dump()))
            if isinstance(client, dict):
                id = client["user_id"]
            else:
                return client
        user = Master(
            client_id=id,
            username=master.username,
            address=master.address,
            address_latitude=master.address_latitude,
            address_longitude=master.address_longitude,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        repair_types = list()
        for device in master.devices:
            repair_types += ServiceCRUD(self.db).get_repair_types_by_device(device)
        for repair in repair_types:
            master_repair = (
                self.db.query(MasterRepair)
                .filter(
                    MasterRepair.master_id == user.username,
                    MasterRepair.repair_id == repair.id,
                )
                .first()
            )
            if not master_repair:
                new_repair = MasterRepair(
                    master_id=user.username,
                    repair_id=repair.id,
                    address_latitude=master.address_latitude,
                    address_longitude=master.address_longitude,
                )
                self.db.add(new_repair)
        self.db.commit()
        return {"result": "Success!"}

    def get_all_clients(self) -> List[Client]:
        clients = self.db.query(Client).all()
        return list(clients) if len(clients) else []

    def get_client_by_id(self, id: int) -> Client:
        client = self.db.query(Client).filter(Client.id == id).first()
        return client

    def update_client_by_id(
        self, id: int, data: dict, file: UploadFile
    ) -> Client | Exception:
        client = self.db.query(Client).filter(Client.id == id).first()
        if not client:
            return AppException.NotFoundException(detail="Пользователь не найден!")
        if "phone" in data and data["phone"] != client.phone:
            is_client = (
                self.db.query(Client).filter(Client.phone == data["phone"]).first()
            )
            if is_client and is_client.id != id:
                return AppException.AlreadyExistsException(
                    "Такой номер телефона уже используется!"
                )
            client.is_phone_verified = False
        if "email" in data and data["email"] != client.email:
            is_client = (
                self.db.query(Client).filter(Client.email == data["email"]).first()
            )
            if is_client and is_client.id != id:
                return AppException.AlreadyExistsException(
                    "Такая почта уже используется!"
                )
            is_valid_email = email_validator(data["email"])
            if not is_valid_email:
                return AppException.ValidationException(detail="Некорректный e-mail!")
            client.is_email_verified = False

        if "new_password1" in data:
            hashed_password = client.password
            if not verify_password(data["old_password"], hashed_password):
                return AppException.ValidationException(detail="Неправильный пароль!")

            is_valid_password = password_validator(
                data["new_password1"], data["new_password2"]
            )
            if not is_valid_password:
                return AppException.ValidationException(detail="Некорректный пароль!")
        if file:
            if os.path.exists(f"media/files/{file.filename}"):
                i = 1
                paths_parts = [
                    file.filename[: file.filename.rindex(".")],
                    file.filename[file.filename.rindex(".") + 1 :],
                ]
                while os.path.exists(
                    f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                ):
                    i += 1
                with open(
                    f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                ) as f:
                    content = file.file.read()
                    f.write(content)
                    file_link = f.name[6:]
            else:
                with open(f"media/files/{file.filename}", "wb") as f:
                    content = file.file.read()
                    f.write(content)
                    file_link = f.name[6:]
            data["avatar"] = f"{file_link}"
        for attr in data:
            has_attr = hasattr(client, attr)
            if has_attr:
                setattr(client, attr, data[attr])

        self.db.commit()
        self.db.refresh(client)
        return client

    def get_all_masters(self) -> List[Master]:
        masters = self.db.query(Master).all()
        return list(masters) if len(masters) else []

    def get_master_by_username(self, username: str) -> dict | Exception:
        master = self.db.query(Master).filter(Master.username == username).first()
        if not master:
            return AppException.NotFoundException(detail="Пользователь не найден!")
        new_master = dict(master.__dict__)
        new_master.update(
            {
                "name": master.client.name,
                "lastname": master.client.lastname,
                "avatar": master.client.avatar,
            }
        )
        return new_master

    def update_master_by_username(
        self, username: str, data: dict, pictures: List[UploadFile]
    ) -> dict | Exception:
        master = self.db.query(Master).filter(Master.username == username).first()
        if not master:
            return AppException.NotFoundException(detail="Пользователь не найден!")

        for attr in data:
            has_attr = hasattr(master, attr)
            if has_attr:
                setattr(master, attr, data[attr])
        if data.get("address_latitude"):
            master_repairs = (
                self.db.query(MasterRepair)
                .filter(MasterRepair.master_id == username)
                .all()
            )
            for master_repair in master_repairs:
                master_repair.address_latitude = data.get("address_latitude")
                master_repair.address_longitude = data.get("address_longitude")
        if pictures:
            new_pictures = list()
            for file in pictures:
                if type(file) == str:
                    new_pictures.append(file)
                    continue
                if os.path.exists(f"media/files/{file.filename}"):
                    i = 1
                    paths_parts = [
                        file.filename[: file.filename.rindex(".")],
                        file.filename[file.filename.rindex(".") + 1 :],
                    ]
                    while os.path.exists(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                    ):
                        i += 1
                    with open(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                    ) as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                else:
                    with open(f"media/files/{file.filename}", "wb") as f:
                        content = file.file.read()
                        f.write(content)
                        link = f.name[6:]
                new_pictures.append(link)
            master.pictures = new_pictures
        self.db.commit()
        self.db.refresh(master)
        return master

    def get_master_by_client(self, user: Client) -> Master:
        master = self.db.query(Master).filter(Master.client_id == user.id).first()
        if not master:
            raise HTTPException(status_code=404, detail="Не удалось найти мастера!")
        return master

    def notification_handler(self, data: dict, user: models.user.Client):
        new_data = None
        receiver = None
        try:
            match data.get("type"):
                case 1:
                    manager = SocketManager()
                    new_data = {
                        "type": 1,
                        "online_users": list(manager.active_connections.keys()),
                    }
                    receiver = user.id
                case 2:
                    manager = SocketChatManager()
                    if (
                        not (data["receiver_id"], data["dialog_id"])
                        in manager.active_connections
                    ):
                        receiver = data["receiver_id"]
                        unread_message = (
                            self.db.query(UnreadMessage)
                            .filter(
                                UnreadMessage.client_id == data["receiver_id"],
                                UnreadMessage.dialog_id == data["dialog_id"],
                            )
                            .first()
                        )
                        if not unread_message:
                            unread_message = UnreadMessage(
                                client_id=data["receiver_id"],
                                dialog_id=data["dialog_id"],
                            )
                            self.db.add(unread_message)
                            self.db.commit()
                            self.db.refresh(unread_message)
                            new_unread_messages = unread_message.messages
                            new_unread_messages.append(data["message_id"])
                            new_unread_messages.messages = new_unread_messages
                        else:
                            if data["message_id"] not in unread_message.messages:
                                new_unread_messages = unread_message.messages
                                new_unread_messages.append(data["message_id"])
                                unread_message.messages = new_unread_messages
                                self.db.commit()
                                self.db.refresh(unread_message)
                        messages = (
                            self.db.query(UnreadMessage)
                            .filter(UnreadMessage.client_id == data["receiver_id"])
                            .all()
                        )
                        unread_messages = list()
                        for message in messages:
                            unread_messages.append(
                                UnreadMessageOut(**message.__dict__).model_dump(
                                    mode="json"
                                )
                            )
                        new_data = {
                            "type": 2,
                            "sender": user.id,
                            "unread_messages": unread_messages,
                        }
                case 3:
                    new_data = {"type": 3, "sender": user.id, "order": data["order_id"]}
                    receiver = data["receiver_id"]
                    new_user = (
                        self.db.query(Client).filter(Client.id == receiver).first()
                    )
                    if not new_user:
                        raise AppException.NotFoundException("Получатель не найден!")
                    notification = Notification(
                        type=NotificationTypeEnum.accepted_order,
                        receiver_id=receiver,
                        entity=data["order_id"],
                    )
                    self.db.add(notification)
                    self.db.commit()
                case 4:
                    new_data = {
                        "type": 4,
                        "sender": user.id,
                        "request": data["request_id"],
                    }
                    receiver = data["receiver_id"]
                    new_user = (
                        self.db.query(Client).filter(Client.id == receiver).first()
                    )
                    if not new_user:
                        raise AppException.NotFoundException("Получатель не найден!")
                    notification = Notification(
                        type=NotificationTypeEnum.new_offer,
                        receiver_id=receiver,
                        entity=data["request_id"],
                    )
                    self.db.add(notification)
                    self.db.commit()
                case 5:
                    new_data = {"type": 5, "sender": user.id, "offer": data["offer_id"]}
                    receiver = data["receiver_id"]
                    new_user = (
                        self.db.query(Client).filter(Client.id == receiver).first()
                    )
                    if not new_user:
                        raise AppException.NotFoundException("Получатель не найден!")
                    notification = Notification(
                        type=NotificationTypeEnum.accepted_offer,
                        receiver_id=receiver,
                        entity=data["offer_id"],
                    )
                    self.db.add(notification)
                    self.db.commit()
                case _:
                    raise AppException.ValidationException("Некорректный тип!")
        except KeyError:
            raise AppException.ValidationException("Некорректные данные!")
        return new_data, receiver

    def write_commission_off(self, master: Master, price: float) -> Master:
        settings = self.db.query(Settings).filter(Settings.id == 1).first()
        amount = price * settings.commission
        if master.balance < amount:
            raise AppException.PaymentRequiredException(
                "Недостаточно средств, пополните счет!"
            )
        master.balance -= amount
        self.db.commit()
        return master

    def charge_commission(self, username: str, price: float) -> None:
        master = self.db.query(Master).filter(Master.username == username).first()
        settings = self.db.query(Settings).filter(Settings.id == 1).first()
        amount = price * settings.commission
        master.balance += amount
        self.db.commit()

    def replenish_balance(self, master: Master, amount: float) -> dict | Exception:
        if amount <= 0:
            return AppException.ValidationException("Некорректная сумма платежа!")
        return_id = uuid.uuid4()
        new_payment = DBPayment(
            master_username=master.username, id=return_id, amount=amount
        )
        payment = Payment.create(
            {
                "amount": {"value": amount, "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"http://localhost:3000/master/wallet/{return_id}",
                },
                "capture": True,
                "description": f"Пополение баланса мастера #{master.client.id}",
            },
            uuid.uuid4(),
        )
        print(payment)
        new_payment.payment_id = payment.id
        new_payment.status = payment.status
        new_payment.paid = payment.paid
        new_payment.description = payment.description
        self.db.add(new_payment)
        self.db.commit()
        data = {
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
        }
        return data

    def confirm_payment(self, return_id: uuid.UUID) -> dict | Exception:
        payment = self.db.query(DBPayment).filter(DBPayment.id == return_id).first()
        if not payment:
            return AppException.NotFoundException("Платеж не найден!")
        if payment.status == "succeeded":
            return AppException.AlreadyExistsException("Платеж уже подтвержден!")
        kassa_payment = Payment.find_one(str(payment.payment_id))
        payment.status = kassa_payment.status
        payment.paid = kassa_payment.paid
        if kassa_payment.status == "succeeded":
            master = (
                self.db.query(Master)
                .filter(Master.username == payment.master_username)
                .first()
            )
            master.balance += payment.amount
            payment.is_confirmed = True
        self.db.commit()
        return {"result": "Success"}

    def get_unread_messages(self, user_id: int) -> List[UnreadMessage]:
        unread_messages = (
            self.db.query(UnreadMessage)
            .filter(UnreadMessage.client_id == user_id)
            .all()
        )
        return list(unread_messages)

    async def send_mailing(
        self, master_username: str, order_id: int = None, request_id: int = None
    ) -> None:
        if master_username == "__all__":
            masters = (
                self.db.query(Master)
                .filter(Master.mailing == True, Master.is_active == True)
                .all()
            )
            for master in masters:
                if order_id:
                    email = Email(
                        master.client,
                        email=[master.client.email],
                        entity_id=order_id,
                        type=2,
                    )
                    await email.send_mailing("tsarbirzzha.ru | Уведомление!")
                elif request_id:
                    email = Email(
                        master.client,
                        email=[master.client.email],
                        entity_id=request_id,
                        type=3,
                    )
                    await email.send_mailing("tsarbirzzha.ru | Уведомление!")
            return

        master = (
            self.db.query(Master).filter(Master.username == master_username).first()
        )
        if not master.mailing:
            return
        if order_id:
            email = Email(
                master.client, email=[master.client.email], entity_id=order_id, type=2
            )
            await email.send_mailing("tsarbirzzha.ru | Уведомление!")
        elif request_id:
            email = Email(
                master.client, email=[master.client.email], entity_id=request_id, type=3
            )
            await email.send_mailing("tsarbirzzha.ru | Уведомление!")
        return

    def get_deposit_history_by_master(self, master: Master) -> List[DBPayment]:
        payments = (
            self.db.query(DBPayment)
            .filter(
                DBPayment.master_username == master.username,
                DBPayment.status != None,
            )
            .all()
        )
        return payments

    async def recover_password(self, data: RecoverPasswordIn) -> dict | Exception:
        user = self.db.query(Client).filter(Client.phone == data.phone).first()
        if not user:
            return AppException.NotFoundException("Пользователь не найден!")
        code = "".join(["{}".format(randint(0, 9)) for num in range(0, 6)])

        await Email(user, [user.email], code).send_password_recovery_code(
            "Восстановление пароля TsarBirzzha"
        )
        user.password_recovery_code = code
        self.db.commit()
        return {"result": "Success!", "user_id": user.id}

    def verify_password_recovery(self, code: str, user_id: int) -> dict | Exception:
        user = self.db.query(Client).filter(Client.id == user_id).first()
        if not user:
            return AppException.NotFoundException("Пользователь не найден!")
        if user.password_recovery_code != code:
            return AppException.ValidationException("Неправильный код подтверждения!")
        return {"result": "Success!"}

    def change_password(self, data: ChangePasswordIn) -> dict | Exception:
        user = self.db.query(Client).filter(Client.id == data.user_id).first()
        if not user:
            return AppException.NotFoundException("Пользователь не найден!")
        if user.password_recovery_code != data.code:
            return AppException.ValidationException("Неправильный код подтверждения!")
        if not password_validator(data.password):
            return AppException.ValidationException(
                "Пароль не удовлетворяет требованиям!"
            )
        user.password = get_hashed_password(data.password)
        user.password_recovery_code = None
        self.db.commit()
        return {"result": "Success!"}

    def delete_account(self, user: Client) -> dict:
        self.db.delete(user)
        self.db.commit()
        return {"result": "Success!"}
