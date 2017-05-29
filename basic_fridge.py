# coding=utf8
"""
This file contains classes for simulating, controlling and observing a fridge.

@author: Stefan Scherfke
@contact: stefan.scherfke at uni-oldenburg.de

Updated for simpy 3 by Ben Howes of Zoetrope Labs (https://zoetrope.io)
"""

from math import exp
import logging
import random
from collections import namedtuple

import simpy

log = logging.getLogger('Processes')

FridgeInternalState = namedtuple("FridgeInternalState", ["temp", "current"])

def fridge(env, data_output, T_O = 20.0, A = 3.21, m_c = 15.97, tau = 1.0/60,
                  eta = 3.0, q_i = 0.0, q_max = 70.0,
                  T_i = 5.0, T_range = [5.0, 8.0], noise = False,
                  cool_on_start=True):
    """
    This generator represents a simulated fridge.

    It's temperature T for and equidistant series of time steps is computed by
    $T_{i+1} = \epsilon \cdot T_i + (1 - \epsilon) \cdot \left(T^O - \eta
    \cdot \frac{q_i}{A}\right)$ with $\epsilon = e^{-\frac{\tau A}{m_c}}$.

    @param env:       The SimPy simulation this process belongs to
    @type env:        SimPy.Environment instance
    @param data_output A list which we can append to
    @param T_O:       Outside temperature
    @param A:         Insulation
    @param m_c:       Thermal mass/thermal storage capacity
    @param tau:       Time span between t_i and t_{i+1}
    @param eta:       Efficiency of the cooling device
    @param q_i:       Initial/current electrical power
    @param q_max:     Power required during cool-down
    @param T_i:       Initial/current temperature
    @param T_range:   Allowed range for T_i
    @param noise:     Add noise to the fridge's parameters, if True
    @type noise:      bool
    """

    if cool_on_start:
        q_i = q_max

    while True:
        epsilon = exp(-(tau * A) / m_c)
        T_i = epsilon * T_i + (1 - epsilon) \
                * (T_O - eta * (q_i / A))
        if T_i >= T_range[1]:
            q_i = q_max         # Cool down
        elif T_i <= T_range[0]:
            q_i = 0.0                # Stop cooling

        log.debug('T_i: %2.2f°C at %.2f' % (T_i, env.now))
        data_output.append(FridgeInternalState(T_i, q_i))
        yield env.timeout(tau)

def fridge_observer(env, fridges, fridges_data, output, tau, aggSteps):
    """
    This process observes the temperature and power consumption of a set of
    fridges.

    @param fridges:     A list of fridges (not used)
    @param fridges_data:     A list of lists containing FridgeInternalState output from each fridge
    @param output:          The observable output aggregation
    @param tau:              Timestep size
    @aggSteps:          The number of steps per aggregation
    """

    _aggSteps = aggSteps
    aggSteps = 0
    consumption = 0
    lastProgUpdate = 0

    while True:
        #prog = env.now * 100 / self.sim._endtime
        #if int(prog) > lastProgUpdate:
        #    log.info('Progress: %d%%' % prog)
        #    lastProgUpdate = prog
        if (aggSteps >= _aggSteps):
            log.debug('Aggregating at %.2f' % env.now)
            output.append(consumption/_aggSteps)
            consumption = 0
            aggSteps = 0

        for fridge_data in fridges_data:
            consumption += fridge_data[-1].current

        aggSteps += 1
        yield env.timeout(tau)


if __name__ == '__main__':
    logging.basicConfig(
            level = logging.DEBUG,
            format = '%(levelname)-8s %(asctime)s %(name)s: %(message)s')

    tau = 1./60 # Step size 1min
    aggSteps = 15 # Aggregate consumption in 15min blocks
    params = {'tau': tau}

    env = simpy.Environment()

    data_output = []
    agg_output = []
    fridge = fridge(env, data_output)
    observer = fridge_observer(env, [fridge], [data_output], agg_output, tau, aggSteps)

    env.process(fridge)
    env.process(observer)
    env.run(until = 4 + tau)

    print(agg_output)
