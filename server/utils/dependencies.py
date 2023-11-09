from config.database import get_db
from fastapi import Depends, HTTPException, status, Form

from config.settings import ALGORITHM, JWT_SECRET_KEY
from models.user import Client
from jose import jwt
from datetime import datetime

from schemas.submission import RequestIn, RequestEdit, FeedbackIn
from schemas.user import TokenPayload, ClientEdit, UserEdit
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", scheme_name="JWT")


async def get_current_user(db=Depends(get_db), token=Depends(oauth2_scheme)) -> Client:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Авторизуйтесь заново!",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходимо авторизоваться",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Client = db.query(Client).filter(Client.id == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден!",
        )

    return user


async def is_user_active(user: Client = Depends(get_current_user)) -> None:
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите почту!",
        )
    if not user.is_phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Подтвердите номер телефона!"
        )


def client_checker(data: str = Form(...)):
    print(data)

    try:
        model = ClientEdit.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return model


def user_checker(data: str = Form(...)):
    try:
        model = UserEdit.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return model


def request_checker(data: str = Form(...)):
    try:
        model = RequestIn.model_validate_json(data)
    except ValidationError as e:
        print(e.errors)
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return model


def request_edit_checker(data: str = Form(...)):
    try:
        model = RequestEdit.model_validate_json(data)
    except ValidationError as e:
        print(e.errors)
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return model


def feedback_checker(data: str = Form(...)):
    try:
        model = FeedbackIn.model_validate_json(data)
    except ValidationError as e:
        print(e.errors)
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return model
