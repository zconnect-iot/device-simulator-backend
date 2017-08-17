import numpy
from .util import (
    single_sample
)
from scipy.integrate import odeint
from collections import namedtuple as T

Property = T('Property', 'unit name start')
System = T('System', 'processes properties dependencies')

SimulationStep = T('SimulationStep', 'x0 inputs duration')


class Bounded(T('Bounded', 'var min max')):
    def _ensure_in_range(self, v):
        if v >= self.max:
            return self.max
        elif v <= self.min:
            return self.min
        else:
            return v

    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in ('min', 'max'):
            return getattr(self.var, name)

    def __call__(self, sim_step):
        ts, xs = self.var(sim_step)
        return (ts, tuple(self._ensure_in_range(x) for x in xs))


class FirstOrder(T('FirstOrder', 'name fuse_inputs start')):
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


class LinearCombination(T('LinearCombination', 'coefficients')):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            sum(c*v for c, v in zip(self.coefficients, sim_step.inputs))
        )


class Counter(T('Counter', 'start step name')):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            sim_step.x0 + self.step
        )


class ResetWhen(T('ResetWhen', 'var cond')):
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in ('cond',):
            return getattr(self.var, name)

    def __call__(self, sim_step):
        reset_on, *_ = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=sim_step.inputs[1:]))
            if not self.cond(reset_on)
            else single_sample(sim_step.duration, self.var.start)
        )


class PauseWhen(T('PauseWhen', 'var cond')):
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in ('cond',):
            return getattr(self.var, name)

    def __call__(self, sim_step):
        pause_on, *var_input = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=var_input))
            if not self.cond(pause_on)
            else single_sample(sim_step.duration, sim_step.x0)
        )


class Boolean(T('Boolean', 'name start predicate')):
    def __call__(self, sim_step):
        return single_sample(
            sim_step.duration,
            1 if self.predicate(sim_step.x0, sim_step.inputs) else 0
        )
