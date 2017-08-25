import numpy
from .util import (
    single_sample
)
from .filters import (
    Bounded,
    PauseWhen,
    ResetWhen,
)
from scipy.integrate import odeint
from collections import namedtuple as T

System = T('System', 'processes properties dependencies')

SimulationStep = T('SimulationStep', 'x0 inputs duration')

_signal_fields = ('name', 'human_name', 'start')


def signal_fields(fields):
    return _signal_fields + tuple(fields.split())


Property = T('Property', signal_fields('unit'))


class FirstOrder(T('FirstOrder', signal_fields('fuse_inputs'))):
    """
    @prop gain - DC gain of the system
    @prop time_constant - time after which the output is at 95% of the total
                            step response.
    """
    def __call__(self, sim_step):
        """
        Compute the output of a first-order dynamical system.

        @param u - system input, considered constant for the duration of
                   time_step
        @param time_step - duration [0,time_step] of simulation
        """
        gain, time_constant, u = self.fuse_inputs(*sim_step.inputs)

        def model(x, t):
            """Solving x' = N*x + K*u for x"""
            return (-x + gain * u)/time_constant
        # TODO: divide the timestamps in a smarter way
        ts = numpy.linspace(0, sim_step.duration, 100)
        xs = odeint(model, sim_step.x0, ts)
        return (ts, tuple(el for el in xs[:, 0]))


class LinearCombination(T('LinearCombination', signal_fields('coefficients'))):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            sum(c*v for c, v in zip(self.coefficients, sim_step.inputs))
        )


class Counter(T('Counter', signal_fields('step'))):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            sim_step.x0 + self.step
        )


class Boolean(T('Boolean', signal_fields('predicate'))):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            1 if self.predicate(sim_step.x0, sim_step.inputs) else 0
        )


class OnOffController(T('OnOffController', signal_fields('hyst on off'))):
    def __call__(self, sim_step):
        signal, set_point = sim_step.inputs
        upper_bound, lower_bound = set_point + self.hyst, set_point - self.hyst
        # handle out-of-bounds signal first
        if signal > upper_bound:
            return single_sample(sim_step.duration, self.off)
        if signal < lower_bound:
            return single_sample(sim_step.duration, self.on)
        # now signal is within bounds for sure
        if sim_step.x0 == self.on:
            val = self.on if signal >= lower_bound else self.off
        else:
            val = self.off if signal <= upper_bound else self.on
        return single_sample(sim_step.duration, val)
