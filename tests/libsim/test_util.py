from libsim.util import (
    within_top_margin,
    within_bottom_margin,
    single_sample,
    latest_sample
)


def test_bottom_margin():
    assert within_bottom_margin(0, 1, 0.5, 0.25)
    assert within_bottom_margin(-1, 0, 0.5, -0.75)
    assert within_bottom_margin(0, 1, 0.1, 0)
    assert within_bottom_margin(0, 1, 0.1, 0.1)


def test_top_margin():
    assert within_top_margin(0, 1, 0.5, 0.75)
    assert within_top_margin(-1, 0, 0.5, -0.25)
    assert within_top_margin(0, 1, 0.1, 1)
    assert within_top_margin(0, 1, 0.1, 0.9)


def test_single_sample():
    assert single_sample(0, 1) == ((0,), (1,))


def test_latest_sample():
    assert latest_sample((tuple(range(20)), tuple(range(20,40)))) == 39
