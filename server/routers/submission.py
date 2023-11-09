from fastapi import APIRouter, Depends, UploadFile
from starlette.background import BackgroundTasks

from models import StatusEnum
from services.submission import (
    OrderService,
    RequestService,
    OfferService,
    FeedbackService,
)
from schemas.submission import (
    Order,
    OrderIn,
    OrderEdit,
    RequestIn,
    Request,
    RequestEdit,
    Offer,
    OfferIn,
    OfferEdit,
    Feedback,
    FeedbackIn,
    FeedbackEdit,
)
from utils.service_result import handle_result
from config.database import get_db
from typing import List
from utils.dependencies import (
    get_current_user,
    request_checker,
    is_user_active,
    feedback_checker,
)

router = APIRouter(
    prefix="/submission",
    tags=["submissions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/order", response_model=Order)
async def create_order(
    data: OrderIn,
    bg_tasks: BackgroundTasks,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = await OrderService(db).create_order(data, user, bg_tasks)
    return handle_result(result)


@router.get("/order/{id}", response_model=Order)
async def get_order(id: int, user=Depends(get_current_user), db: get_db = Depends()):
    result = OrderService(db).get_order(id)
    return handle_result(result)


@router.get("/orders/client", response_model=List[Order])
async def get_orders_by_client(user=Depends(get_current_user), db: get_db = Depends()):
    result = OrderService(db).get_orders_by_client(user.id)
    return handle_result(result)


@router.get("/orders/master", response_model=List[Order])
async def get_orders_by_master(user=Depends(get_current_user), db: get_db = Depends()):
    result = OrderService(db).get_orders_by_master(user)
    return handle_result(result)


@router.patch("/order/{id}", response_model=Order)
async def patch_order(
    id: int,
    data: OrderEdit,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OrderService(db).patch_order(id, data, user)
    return handle_result(result)


@router.patch("/order/complete/{id}", response_model=dict)
async def finish_order(
    id: int,
    status: StatusEnum,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OrderService(db).finish_order(id, status, user)
    return handle_result(result)


@router.delete("/order/{id}")
async def delete_order(
    id: int,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OrderService(db).delete_order(id, user)
    return handle_result(result)


@router.post("/request", response_model=Request)
async def create_request(
    bg_tasks: BackgroundTasks,
    data: RequestIn = Depends(request_checker),
    files: List[UploadFile] = None,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = await RequestService(db).create_request(data, user, bg_tasks, files)
    return handle_result(result)


@router.get("/request/{id}", response_model=Request)
async def get_request(id: int, user=Depends(get_current_user), db: get_db = Depends()):
    result = RequestService(db).get_request(id)
    return handle_result(result)


@router.get("/requests", response_model=List[Request])
async def get_requests(user=Depends(get_current_user), db: get_db = Depends()):
    result = RequestService(db).get_requests(user.id)
    return handle_result(result)


@router.get("/requests/master", response_model=List[Request])
async def get_requests_by_master(
    user=Depends(get_current_user), db: get_db = Depends()
):
    result = RequestService(db).get_requests_by_master(user)
    return handle_result(result)


@router.get("/requests/client", response_model=List[Request])
async def get_requests_by_client(
    user=Depends(get_current_user), db: get_db = Depends()
):
    result = RequestService(db).get_requests_by_client_id(user.id)
    return handle_result(result)


@router.patch("/request/{id}", response_model=Request)
async def patch_request(
    id: int,
    data: RequestEdit,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = RequestService(db).patch_request(id, data, user.id)
    return handle_result(result)


@router.patch("/request/complete/{id}", response_model=dict)
async def complete_request(
    id: int,
    status: StatusEnum,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = RequestService(db).complete_request(id, user, status)
    return handle_result(result)


@router.delete("/request/{id}")
async def delete_request(
    id: int,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = RequestService(db).delete_request(id, user.id)
    return handle_result(result)


@router.post("/offer", response_model=Offer)
async def create_offer(
    data: OfferIn,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OfferService(db).create_offer(data, user)
    return handle_result(result)


@router.get("/offer", response_model=Offer)
async def get_offer(
    request_id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = OfferService(db).get_offer(request_id, user)
    return handle_result(result)


@router.get("/offers", response_model=List[Offer])
async def get_offers_by_submission(
    request_id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = OfferService(db).get_offers_by_submission(request_id)
    return handle_result(result)


@router.get("/offers/master", response_model=List[Offer])
async def get_offers_by_master(user=Depends(get_current_user), db: get_db = Depends()):
    result = OfferService(db).get_offers_by_master(user)
    return handle_result(result)


@router.patch("/offer/{id}", response_model=Offer)
async def patch_offer(
    id: int,
    data: OfferEdit,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OfferService(db).patch_offer(id, data, user)
    return handle_result(result)


@router.patch("/offer/complete/{id}", response_model=dict)
async def accept_offer(
    id: int,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OfferService(db).accept_offer(id, user)
    return handle_result(result)


@router.delete("/offer/{id}", response_model=Offer)
async def delete_offer(
    id: int,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = OfferService(db).delete_offer(id, user)
    return handle_result(result)


@router.post("/feedback", response_model=Feedback)
async def create_feedback(
    data: FeedbackIn = Depends(feedback_checker),
    pictures: List[UploadFile] = None,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = FeedbackService(db).create_feedback(data, user.id, pictures)
    return handle_result(result)


@router.get("/feedback", response_model=Feedback)
async def get_feedback(
    offer_id: int = None,
    order_id: int = None,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = FeedbackService(db).get_feedback(offer_id, order_id, user)
    return handle_result(result)


@router.get("/feedbacks/{master_username}", response_model=List[Feedback])
async def get_feedbacks(master_username: str, db: get_db = Depends()):
    result = FeedbackService(db).get_feedbacks(master_username)
    return handle_result(result)


@router.patch("/feedback/{id}", response_model=Feedback)
async def patch_feedback(
    id: int,
    data: FeedbackEdit,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = FeedbackService(db).patch_feedback(id, data, user)
    return handle_result(result)


@router.delete("/feedback/{id}")
async def delete_feedback(
    id: int,
    user=Depends(get_current_user),
    is_active=Depends(is_user_active),
    db: get_db = Depends(),
):
    result = FeedbackService(db).delete_feedback(id, user.id)
    return handle_result(result)
