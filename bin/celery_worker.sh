#!/bin/sh

echo "Starting"
su -m celery_worker_user -c "celery -A zcsim.celery_tasks.celery_app worker --loglevel=DEBUG"
