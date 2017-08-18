from libsim.util import (
    single_sample,
)


def create_flip_flop_model(start, flip, flop, name='flip-flop'):
    def model(sim_step):
        val = flip if sim_step.x0 == flop else flop
        return single_sample(sim_step.duration, val)
    model.start = start
    model.name = name
    return model
