"""
`libsim` defines data structures and interface representing continuous,
linear, single-input-single-output (SISO) processes. Callable interface allows
for simulating these processes over a certain time period.

Instances of `models.Bounded` and `models.FirstOrder` are callables
returning time-series data as a pair of tuples (ts, samples).

To express MIMO systems, each variable must specify a function - `fuse_inputs`
- which is used to calculate the final control signal for this variable in a
given simulation step.

The core of this library, the `run.one_step` function, makes a distinction
between process and user-controlled variables. That allows for introduction of
external stimuli, like elements efficiency, leaks or bearings condition, which
would otherwise be non-intuitive to do via process variable parameters (i.e. DC
gain and time constant(s)).

Taking in current state of process variables, user-supplied parameters and
dependency table for process variables `run.one_step` returns the state of all
processes at the end of the simulation step.
"""
