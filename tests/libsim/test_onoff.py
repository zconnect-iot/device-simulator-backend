from libsim.models import (
    SimulationStep,
    OnOffController,
)
from libsim.util import (
    latest_sample,
)


def is_on(ctrl, step):
    return latest_sample(ctrl(step)) == ctrl.on


def is_off(ctrl, step):
    return latest_sample(ctrl(step)) == ctrl.off


def controller(start, hyst, on, off):
    return OnOffController(
        human_name='', name='abcd', start=start, hyst=hyst, on=on, off=off
    )


def test_onoff_adheres_to_variable_protocol():
    step = SimulationStep(x0=0, duration=1, inputs=(0, 0))
    ctrl = controller(start=0, hyst=0, on=1, off=0)
    assert ctrl.name == 'abcd'
    assert ctrl.start == 0
    assert latest_sample(ctrl(step)) in (ctrl.on, ctrl.off)


def test_onoff_on_when_signal_below_set_point():
    step = SimulationStep(x0=0, duration=1, inputs=(-1, 0))
    ctrl = controller(start=0, hyst=0, on=1, off=0)
    assert latest_sample(ctrl(step)) == ctrl.on


def test_onoff_off_when_signal_above_set_point():
    step = SimulationStep(x0=0, duration=1, inputs=(1, 0))
    ctrl = controller(start=0, hyst=0, on=1, off=0)
    assert latest_sample(ctrl(step)) == ctrl.off


def test_onoff_switches_on_when_signal_below_lower_bound():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.off, duration=1, inputs=(-2, 0))
    assert is_on(ctrl, step)


def test_onoff_stays_on_when_signal_below_lower_bound():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.on, duration=1, inputs=(-2, 0))
    assert is_on(ctrl, step)


def test_onoff_switches_off_when_signal_above_upper_bound():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.on, duration=1, inputs=(2, 0))
    assert is_off(ctrl, step)


def test_onoff_stays_off_when_signal_above_upper_bound():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.off, duration=1, inputs=(2, 0))
    assert is_off(ctrl, step)


def test_onoff_stays_off_when_signal_within_bounds():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.off, duration=1, inputs=(0.5, 0))
    assert is_off(ctrl, step)


def test_onoff_stays_on_when_signal_within_bounds():
    ctrl = controller(start=0, hyst=1, on=1, off=0)
    step = SimulationStep(x0=ctrl.on, duration=1, inputs=(0.5, 0))
    assert is_on(ctrl, step)
