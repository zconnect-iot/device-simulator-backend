from celery.schedules import crontab

from ...settings import get_settings

settings = get_settings()

# get from main settings
redis_settings = settings["redis"]

if redis_settings.get("username", False):
    BROKER_URL = "redis://{username}:{password}@{host}:{port}".format(**redis_settings)
else:
    BROKER_URL = "redis://{host}:{port}".format(**redis_settings)

CELERY_TIMEZONE = 'Europe/London'
CELERY_ENABLE_UTC = True

CELERYBEAT_SCHEDULE = {
    "device_simulate_time": {
        "task": "zcsim.celery_tasks.tasks.test",
        "schedule": crontab(second="*/5"),
    }
}

__all__ = [
    "BROKER_URL",
    "CELERY_TIMEZONE",
    "CELERY_ENABLE_UTC",
    "CELERYBEAT_SCHEDULE",
]
