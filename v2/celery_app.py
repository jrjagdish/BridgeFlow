import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "bridgeflow",
    broker=REDIS_URL,
    backend=None,   # job status tracked in DB — no Celery result backend needed
    include=["v2.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,    # results go to DB, not Celery backend
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "dispatch-all-syncs": {
            "task": "v2.tasks.dispatch_all_syncs",
            "schedule": 300.0,  # every 5 minutes
        }
    },
)
