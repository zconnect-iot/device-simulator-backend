from libsim import (models, util)

sim_step = models.SimulationStep(x0=0, inputs=(0,), duration=1)


def test_counter_one_step():
    ctr = models.Counter(name='ctr', start=10, step=1)
    assert util.latest_sample(ctr(sim_step)) == 1


def test_counter_counts_backwards():
    ctr = models.Counter(name='ctr', start=0, step=-1)
    assert util.latest_sample(ctr(sim_step)) == -1


def test_counter_respects_counter():
    ctr = models.Counter(name='ctr', start=0, step=2)
    assert util.latest_sample(ctr(sim_step)) == 2


def test_start_condition():
    assert models.Counter(name='ctr', start=0, step=1).start == 0
