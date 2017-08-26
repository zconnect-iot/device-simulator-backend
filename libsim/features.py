from collections import namedtuple as T
from .models import (
    ModelMixin,
)
from .util import (
    single_sample,
)

class FeatureMixin():
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in (set(self._fields) - set(('var_',))):
            return getattr(self.var_, name)


def feature_type(custom_fields):
    def decorate(f):
        nt_name = f.__name__ + '_props'
        nt_fields = ' '.join(('var_', custom_fields))
        bases = (
            ModelMixin,
            FeatureMixin,
            T(nt_name, nt_fields)
        )

        def invoke_model(self, sim_step):
            try:
                return f(self, self.var_, sim_step)
            except TypeError:
                return f(self.var_, sim_step)

        def create(cls, *args, **kwargs):
            def get(var):
                return cls(var, *args, **kwargs)
            return get

        ret_type = type(f.__name__, bases, {})
        setattr(ret_type, '__call__', invoke_model)
        setattr(ret_type, 'by', classmethod(create))

        return ret_type
    return decorate


@feature_type('min max')
def Bounded(props, var, sim_step):
    def _ensure_in_range(_min, _max, v):
        if v >= _max:
            return _max
        elif v <= _min:
            return _min
        else:
            return v

    ts, xs = var(sim_step)
    return (ts, tuple(_ensure_in_range(props.min, props.max, x) for x in xs))


@feature_type('pause_cond')
def Paused(props, var, sim_step):
    pause_on, *var_input = sim_step.inputs
    return (
        var(sim_step._replace(inputs=var_input))
        if not props.pause_cond(pause_on)
        else single_sample(sim_step.duration, sim_step.x0)
    )


@feature_type('reset_cond')
def Reset(props, var, sim_step):
    reset_on, *var_inputs = sim_step.inputs
    return (
        var(sim_step._replace(inputs=var_inputs))
        if not props.reset_cond(reset_on)
        else single_sample(sim_step.duration, var.start)
    )
