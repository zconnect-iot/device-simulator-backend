import numpy
from scipy.integrate import odeint
from collections import namedtuple as T

Property = T('Property', 'unit name start')

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
        return (
            (sim_step.duration,),
            (sum(c*v for c,v in zip(self.coefficients, sim_step.inputs)),)
        )

def latest_sample(sim_result):
    """
    Returns the variable value at the end of simulation step
    """
    ts, xs = sim_result
    # TODO: Change this when adding higher order variables
    return xs[-1]
