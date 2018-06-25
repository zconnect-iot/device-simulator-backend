import threading
import logging
import os
from ibmiotf import application as ibm_application
import ibmiotf

logger = logging.getLogger(__name__)

class IbmSingleton:
    instance = None
    _lock = threading.Lock()

    def __new__(cls, gw_settings):
        if not cls.instance:
            logger.info("Got lock")
            try:
                logger.info("Not yet connected to IBM. Connecting...")
                logger.info("Thread: %s", threading.current_thread())
                logger.info("PID: %s", os.getpid())
                logger.info("gw_settings: %s", gw_settings)
                cls.instance = ibm_application.Client(gw_settings)
                logger.info("Created client, connecting")
                cls.instance.connect()
                logger.info("----------------------------------CONNECTED TO IBM-----------------------------")
            except ibmiotf.ConnectionException as e:
                logger.exception("=======================Failed to connect to IBM============================")
                cls.instance = None
                return None
            logger.info("Released lock")
        return cls.instance


def get_device_conn(gw_settings):
    logger.debug("Getting IBM connection")
    return IbmSingleton(gw_settings)
