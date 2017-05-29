import time
from .celery_app import app
from celery import current_task
from celery.utils.log import get_task_logger
from datetime import datetime
from math import exp

from dateutil import parser
from dateutil.relativedelta import relativedelta

from ..util.redis import (
    get_redis,
    set_device_state,
    get_device_state,
    set_device_variables,
    get_device_variables,
    set_last_time_step,
    get_last_time_step,
)

from ..settings import get_settings

logger = get_task_logger(__name__)

def fridge_step(device_id, state, variables):
    """Performs the timesteps

    TODO: should be refactored in to some sort of device
    simulation abstractions so that multiple device
    types can be added easily.
    """
    settings = get_settings()
    time_step = relativedelta(seconds = settings['timestep_size'])
    s = dict(state)
    v = dict(variables)

    tau = settings['timestep_size'] / (60 * 60) # in hours

    #physics time
    epsilon = exp(-(tau * v["insulation"]) / v["thermal_mass"])
    T_i = epsilon * s["temp_in"] + (1 - epsilon) \
            * (v["temp_out"] - v["efficiency"] * \
                (s["present_current_draw"] / v["insulation"]))

    if T_i >= s["temp_in_max"]:
        s["present_current_draw"] = s["current_draw"] # Cool down

    elif T_i <= s["temp_in_min"]:
        s["present_current_draw"] = 0.0 # Stop cooling

    s["temp_in"] = T_i
    # Update things in state?
    logger.debug("Device {}: {} {}".format(device_id, s, v))
    logger.debug("Device {}: T_i: {:.2f}°C".format(device_id, T_i))

    return (s, v)

def get_device_info(device_id):
    """Gets device state with defaults

    There's a expiry set on the variables key
    which means that the defaults on here will be
    called fairly reguarly.

    state = things we can't affect
    variables = things we can change as the simulation runs

    """
    state = get_device_state(device_id)
    variables = get_device_variables(device_id)

    if not state.get("temp_in"):
        logger.info("setting default device state")
        state.update({
            "temp_in": 5.0,
            "current_draw": 70.0,
            "temp_in_min": 5.0,
            "temp_in_max": 8.0,
            "present_current_draw": 0.0,
        })

    if not variables:
        logger.info("setting default device variables")
        variables = {
            "temp_out": 21.0,
            "insulation": 3.21,
            "thermal_mass": 15.97,
            "efficiency": 3.0,
        }

    return (state, variables)

def set_device_info(device_id, state, variables):
    set_device_state(device_id, state)
    # Variables should only be set by the user
    #set_device_variables(device_id, variables)

def eval_device_time_step(device_id, up_to_time):
    """Checks a devices timestep and evaluates it needs running"""
    settings = get_settings()
    time_step = relativedelta(seconds = settings['timestep_size'])
    now = get_last_time_step(device_id, up_to_time)

    while (now + time_step) < up_to_time:
        logger.info("doing TS step for {}".format(device_id))
        # Do a step of simulation
        state, variables = get_device_info(device_id)
        state, variables = fridge_step(device_id, state, variables)
        set_device_info(device_id, state, variables)
        # Evaluate if we should send a TS data point to ZConnect platform
        # TODO

        now = set_last_time_step(device_id, now + time_step)

    logger.info("finished device {}".format(device_id))

@app.task()
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
