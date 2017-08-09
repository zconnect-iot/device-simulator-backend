from zcsim.libsim.models import (
    SimulationStep,
    latest_sample,
)

from tests.system import (
    bounded_angular_velocity,
)

def test_upper_bounds_ensured():
    """
    Long enough simulation duration should saturate a bounded variable
    """
    example_step = SimulationStep(
        x0=0,
        u=15000,
        duration=100
    )
    sim_res = bounded_angular_velocity(example_step)
    assert latest_sample(sim_res)  == bounded_angular_velocity.max

def test_lower_bounds_ensured():
    """
    Long enough simulation should saturate a bounded variable (lower bound)
    """
    example_step = SimulationStep(
        x0=0,
        u=-1,
        duration=100
    )
    _, samples = bounded_angular_velocity(example_step)
    assert not any(s < bounded_angular_velocity.min for s in samples)
