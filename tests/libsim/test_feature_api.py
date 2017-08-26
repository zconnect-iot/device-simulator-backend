from tests.helpers import (
    create_flip_flop_model,
)
from libsim.models import (
    SimulationStep,
)
from libsim.features import (
    Bounded,
    Paused,
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
model = create_flip_flop_model(flip=39, flop=flop, start=0)


def test_should_apply_a_feature():
    assert 10 == (model & Bounded.by(min=10, max=20)).min


def test_should_apply_all_features():
    new_model = model & (
        Paused.by(partial(eq,5)),
        Bounded.by(min=10, max=20),
    )
    maxing_step = SimulationStep(x0=flop, inputs=(6,), duration=1)
    pausing_step = maxing_step._replace(inputs=(5,))
    assert new_model.min == latest_sample(new_model(pausing_step))
    assert new_model.max == latest_sample(new_model(maxing_step))
