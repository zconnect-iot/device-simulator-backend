
# Basic Idea
The plan is that this 'server' exposes some endpoints to influence the simulation of one or more devices, so that failures and notifications can be invoked without real hardware.

The architecture is that we have a redis store which holds the state and simulation variables, along with a celery runner which will reguarly run through timesteps to update the simulation of a device.

As a PoC (in both interpretations of the analogy), this is just for a fridge simulation.

# Running

Needs docker and docker-compose installed. To spin up the worker, beat and server (on port 5000):

```
./run_docker.sh
```
