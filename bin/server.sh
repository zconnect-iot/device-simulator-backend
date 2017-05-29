#!/bin/sh

echo "Starting"
uwsgi --ini=config/uwsgi-prod.ini
