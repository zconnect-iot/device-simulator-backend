import numpy
from .util import (
    single_sample
)
from scipy.integrate import odeint
from collections import namedtuple as T


def signal_fields(custom_fields=None):
    _signal_fields = ('name', 'human_name', 'start')
    custom_fields = custom_fields or ''
    return _signal_fields + tuple(custom_fields.split())


System = T('System', 'processes properties dependencies')
SimulationStep = T('SimulationStep', 'x0 inputs duration')
Property = T('Property', signal_fields('unit'))


class ModelMixin():
    def __and__(self, feature_or_features):
        """
        @feature_or_features is an iterable or a single element
        """
        try:  # @feature_or_features is a single callable
            feature = feature_or_features
            return feature(self)
        except TypeError:
            pass
        features = iter(feature_or_features)
        try:
            head = next(features)
            return head(self) & features
        except StopIteration:
            return self


def model_type(custom_fields=None):
    def decorate(f):
        bases = (
            ModelMixin,
            T(f.__name__ + '_props', signal_fields(custom_fields)),
        )

        def invoke_model(self, sim_step):
            try:
                return f(self, sim_step)
            except TypeError:
                return f(sim_step)

        return type(f.__name__, bases, {'__call__': invoke_model})
    return decorate


def model(name, human_name, start):
    def decorate(f):
        return model_type()(f)(name=name, human_name=human_name, start=start)
    return decorate


@model_type('fuse_inputs')
def FirstOrder(props, sim_step):
    """
    Compute the output of a first-order dynamical system.

    @param u - system input, considered constant for the duration of
    time_step
    @param time_step - duration [0,time_step] of simulation
    """
    gain, time_constant, u = props.fuse_inputs(*sim_step.inputs)

    def model(x, t):
        """Solving x' = N*x + K*u for x"""
        return (-x + gain * u)/time_constant
    # TODO: divide the timestamps in a smarter way
    ts = numpy.linspace(0, sim_step.duration, 100)
    xs = odeint(model, sim_step.x0, ts)
    return (ts, tuple(el for el in xs[:, 0]))


@model_type('coefficients')
def LinearCombination(props, sim_step):
    return single_sample(
        sim_step.duration,
        sum(c*v for c, v in zip(props.coefficients, sim_step.inputs))
    )


@model_type('step')
def Counter(props, sim_step):
        return single_sample(
            sim_step.duration,
            sim_step.x0 + props.step
        )


@model_type('predicate')
def Boolean(props, sim_step):
    return single_sample(
        sim_step.duration,
        1 if props.predicate(sim_step.x0, sim_step.inputs) else 0
    )


@model_type('hyst on off')
def OnOffController(props, sim_step):
    signal, set_point = sim_step.inputs
    upper_bound, lower_bound = set_point + props.hyst, set_point - props.hyst
    # handle out-of-bounds signal first
    if signal > upper_bound:
        return single_sample(sim_step.duration, props.off)
    if signal < lower_bound:
        return single_sample(sim_step.duration, props.on)
    else:
        return single_sample(sim_step.duration, sim_step.x0)
