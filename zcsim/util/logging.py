import logging
import logging.config

from ..settings import get_settings


class SystemNameFilter(logging.Filter):
    """docstring for SystemNameFilter"""
    def __init__(self, system_name):
        self.system_name = system_name

        super().__init__()

    def filter(self, record):
        record.sysname = self.system_name
        # We're just adding data, not filtering
        return True

def setup_logging(name, system_type_name):
    """
        Setup logging and add the system_type_name filter.

        name (str) The scope which logging is being set up from, e.g. 'novoserver.workers.store'
        system_type_name (str) The name of the system - will be used in paper trail
                                logs to set the env.
    """
    settings = get_settings()

    logging.config.dictConfig(settings["logging"])
    logger = logging.getLogger(__name__)
    context = SystemNameFilter(system_type_name)

    # Try to make sure it gets added to all handler instances
    for h in logger.parent.handlers + logger.handlers + logger.root.handlers:
        h.addFilter(context)

    logger.info("Set up logging {}".format(name))
    print("setup logging")

    return logger
