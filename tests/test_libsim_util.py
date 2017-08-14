from zcsim.libsim.util import (
    within_top_margin,
    within_bottom_margin
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
