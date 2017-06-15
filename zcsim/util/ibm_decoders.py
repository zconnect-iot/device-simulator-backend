"""
This file exposes some functionality which allows the server to
send notifications to devices - however does not allow the server
to get messages from workers, that's left to workers
"""
from datetime import datetime
import logging

from zcsim.util.json import dump_plain_json

from ibmiotf.codecs.jsonIotfCodec import decode

logger = logging.getLogger(__name__)

class NovoDecoder:
    @staticmethod
    def encode(data=None, timestamp=None):
        if timestamp:
            ts = timestamp.isoformat()
        else:
            ts = datetime.utcnow().isoformat()

        payload = { 'd': data, 'ts': ts }
        return dump_plain_json(payload)

    @staticmethod
    def decode(message):
        return decode(message)

