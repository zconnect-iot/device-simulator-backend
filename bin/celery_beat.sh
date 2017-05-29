#!/bin/sh

echo "Starting"
celery -A zcsim.celery_tasks.celery_app beat --loglevel=DEBUG
