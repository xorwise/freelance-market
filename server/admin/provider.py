from fastapi import HTTPException, status
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from schemas.user import RefreshToken
from utils.app_exceptions import AppExceptionCase
from utils.auth import refresh_token
from utils.dependencies import get_current_user
from cruds.user import UserCRUD
from fastapi.security import OAuth2PasswordRequestForm
from config.database import engine
from sqlalchemy.orm import sessionmaker


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MyAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        db = next(get_db())
        tokens = UserCRUD(db).get_jwt_tokens(
            OAuth2PasswordRequestForm(username=username, password=password)
        )
        if isinstance(tokens, AppExceptionCase):
            raise LoginFailed(tokens.detail)
        user = await get_current_user(db, tokens["access_token"])
        if user.is_superuser:
            request.session.update({"userdata": tokens})
            return response
        else:
            raise LoginFailed("Пользователь не админ!")

    async def is_authenticated(self, request) -> bool:
        tokens = request.session.get("userdata")
        db = next(get_db())
        user = None
        if tokens is None:
            return False
        try:
            user = await get_current_user(db, tokens["access_token"])
        except HTTPException as error:
            if error.status_code == status.HTTP_401_UNAUTHORIZED:
                token = RefreshToken(token=tokens["refresh_token"])
                new_token = refresh_token(token)
                tokens["access_token"] = new_token["access_token"]
                request.session.update({"userdata": tokens})
                user = await get_current_user(db, tokens["access_token"])
        if user:
            request.state.user = {
                "name": f"{user.name} {user.lastname}",
                "avatar": user.avatar,
            }
            return True
        return False

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        photo_url = None
        if user["avatar"] is not None:
            photo_url = f'"{request.base_url}{user["avatar"]}"'
        return AdminUser(username=user["name"], photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
