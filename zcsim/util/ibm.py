import threading
import logging
import os
from ibmiotf import device as ibm_device
from zcsim.util.ibm_decoders import NovoDecoder
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
                cls.instance = ibm_device.Client(gw_settings)
                cls.instance.setMessageEncoderModule("novo", NovoDecoder)
                logger.info("Created client, connecting")
                cls.instance.connect()
                logger.info("----------------------------------CONNECTED TO IBM-----------------------------")
            except ibmiotf.ConnectionException as e:
                logger.error("=======================Failed to connect to IBM============================")
            logger.info("Released lock")
        return cls.instance


def get_device_conn(gw_settings):
    logger.debug("Getting IBM connection")
    return IbmSingleton(gw_settings)

