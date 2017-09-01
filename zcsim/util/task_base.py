from celery import Task

from zcsim.settings import get_settings
from zcsim.util.ibm import get_device_conn


class WatsonIoTTaskBase(Task):
    _watson = None

    @property
    def watson(self):
        if not self._watson:
            # make a watson connection
            self._watson = get_device_conn(get_settings()["watson"])
        return self._watson
