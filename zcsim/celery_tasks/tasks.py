import time
from .celery_app import app
from celery import current_task
from celery.utils.log import get_task_logger
import signal
import subprocess
import os

from ..util.redis import get_redis


@app.task
def test():
    return 42
