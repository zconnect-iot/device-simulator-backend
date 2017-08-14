
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
    name: String # human-readable process name
    start: SignalVal # value at the beginning of simulation
}

# A *property* is a named tuple with the following attributes:

type Property = {
    name: String # human-readable property name
    unit: String # human-readable unit name
    start: SignalVal # value at the beginning of simulation
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
that, see `libsim.models.Bounded`.

It's worth keeping in mind that due to the dependencies being declared outside
of the actual process definitions, you have to make sure that their order in
the `system.dependencies` object matches exactly what is expected as `inputs`
in `Process.__call__` function of the process whose dependencies are being
declared.

TODO: Write helper functions in `libsim` to make sure it actually happens.

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
