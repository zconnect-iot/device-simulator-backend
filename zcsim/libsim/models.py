import numpy
from scipy.integrate import odeint
from collections import namedtuple as T

"""
@param gain - DC gain of the system
@param time_constant - time after which the output is at 95% of the total
                        step response.
"""


SimulationStep = T('SimulationStep', 'x0 u duration')


class FirstOrderVar(T('FirstOrderVar', 'name fuse_inputs gain time_constant')):
    def __call__(self, sim_step):
        """
        Compute the output of a first-order dynamical system.

        @param u - system input, considered constant for the duration of
                   time_step
        @param time_step - duration [0,time_step] of simulation
        """
        def model(x, t):
            """Solving x' = N*x + K*u for x"""
            return (-x + self.gain * sim_step.u)/self.time_constant
        # TODO: divide the timestamps in a smarter way
        ts = numpy.linspace(0, sim_step.duration, 100)
        xs = odeint(model, sim_step.x0, ts)
        return (ts, xs)


def angular_velocity(name):
    """
    @param power_in
    @param efficiency
    """
    gain = 0.3
    time_constant = 10

    def fuse(power_in, efficiency):
        return power_in * efficiency

    return FirstOrderVar(name, fuse, gain, time_constant)


def flow(name):
    gain = 1
    time_constant = 0.1

    def fuse(flow, valve_on):
        return flow if valve_on else 0

    return FirstOrderVar(name, fuse, gain, time_constant)
