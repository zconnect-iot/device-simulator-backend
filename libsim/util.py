def within_bottom_margin(_min, _max, frac, value):
    _range = _max - _min
    bottom_margin = _min + _range * frac
    return _min <= value <= bottom_margin


def within_top_margin(_min, _max, frac, value):
    _range = _max - _min
    top_margin = _max - _range * frac
    return top_margin <= value <= _max
