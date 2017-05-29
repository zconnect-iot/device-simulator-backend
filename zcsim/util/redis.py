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

# Device state
def get_device_state_key(device_id):
    return "{device_id}_state".format(device_id)

def set_device_state(device_id, state):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.hmset(device_key, state)

def get_device_state(device_id):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    return redis.hgetall(device_key)

# device variables
def get_device_variables_key(device_id):
    return "{device_id}_variables".format(device_id)

def set_device_variables(device_id, variables):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    redis.hmset(device_key, variables)

def get_device_variables(device_id):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    return redis.hgetall(device_key)
