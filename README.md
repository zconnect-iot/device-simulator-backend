# Basic Idea
The plan is that this 'server' exposes some endpoints to influence the simulation of one or more devices, so that failures and notifications can be invoked without real hardware.

The architecture is that we have a redis store which holds the state and simulation variables, along with a celery runner which will reguarly run through timesteps to update the simulation of a device.

As a PoC (in both interpretations of the analogy), this is just for a fridge simulation.

# Simulation

The core simulation logic is implemented in `libsim` package. It defines
basic building blocks from which the user can compose complete systems for
simulation.

## Concepts

Simulation data is divided into two groups of entities: *processes* and
*properties*. Together they are referred to as *signals*.

*Processes* represent signals which are simulated and can be observed via the
server API.

*Properties* represent any external interference, either from the user or the
environment, that can influence processes. That includes buttons and levers,
leaks in pipes, electrical efficiency of various components etc.

During the simulation, each signal has a scalar value. Step duration is assumed
to be in seconds.

A *system* consists of all the *signals* and *dependencies* (*D*) between them.
These dependencies together with the vector of current signal values
(*V<sub>current</sub>*) are used to calculate the vector of next signal values
(*V<sub>next</sub>*).

## Main loop

Simulation loop can be described by the following pseudocode.

1. Get default values of all processes and properties.
2. t := 0
2. Apply F(V<sub>current</sub>, D, duration) &rarr; V<sub>next</sub>
3. t := t + duration, V<sub>current</sub> := V<sub>next</sub>
2. Store (t, V<sub>next</sub>)
1. Go to 3.

## Data representation

```
type SignalVal = Number | Bool
type SimulationStep = {
    x0: SignalVal
    duration: Int
    inputs: Tuple<SignalVal>
}

# A *process* is a callable adhering to the following interface:

type Process = {
    __call__: (step: SimulationStep) -> SignalVal
    human_name: String # human-readable process name
    name: String # machine-readable process name, used as an id of the process
    start: SignalVal # value at the beginning of simulation
}

# A *property* is a named tuple with the following attributes:

type Property = {
    human_name: String # human-readable property name
    name: String # machine-readable process name, used as an id of the property
    unit: String # human-readable unit name
    start: SignalVal # value at the beginning of simulation
    min: SignalVal # property shall not be lower than this
    max: SignalVal # property shall not be higher than this
    step: SignalVal # smallest expected change in property value
}

# A *system* is a named tuple with the following attributes:

type System = {
    processes: Tuple<Process>
    properties: Tuple<Property>
    dependencies: Dict<Process, Tuple<Process | Property>>
}
```

Note that such abstraction allows for easily composing processes of orthogonal
parts, as long as they all conform to the Process interface. For an example of
that, see `libsim.features` module.

## How to use `libsim` API

### Process types - `libsim.models`

1. `FirstOrder(fuse_inputs)`

    Simulates a linear process with multiple inputs and one output (MISO)
    characterised by potentially variable *gain* and *time constant*. Both
    characteristics can be controlled by `fuse_inputs` function.

    `fuse_inputs(dep1, ..., depN : SignalVal): (gain: Number, time_constant:
    Number, fused_input_signal: Number)` is called at the beginning of every
    simulation step to calculate model parameters used for this step only. It
    may be called more than once, so it should have no visible side-effects.

1. `LinearCombination(coefficients)`

    Output signal is a linear combination of input signals with given
    `coefficients`.

1. `Counter(step)`

    Output signal is its value in previous sim step plus `step`.

1. `Boolean(predicate)`

    Output signal is 1 if `predicate` evaluates to true, else 0.

    `predicate(x0: SignalVal, inputs: Tuple<SignalVal>): Boolean` where x0 is
    own value from previous sim step and inputs is a tuple of dependencies'
    values.

1. `OnOffController(hyst, on, off)`

    Expects an input signal and set point signal as dependencies.

    Output signal is `on` when the input signal is below lower threshold or
    rising[(*)](#impl-note) between thresholds.

    Output signal is `off` when the input signal is above upper threshold or
    falling[(*)](#impl-note) between thresholds.

    Upper threshold is set point plus `hyst`.
    Lower threshold is set point minus `hyst`.

    <a name="impl-note"></a>(*) Rising and falling of the input signal is
    approximated by, respectively, previous `on` and previous `off` states.
    This leads to erratic behaviour when the input signal changes direction
    between thresholds, but is corrected as soon as it crosses any of them. It
    shouldn't be a problem unless `hyst` is too large for the problem you're
    trying to solve.

You can create your own models with `@model` and `@model_type` function
decorators.

`@model` is appropriate when you want to create a one-off, unparameterised
model from a simple function.

`@model_type` lets you create a class of parameterised model instances. Use it
when you need to create a model type similar in functionality to those
described above.

Example:
```python
from libsim.model import (model, model_type)
from libsim.utils import (single_sample)

@model(name='const1', human_name='My model 1', start=0)
def constant1(sim_step):
    return single_sample(sim_step.duration, 42)

@model_type('const')
def variable1(props, sim_step):
    return single_sample(sim_step.duration, props.const)

const2 = variable1(name='const2', human_name='My model 2', start=10, const=2)
```

### Optional process features - `libsim.features`

1. `BoundedBy(min, max)`

    Ensures that process output will be in range (min, max), inclusive.

2. `ResetBy(reset_cond)`

    Process is reset to its starting value if `reset_cond` evaluates to true.

    `reset_cond(reset_on: SignalVal): Boolean` is not guaranteed to be called
    only once and thus should have no visible side-effects.

    When you apply this feature, remember to
    prepend[(**)](#composing_features_note) the resetting signal to process
    dependencies.

3. `PausedBy(pause_cond)`

    Process is paused (value from previous step returned) if `pause_cond`
    evaluates to true.

    `pause_cond(pause_on: SignalVal): Boolean` is not guaranteed to be called
    only once and thus should have no visible side-effects.

    When you apply this feature, remember to
    prepend[(**)](#composing_features_note) the resetting signal to process
    dependencies.

Example:

```python
less_than_5 = operator.lt(5)
# features are composable
proc = FirstOrder(...) & BoundedBy(min=0, max=10) & ResetBy(less_than_5)
# which is equivalent to
proc = FirstOrder(...) & (BoundedBy(...), ResetBy(...))
```

Just like with processes, you can create your own features with `@feature_type`
function decorator.

Example:
```python
from libsim.features import feature_type
from libsim.util import single_sample

@feature_type('value')
def OverwrittenWith(props, var, sim_step):
    ignore = var(sim_step)
    return single_sample(sim_step.duration, props.value)

just_42 = Counter(...) & OverwrittenWith(42)
# same as
just_42 = Counter(...) & OverwrittenWith(value=42)


# omit the props if you don't need them
@feature_type()
def Inverted(var, sim_step):
    ts, xs = var(sim_step)
    return (ts, tuple(-x for x in xs))

inverted_counter = Counter(...) & Inverted()
```

## Final notes and caveats

It's worth keeping in mind that due to the dependencies being declared outside
of the actual process definitions, you have to make sure that their order in
the `system.dependencies` object matches exactly what is expected as `inputs`
in `Process.__call__` function of the process whose dependencies are being
declared.

TODO: Write helper functions in `libsim` to make sure it actually happens.

<a name=composing_features_note></a>(\*\*)Care needs to be taken when applying
features that require additional signals as dependencies, because the
dependency table for the original signal has to be
modified.

Example:

```python
def fi(dep1, dep2, dep3):
    ...

proc = FirstOrder(
    fuse_inputs=fi,
    ...
) & (
    ResetBy(...),
    PausedBy(...)
)

system = System(
    ...,
    dependencies: {
        ...,
        proc: (pausing_signal, resetting_signal, dep1, dep2, dep3)
    }
)
```

## System configuration

Any python module exposing `system` variable adhering to the above spec can be
treated as a valid system definition. For an example see
`zcsim/settings/system.py`. You can point the main simulation code to the right
definition with the `sim_system` key in the appropriate settings YAML file.

# Running

Needs docker and docker-compose installed. To spin up the worker, beat and server (on port 5000):

```
./run_docker.sh
```
