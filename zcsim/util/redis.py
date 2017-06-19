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
            redis_settings = settings['redis']['connection']
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

def get_device_state_min_max(device_id):
    min_max_thresholds = settings['min_max_thresholds']['state']
    state = get_device_state(device_id)

    for k,v in state.items():
        # Add the min / max values.
        try:
            state[k] = {
                "min": min_max_thresholds[k]["min"],
                "max": min_max_thresholds[k]["max"],
                "value": v,
            }
            if "name" in min_max_thresholds[k]:
                state[k].update({"human_name": min_max_thresholds[k]["name"]})
        except KeyError:
            state[k] = v
    return state

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

def delete_device_state(device_id):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.delete(device_key)

# device variables
def get_device_variables_key(device_id):
    return "{}_variables".format(device_id)

def set_device_variables(device_id, variables):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    redis.hmset(device_key, variables)
    if settings["reset_timeout"]:
        redis.expire(device_key, settings["reset_timeout"])

def get_device_variables_min_max(device_id):
    min_max_thresholds = settings['min_max_thresholds']['variables']
    variables = get_device_variables(device_id)

    for k,v in variables.items():
        # Add the min / max values.
        variables[k] = {
            "min": min_max_thresholds[k]["min"],
            "max": min_max_thresholds[k]["max"],
            "value": v,
        }
        if "name" in min_max_thresholds[k]:
            variables[k].update({"human_name": min_max_thresholds[k]["name"]})
    return variables

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

def delete_device_variables(device_id):
    redis = get_redis()
    device_key = get_device_variables_key(device_id)
    redis.delete(device_key)

def reset_state_and_variables(device_id):
    delete_device_state(device_id)
    delete_device_variables(device_id)

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

def get_last_send_time(device_id):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    ts_string = redis.hget(device_key, 'send_ts')
    if ts_string:
        return parser.parse(ts_string)
    else:
        return None

def set_last_send_time(device_id, ts):
    """
    Sets the last send time to the ts
    """
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.hset(device_key, 'send_ts', str(ts))
