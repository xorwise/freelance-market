from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse

from utils.app_exceptions import AppExceptionCase, internal_exception_handler
from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles
from routers import user, service, submission, index, chat, websockets
from config.database import create_tables
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)
from utils.app_exceptions import app_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from admin import admin

create_tables()


app = FastAPI()


class SpaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            return FileResponse("media/index.html")
        return response


app.add_middleware(SpaMiddleware)

myadmin = FastAPI()


api = FastAPI()


@api.exception_handler(StarletteHTTPException)
async def custom_http_api_exception_handler(request, e):
    return await http_exception_handler(request, e)


@api.exception_handler(RequestValidationError)
async def custom_validation_api_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@api.exception_handler(AppExceptionCase)
async def custom_api_exception_handler(request, e):
    return await app_exception_handler(request, e)


@app.exception_handler(Exception)
async def internal_app_exception_handler(request, e):
    return await internal_exception_handler(request, e)


api.include_router(user.router)
api.include_router(service.router)
api.include_router(submission.router)
api.include_router(index.router)
api.include_router(chat.router)
app.include_router(websockets.router)

admin.mount_to(myadmin)
app.mount("/admin", myadmin)
app.mount("/api", api)
app.mount("/", StaticFiles(directory="media", html=True), name="media")


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
