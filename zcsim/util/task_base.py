from celery import Task

from zcsim.util.ibm import get_device_conn


class WatsonIoTTaskBase(Task):
    _watson = None

    @property
    def watson(self):
        if not self._watson:
            # make a watson connection
            self._watson = get_device_conn()
        return self._watson