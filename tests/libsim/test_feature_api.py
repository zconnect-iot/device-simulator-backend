from tests.helpers import (
    create_flip_flop_model,
)
from libsim.models import (
    SimulationStep,
)
from libsim.features import (
    BoundedBy,
    PausedBy,
    feature_type,
)
from libsim.util import (
    latest_sample,
)
from functools import (
    partial,
)
from operator import (
    eq,
)

flop = 0
flip = 39
model = create_flip_flop_model(flip=flip, flop=flop, start=0)


def test_paramterless_feature_creation():
    @feature_type()
    def Inverted(var, sim_step):
        ts, xs = var(sim_step)
        return (ts, tuple(-x for x in xs))

    step = SimulationStep(x0=flip, duration=1, inputs=tuple())
    assert -flop == latest_sample((model & Inverted())(step))


def test_should_apply_a_feature():
    assert 10 == (model & BoundedBy(min=10, max=20)).min


def test_should_apply_all_features():
    new_model = model & (
        PausedBy(partial(eq,5)),
        BoundedBy(min=10, max=20),
    )
    maxing_step = SimulationStep(x0=flop, inputs=(6,), duration=1)
    pausing_step = maxing_step._replace(inputs=(5,))
    assert new_model.min == latest_sample(new_model(pausing_step))
    assert new_model.max == latest_sample(new_model(maxing_step))
