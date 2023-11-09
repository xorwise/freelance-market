from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel

import models
from jinja2 import Environment, select_autoescape, PackageLoader

from config.settings import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    EMAIL_FROM,
)
from utils.app_exceptions import AppException


class EmailSchema(BaseModel):
    email: List[EmailStr]


env = Environment(
    loader=PackageLoader(package_name="main", package_path="templates/email"),
    autoescape=select_autoescape(["html", "xml"]),
)


class Email:
    conf = ConnectionConfig(
        MAIL_USERNAME=EMAIL_USERNAME,
        MAIL_PASSWORD=EMAIL_PASSWORD,
        MAIL_FROM=EMAIL_FROM,
        MAIL_PORT=EMAIL_PORT,
        MAIL_SERVER=EMAIL_HOST,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    def __init__(
        self,
        user: models.user.Client,
        email: List[str],
        code: str = None,
        entity_id: int = None,
        type: int = 1,
    ):
        self.name = user.name
        self.sender = "Codevo <admin@admin.com>"
        self.email = email
        self.code = code
        self.entity_id = entity_id
        self.type = type
        pass

    async def send_mailing(self, subject):
        template = env.get_template(f"mailing.html")

        html = template.render(
            entity_id=self.entity_id,
            type=self.type,
            first_name=self.name,
            subject=subject,
        )

        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        fm = FastMail(self.conf)
        await fm.send_message(message)

    async def send_mail(self, subject):
        template = env.get_template(f"verification.html")

        html = template.render(code=self.code, first_name=self.name, subject=subject)

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        # Send the email
        fm = FastMail(self.conf)
        await fm.send_message(message)

    async def send_password_recovery_code(self, subject: str) -> None:
        template = env.get_template(f"password_recovery.html")

        html = template.render(code=self.code, first_name=self.name, subject=subject)

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        # Send the email
        fm = FastMail(self.conf)
        await fm.send_message(message)

    async def send_verification_code(self):
        try:
            await self.send_mail("Your verification code (Valid for 10min)")
        except Exception as e:
            print(e.__context__)
            raise AppException.InternalServerException(
                "Не удалось отправить код подтверждения!"
            )
