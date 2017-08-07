"""
System definitions for test suite
"""

from zcsim.libsim.models import (
    ExternalVar,
    FirstOrderVar,
    Bounded,
)
load = ExternalVar(unit='kg', name='Load on shaft', start=0)
engine_efficiency = ExternalVar(unit='%', name='Eff', start=70)


def input_current_fuse_inputs(engine_efficiency, load):
    return float(load)/1000.0 * engine_efficiency


def angular_velocity_fuse_inputs(input_current, load):
    return float(input_current)/float(load)


input_current = FirstOrderVar(
    name='Current draw from mains',
    gain=1, time_constant=5, fuse_inputs=input_current_fuse_inputs,
    start=0
)

angular_velocity = FirstOrderVar(
    name='RPM of shaft',
    gain=5, time_constant=3, start=0,
    fuse_inputs=angular_velocity_fuse_inputs
)
bounded_angular_velocity = Bounded(var=angular_velocity, min=0, max=15000)

deps = {
    angular_velocity: (input_current, load),
    bounded_angular_velocity: (input_current, load),
    input_current: (engine_efficiency, load)
}

system = {
    'processes': (angular_velocity, bounded_angular_velocity, input_current),
    'properties': (load, engine_efficiency),
    'dependencies': deps,
}

incomplete_system = {
    'processes': system['processes'],
    'properties': system['properties'],
    'dependencies': dict()
}