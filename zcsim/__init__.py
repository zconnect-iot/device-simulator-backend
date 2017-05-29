import logging

# Use semantic versioning!
__version__ = "0.1.0"

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

def tracelog(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        # pylint: disable=protected-access
        self._log(TRACE_LEVEL_NUM, message, args, **kws)

logging.Logger.trace = tracelog
