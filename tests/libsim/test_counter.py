from libsim import (models, util)

sim_step = models.SimulationStep(x0=0, inputs=(0,), duration=1)


def counter(start, step):
    return models.Counter(human_name='ctr', name='ctr', start=start, step=step)


def test_counter_one_step():
    ctr = counter(start=10, step=1)
    assert util.latest_sample(ctr(sim_step)) == 1


def test_counter_counts_backwards():
    ctr = counter(start=0, step=-1)
    assert util.latest_sample(ctr(sim_step)) == -1


def test_counter_respects_counter():
    ctr = counter(start=0, step=2)
    assert util.latest_sample(ctr(sim_step)) == 2


def test_start_condition():
    assert counter(start=0, step=1).start == 0
