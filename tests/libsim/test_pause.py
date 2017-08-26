from libsim.models import (
    SimulationStep
)
from libsim.features import (
    Paused,
)
from libsim.util import (
    latest_sample,
)
from tests.helpers import (
    create_flip_flop_model
)


def never(*args):
    return False


def id(x):
    return x


model = create_flip_flop_model(start=0, flip=0, flop=1)


def test_process_interface():
    """
    Should behave like a variable
    """
    var = model & Paused.by(never)
    step = SimulationStep(x0=1, inputs=(0,), duration=1)

    assert var.name == model.name
    assert var.start == model.start
    assert latest_sample(var(step)) == 0


def test_pauses():
    """
    Should not flip when paused
    """
    var = model & Paused.by(id)
    step = SimulationStep(x0=1, inputs=(1,), duration=1)

    assert latest_sample(var(step)) == 1


def test_should_pass_down_input_tail():
    def assert_inputs(sim_step):
        v1, v2 = sim_step.inputs
        assert v1 == 1
        assert v2 == 2
    var = Paused.by(never)(assert_inputs)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)


def test_should_pass_first_input_var_to_predicate():
    def pred(x):
        assert x == 0
        return False
    var = model & Paused.by(pred)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)
