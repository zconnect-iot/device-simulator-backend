from libsim.util import (
    single_sample,
)
from libsim.models import (
    model,
)


def create_flip_flop_model(start, flip, flop, name='flip-flop'):
    @model(name=name, human_name=name, start=start)
    def _model(sim_step):
        val = flip if sim_step.x0 == flop else flop
        return single_sample(sim_step.duration, val)
    return _model


def never(*args):
    return False
