from .celery_app import app
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from ..util.redis import (
    set_device_state,
    get_device_state,
    set_device_variables,
    get_device_variables,
    set_last_time_step,
    get_last_time_step,
    set_last_send_time,
    get_last_send_time
)

from ..settings import get_settings

from zcsim.util.task_base import WatsonIoTTaskBase

from itertools import chain

from zcsim.libsim.run import (
    system_from_module,
    one_step
)

logger = get_task_logger(__name__)


def system_tables_defaults(syscfg):
    return (
        {k: k.start for k in syscfg['processes']},
        {k: k.start for k in syscfg['properties']}
    )


def to_redis(process_t, prop_t):
    return (
        {k.name: v for k, v in process_t.items()},
        {k.name: v for k, v in prop_t.items()}
    )


def from_redis(syscfg, redis_process_t, redis_prop_t):
    obj_from = {
        o.name: o for o in chain(syscfg['processes'], syscfg['properties'])
    }
    # TODO: get rid of magic keys leaking out of redis util
    return (
        {obj_from[k]: v for k, v in redis_process_t.items() if (k not in ('ts', 'send_ts'))},
        {obj_from[k]: v for k, v in redis_prop_t.items() if (k not in ('ts', 'send_ts'))}
    )

def get_device_info(device_id):
    """Gets device state with defaults

    There's a expiry set on the variables key
    which means that the defaults on here will be
    called fairly reguarly.

    state = things we can't affect
    variables = things we can change as the simulation runs

    """
    system = system_from_module(get_settings()['sim_system'])
    state = get_device_state(device_id)
    variables = get_device_variables(device_id)
    default_state, default_props = to_redis(*system_tables_defaults(system))

    print("Variables were: {}".format(variables))

    # TODO: get rid of magic keys leaking out of redis util
    if all(k in ('ts', 'send_ts') for k in state.keys()):
        logger.info("setting default device state")
        state = default_state
        set_device_state(device_id, state)

    if not variables:
        logger.info("setting default device variables")
        variables = default_props
        set_device_variables(device_id, variables)

    return from_redis(system, state, variables) + (system['dependencies'],)

def eval_device_time_step(device_id, up_to_time):
    """Checks a devices timestep and evaluates it needs running"""
    settings = get_settings()
    time_step = relativedelta(seconds=settings['timestep_size'])
    now = get_last_time_step(device_id, up_to_time)

    send_interval = timedelta(seconds=settings['send_interval'])

    while (now + time_step) < up_to_time:
        logger.info("doing TS step for {}".format(device_id))
        # Do a step of simulation
        state, variables, dependencies = get_device_info(device_id)
        # one second of real time equals a minute of sim time
        state = one_step(state, variables, dependencies,
                         settings['timestep_size'] * 60)
        set_device_state(device_id, to_redis(state, variables)[0])
        # Evaluate if we should send a TS data point to ZConnect platform
        # TODO
        last_send_time = get_last_send_time(device_id)
        real_now = datetime.utcnow()
        if not last_send_time or real_now - last_send_time > send_interval:
            logger.info("Sending to IBM")
            upload_device_state(device_id)
            set_last_send_time(device_id, real_now)
        else:
            logger.info("Not sending to IBM, %s, %s, %s", last_send_time, now, send_interval)

        now = set_last_time_step(device_id, now + time_step)

    logger.info("finished device {}".format(device_id))

def upload_device_state(device_id):
    """ Upload the device state and variables to Watson IoT"""
    device_conn = time_step.watson
    # Get the state and variables so we can build our payload.
    state = get_device_state(device_id)
    variables = get_device_variables(device_id)

    payload = {
        "inside_temp": state['temp_in'],
        "external_temp": variables['temp_out'],
        "power_use": state['present_current_draw'],
    }
    device_conn.publishEvent("periodic",
                             "json-iotf",
                             payload)

    logger.info("Sent event to IBM with payload: %s", payload)


@app.task(base=WatsonIoTTaskBase, ignore_result=True)
def time_step():
    """ For each device id which we support, run the simulation for timesteps
        up to the current time.
    """
    settings = get_settings()
    devices = settings["devices"]

    now = datetime.now() # frozen time

    for device_id in devices:
        logger.info("Checking device {}".format(device_id))
        eval_device_time_step(device_id, now)
