"""
System definitions for test suite
"""

from libsim.models import (
    Property,
    FirstOrder,
    System,
)
from libsim.features import (
    Bounded,
)
load = Property(name='load', unit='kg', human_name='Load on shaft', start=0)
engine_efficiency = Property(
    name='engine-efficiency', unit='%', human_name='Eff', start=70
)


def input_current_fuse_inputs(engine_efficiency, load):
    return 1, 5, float(load)/1000.0 * engine_efficiency


angular_velocity_tau = 3


def angular_velocity_fuse_inputs(input_current, load):
    return 5, angular_velocity_tau, float(input_current)/float(load)


input_current = FirstOrder(
    name='input-current',
    human_name='Current draw from mains',
    start=0,
    fuse_inputs=input_current_fuse_inputs,
)

angular_velocity = FirstOrder(
    name='angular-velocity',
    human_name='RPM of shaft',
    start=0,
    fuse_inputs=angular_velocity_fuse_inputs
)
bounded_angular_velocity = angular_velocity & Bounded.by(min=0, max=15000)

deps = {
    angular_velocity: (input_current, load),
    bounded_angular_velocity: (input_current, load),
    input_current: (engine_efficiency, load)
}

system = System(**{
    'processes': (angular_velocity, bounded_angular_velocity, input_current),
    'properties': (load, engine_efficiency),
    'dependencies': deps,
})

incomplete_system = system._replace(dependencies=dict())

missing_signals = system._replace(
    processes=(input_current, ), properties=(load,)
)
