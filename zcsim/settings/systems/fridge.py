from libsim.models import (
    OnOffController,
    FirstOrder,
    ResetWhen,
    Property,
    System,
)

thermostat = OnOffController(
    name='thermostat',
    start=0,
    hyst=0.5,
    on=0,
    off=1,
)
thermostat_cooling = 1
thermostat_disabled = 0
set_point = Property(name='set-point', start=5, unit='deg. C')
ambient_temp = Property(name='ambient-temp', start=25, unit='deg. C')
hot_pipe_leak = Property(name='hot-pipe-leak', start=0, unit='0/1')
cold_pipe_leak = Property(name='cold-pipe-leak', start=0, unit='0/1')
door_opened = Property(name='door-opened', start=0, unit='0/1')


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


def ci_fi(cold_pipe_leak, hot_pipe_leak):
    gain = 2 if (cold_pipe_leak or hot_pipe_leak) else 1
    tau = 1
    return (gain, tau, 1)


hot_coolant_temp = FirstOrder(
    name='hot-coolant-temp',
    start=ambient_temp.start,
    fuse_inputs=hct_fi
)
cold_coolant_temp = FirstOrder(
    name='cold-coolant-temp',
    start=ambient_temp.start,
    fuse_inputs=cct_fi
)
box_temp = FirstOrder(
    name='box-temp',
    start=ambient_temp.start,
    fuse_inputs=bt_fi
)
current_in = ResetWhen(
    cond=lambda ctrl: ctrl == thermostat_disabled,
    var=FirstOrder(name='current-in', start=0, fuse_inputs=ci_fi)
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
        current_in: (thermostat, cold_pipe_leak, hot_pipe_leak)
    }
)
