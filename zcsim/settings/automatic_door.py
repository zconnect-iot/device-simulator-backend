from collections import namedtuple as T
from zcsim.libsim import models

motor_efficiency = models.Property(name='motor_efficiency', unit='%', start=70)
fuse_blown = models.Property(name='fuse_blown', unit='[yes/no]', start=0)
people_waiting = models.Property(
    name='people_waiting', unit='[yes/no]', start=0
)
bearing_condition = T('BearingConditon', 'left right')(
    left=models.Property(name='bearing_condition_left', unit='%', start=100),
    right=models.Property(name='bearing_condition_right', unit='%', start=100),
)


def _within_bottom_margin(_min, _max, frac, value):
    _range = _max - _min
    bottom_margin = _min + _range * frac
    return _min <= value <= bottom_margin


def _within_top_margin(_min, _max, frac, value):
    _range = _max - _min
    top_margin = _max - _range * frac
    return top_margin <= value <= _max


def door_position_input(door_position_now, people_waiting, bearing_condition, current_in):
    """
    It should take from 2 to 30 seconds for the doors to almost close. Remaining
    error could be treated as sensor tolerance.
    """
    # If insufficient engine power, don't move the door
    if not _within_top_margin(0, 5, 0.02, current_in):
        return door_position_now, 0.001, 1
    # linear transformation (0,100) -> (2,30)
    time_constant = (-28.0 * float(bearing_condition) + 3000.0) / 100.0
    gain = 10
    if people_waiting:
        return gain, time_constant, 1
    else:
        return gain, time_constant, 0


door_position = T('DoorPosition', 'left right')(
    left=models.FirstOrder(
        name='door_position_left', start=0,
        fuse_inputs=door_position_input
    ),
    right=models.FirstOrder(
        name='door_position_right', start=0,
        fuse_inputs=door_position_input
    ),
)


def current_in_inputs(door_position, people_waiting):
    gain = 5
    time_constant = 0.2
    door_should_open = people_waiting\
        and not _within_top_margin(0, 10, 0.05, door_position)
    door_should_close = not people_waiting\
        and not _within_bottom_margin(0, 10, 0.05, door_position)
    should_spin = door_should_open or door_should_close
    return (gain, time_constant, 1) if should_spin\
        else (gain, time_constant, 0)


current_in_left = models.FirstOrder(
    name='current_in_left',
    start=0,
    fuse_inputs=current_in_inputs
)


current_in_right = models.FirstOrder(
    name='current_in_right',
    start=0,
    fuse_inputs=current_in_inputs
)


system = {
    'processes': (
        door_position.left,
        door_position.right,
        current_in_left,
        current_in_right
    ),
    'properties': (
        fuse_blown,
        motor_efficiency,
        people_waiting,
        bearing_condition.left,
        bearing_condition.right
    ),
    'dependencies': {
        door_position.left: (door_position.left, people_waiting, bearing_condition.left, current_in_left),
        door_position.right: (door_position.right, people_waiting, bearing_condition.right, current_in_right),
        current_in_left: (door_position.left, people_waiting),
        current_in_right: (door_position.right, people_waiting)
    }
}
