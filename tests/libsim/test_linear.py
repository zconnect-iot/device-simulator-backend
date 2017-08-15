from libsim import (models, util)


def test_coefficient_applied():
    coefficients = (1, 2, 3)
    step = models.SimulationStep(
        x0=0, duration=100, inputs=(3, 4, 5)
    )
    var = models.LinearCombination(coefficients)

    assert util.latest_sample(var(step)) == 26
