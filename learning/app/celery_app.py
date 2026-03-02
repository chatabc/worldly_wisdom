import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "learning_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.video_tasks", "app.tasks.knowledge_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

celery_app.conf.beat_schedule = {
    "daily-learning-task": {
        "task": "app.tasks.video_tasks.scheduled_learning",
        "schedule": crontab(hour=2, minute=0),
    },
}
