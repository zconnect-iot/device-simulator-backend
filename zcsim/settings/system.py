"""
System definitions for the real simulation
"""

from zcsim.libsim.models import (
    ExternalVar,
    FirstOrderVar,
    Bounded,
)
load = ExternalVar(unit='kg', name='Load on shaft', start=0)
engine_efficiency = ExternalVar(unit='%', name='Engine efficiency', start=70)


def input_current_fuse_inputs(engine_efficiency, load):
    return 1, 5, float(load)/1000.0 * engine_efficiency


def angular_velocity_fuse_inputs(input_current, load):
    return 5, 3, float(input_current)/float(load) if load > 0 else 0


input_current = FirstOrderVar(
    name='Current draw from mains',
    start=0,
    fuse_inputs=input_current_fuse_inputs,
)

angular_velocity = FirstOrderVar(
    name='RPM of shaft',
    start=0,
    fuse_inputs=angular_velocity_fuse_inputs
)
bounded_angular_velocity = Bounded(var=angular_velocity, min=0, max=15000)

system = {
    'processes': (bounded_angular_velocity, input_current),
    'properties': (load, engine_efficiency),
    'dependencies': {
        bounded_angular_velocity: (input_current, load),
        input_current: (engine_efficiency, load)
    }
}
