from libsim.models import (
    ResetWhen,
    SimulationStep
)
from libsim.util import (
    latest_sample,
    single_sample
)
from functools import partial
from operator import eq

sim_step = SimulationStep(x0=0, inputs=(0,), duration=1)


def model(sim_step):
    val = 0 if sim_step.x0 else 42
    return single_sample(sim_step.duration, val)


model.name = 'flip-flop'
model.start = 20


def never(*args):
    return False


def test_reset():
    """
    Should be reset to starting value when condition met
    """
    resettable = ResetWhen(var=model, cond=partial(eq, 0))

    assert latest_sample(resettable(sim_step)) == 20


def test_param_forwarding():
    """
    Should behave like a variable
    """
    assert ResetWhen(var=model, cond=lambda: False).start == 20


def test_should_pass_down_input_tail():
    def assert_inputs(sim_step):
        v1, v2 = sim_step.inputs
        assert v1 == 1
        assert v2 == 2
    var = ResetWhen(cond=never, var=assert_inputs)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)
