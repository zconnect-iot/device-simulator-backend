from functools import wraps
from collections import namedtuple as T


def within_bottom_margin(_min, _max, frac, value):
    _range = _max - _min
    bottom_margin = _min + _range * frac
    return _min <= value <= bottom_margin


def within_top_margin(_min, _max, frac, value):
    _range = _max - _min
    top_margin = _max - _range * frac
    return top_margin <= value <= _max


def single_sample(t, x):
    return ((t,), (x,))


def latest_sample(sim_result):
    """
    Returns the variable value at the end of simulation step
    """
    ts, xs = sim_result
    # TODO: Change this when adding higher order variables
    return xs[-1]


def neg(f):
    @wraps(f)
    def _(*args, **kwargs):
        return not f(*args, **kwargs)
    return _


class Predicate(T('Predicate', 'f')):
    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __and__(self, pred):
        def _and_(*args, **kwargs):
            return self.f(*args, **kwargs) and pred(*args, **kwargs)
        return Predicate(_and_)

    def __or__(self, pred):
        def _or_(*args, **kwargs):
            return self.f(*args, **kwargs) or pred(*args, **kwargs)
        return Predicate(_or_)

    def __invert__(self):
        return neg(self.f)


def predicate(f):
    return wraps(f)(Predicate(f))
