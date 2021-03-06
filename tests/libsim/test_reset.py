from libsim.models import (
    SimulationStep
)
from libsim.features import (
    ResetBy,
)
from libsim.util import (
    latest_sample,
)
from tests.helpers import (
    create_flip_flop_model,
)
from functools import partial
from operator import eq

sim_step = SimulationStep(x0=0, inputs=(0,), duration=1)
model = create_flip_flop_model(start=20, flip=0, flop=42)


def never(*args):
    return False


def test_reset():
    """
    Should be reset to starting value when condition met
    """
    resettable = model & ResetBy(reset_cond=partial(eq, 0))

    assert latest_sample(resettable(sim_step)) == 20


def test_param_forwarding():
    """
    Should behave like a variable
    """
    assert (model & ResetBy(reset_cond=lambda: False)).start == 20


def test_should_pass_down_input_tail():
    def assert_inputs(sim_step):
        v1, v2 = sim_step.inputs
        assert v1 == 1
        assert v2 == 2
    var = ResetBy(never)(assert_inputs)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)


def test_should_call_predicate_with_first_input_only():
    def pred(x):
        assert x == 0
        return False
    var = model & ResetBy(pred)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)
