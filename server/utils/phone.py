from typing import Match
import requests
import re
from utils.app_exceptions import AppException


class TSMSResponse:
    id: str = "0"
    status: int = 0
    status_code: int = -1
    balance: float = 0


class SMSTransport:
    _URL = "https://sms.ru/sms/send"

    def __init__(self, api_id):
        self._api_id = api_id

    def send(self, to: str, msg: str) -> None:
        if not self.validate_phone(to):
            raise AppException.ValidationException("Некорректный номер телефона!")

        response = requests.get(
            self._URL,
            params={
                "api_id": self._api_id,
                "to": to,
                "msg": msg,
                "json": 1,
                "from": "xorwise.dev",
            },
        ).json()

        print(response)
        if response["status"] == "OK":
            phone = response["sms"][to]

            if phone["status"] == "OK":
                return
        raise AppException.InternalServerException(
            "Не удалось отправить код подтверждения!"
        )

    @classmethod
    def validate_phone(cls, phone: str) -> Match[str] | None:
        return re.match(r"^7[0-9]{10}$", phone)
