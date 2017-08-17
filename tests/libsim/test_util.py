from libsim.util import (
    within_top_margin,
    within_bottom_margin,
    single_sample,
    latest_sample,
    neg,
    predicate,
    range_transform,
)
import pytest


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


@predicate
def _truth():
    return True


@predicate
def _false():
    return False


def test_neg():
    false = neg(_truth)
    assert not false()


def test_predicate():
    assert not (_truth & _false)()
    assert (_false | _truth)()
    assert (~_false)()
    assert ((_truth & _false) | (_truth & _truth))()


def test_range_tf_should_raise_when_from_not_a_range():
    with pytest.raises(ValueError):
        range_transform((0, 0), (1, 2))


def test_range_transform_ints():
    _from = (0, 20)
    to = (20, 30)
    tf = range_transform(_from, to)
    assert tf(0) == 20
    assert tf(20) == 30
    assert tf(10) == 25


def test_range_transform_floats():
    _from = (0.0, 1.0)
    to = (20.0, 40.0)
    tf = range_transform(_from, to)
    assert tf(0.0) == 20.0
    assert tf(0.5) == 30.0
    assert tf(1.0) == 40.0
