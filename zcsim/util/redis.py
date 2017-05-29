import logging
from redis import ConnectionPool, StrictRedis
from ..settings import get_settings

logger = logging.getLogger(__name__)

class RedisConnectionPoolSingleton:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            redis_settings = get_settings()['redis']['connection']
            if 'username' in redis_settings:
                redis_settings.pop('username')
            cls.instance = ConnectionPool(*args, **kwargs, **redis_settings)
        return cls.instance


def get_redis():
    return StrictRedis(connection_pool=RedisConnectionPoolSingleton(decode_responses=True),
                       charset="utf-8",
                       decode_responses=True)
