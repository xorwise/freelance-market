import uuid

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from services.user import ClientService, UserService, MasterService
from schemas.user import (
    Client,
    ClientRegister,
    Master,
    MasterRegister,
    ClientEdit,
    MasterEdit,
    UserEdit,
    MasterIn,
    MasterWithName,
    RefreshToken,
    UnreadMessageOut,
    PaymentOut,
    RecoverPasswordIn,
    ChangePasswordIn,
)
from utils.service_result import handle_result
from utils.dependencies import (
    get_current_user,
    client_checker,
    user_checker,
    is_user_active,
)
from config.database import get_db
from typing import Union, List

router = APIRouter(
    prefix="/user",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register/client")
async def create_client(client: ClientRegister, db: get_db = Depends()):
    result = await ClientService(db).create_client(client)
    return handle_result(result)


@router.post("/email/send")
async def send_email_code(user=Depends(get_current_user), db: get_db = Depends()):
    result = await ClientService(db).send_email_code(user)
    return handle_result(result)


@router.get("/email/verify/{code}")
async def verify_email(
    code: str, user=Depends(get_current_user), db: get_db = Depends()
):
    result = ClientService(db).verify_email(user, code)
    return handle_result(result)


@router.post("/phone/send")
async def send_phone_code(
    bg_tasks: BackgroundTasks, user=Depends(get_current_user), db: get_db = Depends()
):
    result = await ClientService(db).send_phone_code(user, bg_tasks)
    return handle_result(result)


@router.post("/phone/verify/{code}")
async def verify_phone(
    code: str, user=Depends(get_current_user), db: get_db = Depends()
):
    result = ClientService(db).verify_phone(user, code)
    return handle_result(result)


@router.post("/login/")
async def auth_user(
    user: OAuth2PasswordRequestForm = Depends(), db: get_db = Depends()
):
    result = UserService(db).auth_user(user)
    return handle_result(result)


@router.post("/refresh")
async def refresh_token(access_token: RefreshToken, db: get_db = Depends()):
    result = UserService(db).refresh(access_token)
    return handle_result(result)


@router.get(
    "/me", summary="Get details of currently logged in user", response_model=Client
)
async def get_me(user=Depends(get_current_user)):
    print(user)
    return user


@router.post("/register/master")
async def create_master(master: MasterRegister, db: get_db = Depends()):
    result = await MasterService(db).create_master(None, master)
    return handle_result(result)


@router.post("/add/master")
async def add_master(
    master: MasterIn, db: get_db = Depends(), user=Depends(get_current_user)
):
    result = await MasterService(db).create_master(user.id, master)
    return handle_result(result)


@router.get("/clients", response_model=List[Client])
async def get_clients(user=Depends(get_current_user), db: get_db = Depends()):
    result = ClientService(db).get_all_clients()
    return handle_result(result)


@router.get("/client/{id}", response_model=Client)
async def get_client(id: int, user=Depends(get_current_user), db: get_db = Depends()):
    result = ClientService(db).get_client(id)
    return handle_result(result)


@router.patch("/client", response_model=Client)
async def patch_client(
    data: ClientEdit = Depends(client_checker),
    file: UploadFile = None,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = ClientService(db).patch_client(
        user.id, data.model_dump(exclude_unset=True, exclude_defaults=True), file
    )
    return handle_result(result)


@router.get("/masters", response_model=List[Master])
async def get_masters(user=Depends(get_current_user), db: get_db = Depends()):
    result = MasterService(db).get_all_masters()
    return handle_result(result)


@router.get("/master", response_model=Master)
async def get_master(user=Depends(get_current_user), db: get_db = Depends()):
    result = MasterService(db).get_master(user)
    return handle_result(result)


@router.get("/master/{username}", response_model=MasterWithName)
async def get_master_by_username(username: str, db: get_db = Depends()):
    result = MasterService(db).get_master_by_username(username)
    return handle_result(result)


@router.patch("/master/{username}", response_model=Master)
async def patch_master(
    username: str,
    data: MasterEdit,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = MasterService(db).patch_master(
        username, data.model_dump(exclude_unset=True), user
    )
    return handle_result(result)


@router.patch("/update/{id}", response_model=Union[Master, Client])
async def patch_user(
    id: int,
    data: UserEdit = Depends(user_checker),
    file: UploadFile = None,
    pictures: List[Union[UploadFile, str]] = None,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = UserService(db).patch_user(
        id,
        data.model_dump(exclude_unset=True, exclude_defaults=True),
        file,
        pictures,
        user,
    )
    return handle_result(result)


uuid.uuid4()


@router.post("/balance/replenish/{amount}")
async def update_balance(
    amount: float,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = UserService(db).update_balance(user, amount)
    return handle_result(result)


@router.get("/balance/confirm/{payment_id}")
async def confirm_payment(payment_id: uuid.UUID, db: get_db = Depends()):
    result = UserService(db).confirm_payment(payment_id)
    return handle_result(result)


@router.get("/unread-messages", response_model=List[UnreadMessageOut])
async def get_unread_messages(user=Depends(get_current_user), db: get_db = Depends()):
    result = UserService(db).get_unread_messages(user)
    return handle_result(result)


@router.get("/balance/history", response_model=List[PaymentOut])
async def get_deposit_history(user=Depends(get_current_user), db: get_db = Depends()):
    result = UserService(db).get_deposit_history(user)
    return handle_result(result)


@router.post("/password/recover")
async def recover_password(data: RecoverPasswordIn, db: get_db = Depends()):
    result = await UserService(db).recover_password(data)
    return handle_result(result)


@router.post("/password/verify/{code}")
async def verify_password_recovery(code: str, user_id: int, db: get_db = Depends()):
    result = UserService(db).verify_password_recovery(code, user_id)
    return handle_result(result)


@router.post("/password/change")
async def change_password(data: ChangePasswordIn, db: get_db = Depends()):
    result = UserService(db).change_password(data)
    return handle_result(result)


@router.delete("/delete")
async def delete_account(user=Depends(get_current_user), db: get_db = Depends()):
    result = UserService(db).delete_account(user)
    return handle_result(result)
