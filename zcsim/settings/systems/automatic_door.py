from collections import namedtuple as T
from libsim import models
from libsim.util import (
    within_bottom_margin,
    within_top_margin,
    predicate,
    range_transform,
)
from functools import partial

motor_efficiency = models.Property(name='motor_efficiency', unit='%', start=70)
fuse_replaced = models.Property(name='fuse_replaced', unit='[0/1]', start=0)
people_waiting = models.Property(
    name='people_waiting', unit='[0/1]', start=0
)
bearing_condition = T('BearingConditon', 'left right')(
    left=models.Property(name='bearing_condition_left', unit='%', start=100),
    right=models.Property(name='bearing_condition_right', unit='%', start=100),
)


current_in_red_zone = predicate(partial(within_top_margin, 0, 5, 0.05))
current_in_green_zone = ~current_in_red_zone


def door_position_input(people_waiting, bearing_condition):
    """
    It should take from 2 to 30 seconds for the doors to almost close. Remaining
    error could be treated as sensor tolerance.
    """
    # linear transformation (0,100) -> (2,30)
    time_constant = range_transform((0, 100), (2, 30))(float(bearing_condition))
    gain = 10
    if people_waiting:
        return gain, time_constant, 1
    else:
        return gain, time_constant, 0


door_position = T('DoorPosition', 'left right')(
    left=models.PauseWhen(
        cond=current_in_green_zone,
        var=models.FirstOrder(
            human_name="Left door position sensor",
            name='door_position_left', start=0,
            fuse_inputs=door_position_input
        )
    ),
    right=models.PauseWhen(
        cond=current_in_green_zone,
        var=models.FirstOrder(
            human_name="Right door position sensor",
            name='door_position_right', start=0,
            fuse_inputs=door_position_input
        )
    )
)


def current_in_inputs(door_position, people_waiting):
    gain = 5
    time_constant = 0.2
    door_should_open = (
        people_waiting
        and
        not within_top_margin(0, 10, 0.05, door_position)
    )
    door_should_close = (
        not people_waiting
        and
        not within_bottom_margin(0, 10, 0.05, door_position)
    )
    should_spin = door_should_open or door_should_close
    return (
        (gain, time_constant, 1)
        if should_spin else
        (gain, time_constant, 0)
    )


current = T('Current', 'left right')(
    left=models.ResetWhen(
        cond=lambda fuse_blown: fuse_blown,
        var=models.Bounded(
            min=0, max=5,
            var=models.FirstOrder(
                human_name="Current drawn from mains (left door)",
                name='current_in_left',
                start=0,
                fuse_inputs=current_in_inputs
            )
        )
    ),
    right=models.ResetWhen(
        cond=lambda fuse_blown: fuse_blown,
        var=models.Bounded(
            min=0, max=5,
            var=models.FirstOrder(
                human_name="Current drawn from mains (right door)",
                name='current_in_right',
                start=0,
                fuse_inputs=current_in_inputs
            )
        )
    )
)


overheat = T('Overheat', 'left right')(
    left=models.ResetWhen(
        cond=current_in_green_zone,
        var=models.Counter(
            human_name="Time left until left motor fails",
            name='overheat_countdown_left', start=20, step=-1
        ),
    ),
    right=models.ResetWhen(
        cond=current_in_green_zone,
        var=models.Counter(
            human_name="Time left until right motor fails",
            name='overheat_countdown_right', start=20, step=-1
        ),
    )
)


@predicate
def is_fuse_blown(x0, inputs):
    overheat_left, overheat_right, fuse_replaced = inputs
    if x0:
        return not fuse_replaced
    else:
        return (overheat_left <= 0 or overheat_right <= 0)


fuse_blown = models.Boolean(
    human_name="Motor failure",
    name='fuse_blown',
    predicate=is_fuse_blown,
    start=0
)

system = models.System(**{
    'processes': (
        door_position.left, door_position.right,
        current.left, current.right,
        overheat.left, overheat.right,
        fuse_blown,
    ),
    'properties': (
        fuse_replaced,
        motor_efficiency,
        people_waiting,
        bearing_condition.left,
        bearing_condition.right
    ),
    'dependencies': {
        door_position.left: (
            current.left, people_waiting, bearing_condition.left
        ),
        door_position.right: (
            current.right, people_waiting, bearing_condition.right,
        ),
        current.left: (fuse_blown, door_position.left, people_waiting),
        current.right: (fuse_blown, door_position.right, people_waiting),
        overheat.left: (current.left,),
        overheat.right: (current.right,),
        fuse_blown: (overheat.left, overheat.right, fuse_replaced),
    }
})
