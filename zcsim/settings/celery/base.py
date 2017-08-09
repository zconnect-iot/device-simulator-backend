from celery.schedules import crontab

from ...settings import get_settings

settings = get_settings()

# get from main settings
redis_settings = settings["redis"]["connection"]

if redis_settings.get("username", False):
    BROKER_URL = "redis://{username}:{password}@{host}:{port}".format(**redis_settings)
else:
    BROKER_URL = "redis://{host}:{port}".format(**redis_settings)

CELERY_TIMEZONE = 'Europe/London'
CELERY_ENABLE_UTC = True

CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER='pickle'
CELERY_ACCEPT_CONTENT = ['pickle']


CELERYBEAT_SCHEDULE = {
    "device_simulate_time": {
        "task": "zcsim.celery_tasks.tasks.time_step",
        "schedule": settings["timestep_size"],
    }
}

__all__ = [
    "BROKER_URL",
    "CELERY_TIMEZONE",
    "CELERY_ENABLE_UTC",
    "CELERYBEAT_SCHEDULE",
]
