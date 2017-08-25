from libsim.models import (
    SimulationStep,
    bounded
)

from tests.system import (
    bounded_angular_velocity,
)

def dummy_model(sim_step):
    return 'data'


def test_upper_bounds_ensured():
    """
    Long enough simulation should saturate a bounded variable
    """
    example_step = SimulationStep(
        x0=0,
        inputs=(15000,1),
        duration=100
    )
    _, samples = bounded_angular_velocity(example_step)
    assert not any(s > bounded_angular_velocity.max for s in samples)

def test_lower_bounds_ensured():
    """
    Long enough simulation should saturate a bounded variable (lower bound)
    """
    example_step = SimulationStep(
        x0=0,
        inputs=(-1,1),
        duration=100
    )
    _, samples = bounded_angular_velocity(example_step)
    assert not any(s < bounded_angular_velocity.min for s in samples)


def test_factory():
    assert 15 == bounded(1,15)(dummy_model).max
