from libsim.models import (
    PauseWhen,
    SimulationStep
)
from libsim.util import (
    latest_sample,
    single_sample
)


def never(*args):
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
    step = SimulationStep(x0=1, inputs=(0,), duration=1)

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


def test_should_pass_down_input_tail():
    def assert_inputs(sim_step):
        v1, v2 = sim_step.inputs
        assert v1 == 1
        assert v2 == 2
    var = PauseWhen(cond=never, var=assert_inputs)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)


def test_should_pass_first_input_var_to_predicate():
    def pred(x):
        assert x == 0
        return False
    var = PauseWhen(cond=pred, var=model)
    step = SimulationStep(x0=1, inputs=(0, 1, 2), duration=1)
    var(step)
