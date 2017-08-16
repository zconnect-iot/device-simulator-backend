from libsim.models import (
    PauseWhen,
    SimulationStep
)
from libsim.util import (
    latest_sample,
    single_sample
)


def never():
    return False


def id(x):
    return x


def model(sim_step):
    val = 0 if sim_step.x0 else 1
    return single_sample(sim_step.duration, val)


model.name = 'flip-flop'
model.start = 0


def test_process_interface():
    """
    Should behave like a variable
    """
    var = PauseWhen(cond=never, var=model)
    step = SimulationStep(x0=1, inputs=tuple(), duration=1)

    assert var.name == model.name
    assert var.start == model.start
    assert latest_sample(var(step)) == 0


def test_pauses():
    """
    Should not flip when paused
    """
    var = PauseWhen(cond=id, var=model)
    step = SimulationStep(x0=1, inputs=(1,), duration=1)

    assert latest_sample(var(step)) == 1
