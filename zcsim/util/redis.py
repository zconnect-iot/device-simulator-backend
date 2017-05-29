import logging
from dateutil import parser
from redis import ConnectionPool, StrictRedis

from ..settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisConnectionPoolSingleton:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            redis_settings = settings['redis']
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
    return "{}_state".format(device_id)

def set_device_state(device_id, state):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.hmset(device_key, state)

def get_device_state(device_id):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    data = redis.hgetall(device_key)
    for k,v in data.items():
        try: # try to make everything a float
            data[k] = float(v)
        except ValueError:
            pass
    return data

# device variables
def get_device_variables_key(device_id):
    return "{}_variables".format(device_id)

def set_device_variables(device_id, variables):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    redis.hmset(device_key, variables)
    redis.expire(device_key, settings["reset_timeout"])

def get_device_variables(device_id):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    data = redis.hgetall(device_key)
    for k,v in data.items():
        try: # try to make everything a float
            data[k] = float(v)
        except ValueError:
            pass
    return data

# Timestep helpers
def get_last_time_step(device_id, now):
    """returns either the timestamp from redis or the current time"""
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    ts_string = redis.hget(device_key, "ts")
    if not ts_string:
        ts = now
        set_last_time_step(device_id, ts)
    else:
        ts = parser.parse(ts_string)
    return ts

def set_last_time_step(device_id, ts):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.hset(device_key, "ts", str(ts))
    return ts
