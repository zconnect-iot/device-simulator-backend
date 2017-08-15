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
