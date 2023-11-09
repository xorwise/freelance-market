import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from celery import Celery
from config.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from celery.schedules import crontab

celery = Celery(__name__)

celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND

celery.conf.task_routes = {"worker.delete_request": "delete_request"}

celery.conf.beat_schedule = {
    "celery_beat_payments": {
        "task": "worker.confirm_payments",
        "schedule": crontab(minute="*/1"),
    }
}

celery.autodiscover_tasks()

from yookassa import Payment
from config.yookassa import Configuration
from config.database import get_db
from models import ServiceRequest, StatusEnum, Payment as DBPayment, Master


@celery.task
def delete_request(request_id):
    db = next(get_db())
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if request.status == StatusEnum.active:
        db.delete(request)
        db.commit()
        print(f"Request #{request.id} deleted")


@celery.task
def confirm_payments():
    db = next(get_db())
    payments = db.query(DBPayment).filter(DBPayment.status == "pending").all()
    for payment in payments:
        payment_info = Payment.find_one(str(payment.payment_id))
        if payment_info.status == "succeeded":
            master = (
                db.query(Master)
                .filter(Master.username == payment.master_username)
                .first()
            )
            master.balance += payment.amount
            payment.is_confirmed = True
        payment.status = payment_info.status
        payment.paid = payment_info.paid
    print(f"{len(payments)} payments checked...")
    db.commit()
