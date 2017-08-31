from libsim.models import (
    OnOffController,
    FirstOrder,
    Property,
    System,
)
from libsim.features import (
    ResetBy,
    BoundedBy,
)
from libsim.util import (
    range_transform,
)
from functools import (
    partial,
)
from operator import (
    eq,
)

thermostat = OnOffController(
    human_name="""Fridge actively cooling?""",
    name='thermostat',
    start=0,
    hyst=0.5,
    on=0,
    off=1,
) & (
    BoundedBy(0, 1)
)
thermostat_cooling = 1
thermostat_disabled = 0
set_point = Property(
    human_name='Cooling temperature',
    name='set-point', start=5, unit='deg. C',
    min=3, max=8, step=0.5
)
ambient_temp = Property(
    human_name='Ambient temperature',
    name='ambient-temp', start=25, unit='deg. C',
    min=20, max=30, step=0.5
)
hot_pipe_leak = Property(
    human_name='Is used cooling liquid pipe leaking?',
    name='hot-pipe-leak', start=0, unit='0/1',
    min=0, max=1, step=1,
)
cold_pipe_leak = Property(
    human_name='Is fresh cooling liquid pipe leaking?',
    name='cold-pipe-leak', start=0, unit='0/1',
    min=0, max=1, step=1,
)
door_opened = Property(
    human_name='Is door open?',
    name='door-opened', start=0, unit='0/1',
    min=0, max=1, step=1,
)


def hct_fi(is_leaking, thermostat, ambient_temp):
    tau = 60  # seconds
    gain = ambient_temp + 15 if not is_leaking else ambient_temp + 5
    return (
        (gain, tau, 1)
        if thermostat == thermostat_cooling else
        (ambient_temp, tau, 1)
    )


def cct_fi(is_leaking, thermostat, ambient_temp, set_point, cct_old):
    tau = 60
    gain = set_point - 1 if not is_leaking else set_point
    return (
        (gain, tau, 1)
        if thermostat == thermostat_cooling else
        (min(cct_old + 1, ambient_temp), tau, 1)
    )


def bt_fi(cct, door_opened):
    tau = 5 * 60
    gain = cct if not door_opened else cct + 5
    return (gain, tau, 1)


hot_coolant_temp = FirstOrder(
    human_name="""Temperature of used cooling fluid""",
    name='hot-coolant-temp',
    start=ambient_temp.start,
    fuse_inputs=hct_fi
) & (
    BoundedBy(ambient_temp.min, ambient_temp.max + 15)
)
cold_coolant_temp = FirstOrder(
    human_name="""Temperature of fresh cooling fluid""",
    name='cold-coolant-temp',
    start=ambient_temp.start,
    fuse_inputs=cct_fi
) & (
    BoundedBy(set_point.min - 1, ambient_temp.max)
)
box_temp = FirstOrder(
    human_name="""Temperature inside the fridge""",
    name='box-temp',
    start=ambient_temp.start,
    fuse_inputs=bt_fi
) & (
    BoundedBy(cold_coolant_temp.min, ambient_temp.max)
)
temp_diff_min = hot_coolant_temp.min - cold_coolant_temp.max
temp_diff_max = hot_coolant_temp.max - cold_coolant_temp.min
gain_from_temp_diff = range_transform((temp_diff_min, temp_diff_max), (0, 0.5))


def ci_fi(cct, hct):
    tau = 1
    return (1 + gain_from_temp_diff(hct - cct), tau, 1)


current_in = FirstOrder(
    human_name="""Current drawn from mains""",
    name='current-in', start=0, fuse_inputs=ci_fi
) & (
    ResetBy(partial(eq, thermostat_disabled)),
    BoundedBy(0, 2),
)


system = System(
    processes=(
        thermostat,
        box_temp,
        hot_coolant_temp,
        cold_coolant_temp,
        current_in,
    ),
    properties=(
        set_point,
        ambient_temp,
        hot_pipe_leak,
        cold_pipe_leak,
        door_opened,
    ),
    dependencies={
        thermostat: (box_temp, set_point),
        box_temp: (cold_coolant_temp, door_opened),
        hot_coolant_temp: (hot_pipe_leak, thermostat, ambient_temp),
        cold_coolant_temp: (cold_pipe_leak, thermostat, ambient_temp,
                            set_point, cold_coolant_temp),
        current_in: (thermostat, cold_coolant_temp, hot_coolant_temp)
    }
)
