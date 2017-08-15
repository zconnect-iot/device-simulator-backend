from libsim.models import (
    SimulationStep,
    ResetWhen,
)
from libsim.util import (
    latest_sample,
)

sim_step = SimulationStep(x0=0, inputs=(0,), duration=1)


def model(sim_step):
    val = 0 if sim_step.x0 else 42
    return (sim_step.duration,), (val,)


model.name = 'flip-flop'
model.start = 20


def test_reset():
    resettable = ResetWhen(var=model, cond=lambda s: s == 0)

    assert latest_sample(resettable(sim_step)) == 20
