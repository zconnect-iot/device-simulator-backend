import logging
from dateutil import parser
from redis import ConnectionPool, StrictRedis

from ..settings import get_settings
from libsim.run import (
    system_from_module,
)
from itertools import (
    chain,
)

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


def to_redis(process_t, prop_t):
    return (
        {k.name: v for k, v in process_t.items()},
        {k.name: v for k, v in prop_t.items()}
    )


def from_redis(syscfg, redis_process_t, redis_prop_t):
    obj_from = {
        o.name: o for o in chain(syscfg.processes, syscfg.properties)
    }
    # TODO: get rid of magic keys leaking out of redis util
    return (
        {obj_from[k]: v for k, v in redis_process_t.items() if (k not in ('ts', 'send_ts'))},
        {obj_from[k]: v for k, v in redis_prop_t.items() if (k not in ('ts', 'send_ts'))}
    )


# Device state
def get_device_state_key(device_id):
    return "{}_state".format(device_id)

def set_device_state(device_id, state):
    redis = get_redis()
    device_key = get_device_state_key(device_id)
    redis.hmset(device_key, state)

def get_device_state_min_max(device_id):
    state = get_device_state(device_id)

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
    variables = get_device_variables(device_id)
    return variables


def get_device_info_extended(device_id):
    system = system_from_module(settings["sim_system"])
    variables = get_device_variables(device_id)
    state = get_device_state(device_id)

    processes, props = from_redis(system, state, variables)
    ext_state = {
        p.name: {
            'value': v,
            'human_name': p.human_name,
            'min': p.min,
            'max': p.max,
        }
        for p, v in processes.items()
    }
    ext_variables = {
        p.name: {
            'value': v,
            'human_name': p.human_name,
            'min': p.min,
            'max': p.max,
            'step': p.step,
        }
        for p, v in props.items()
    }

    return (ext_state, ext_variables)


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
