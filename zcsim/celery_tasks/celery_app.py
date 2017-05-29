from celery import Celery
from ambieprovision.settings import get_settings

settings = get_settings()

celery_settings = {
    'task_serializer': 'pickle',
    'result_serializer': 'pickle',
    'accept_content': ['pickle'],
    'imports': ['ambieprovision.celery_tasks.tasks'],
    'broker_url': settings['celery']['broker']
}

print("Connecting to celery: {}".format(settings['celery']['broker']))
app = Celery('tasks', backend=settings['celery']['broker'], broker=settings['celery']['broker'])
app.config_from_object(celery_settings)
print("Loaded celery settings")
