from celery import Celery
from ..settings import get_settings

settings = get_settings()

app = Celery('tasks')
app.config_from_object("zcsim.settings.celery.{}".format(settings["env"]))

print("Loaded celery settings")
