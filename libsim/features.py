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


def feature_type(custom_fields=None):
    custom_fields = custom_fields or ''
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

        ret_type = type(f.__name__ + '_t', bases, {})
        setattr(ret_type, '__call__', invoke_model)

        def create(*args, **kwargs):
            def get(var):
                return ret_type(var, *args, **kwargs)
            return get

        return create
    return decorate


@feature_type('min max')
def BoundedBy(props, var, sim_step):
    def _ensure_in_range(v):
        if v >= props.max:
            return props.max
        elif v <= props.min:
            return props.min
        else:
            return v

    ts, xs = var(sim_step)
    return (ts, tuple(_ensure_in_range(x) for x in xs))


@feature_type('pause_cond')
def PausedBy(props, var, sim_step):
    pause_on, *var_input = sim_step.inputs
    return (
        var(sim_step._replace(inputs=var_input))
        if not props.pause_cond(pause_on)
        else single_sample(sim_step.duration, sim_step.x0)
    )


@feature_type('reset_cond')
def ResetBy(props, var, sim_step):
    reset_on, *var_inputs = sim_step.inputs
    return (
        var(sim_step._replace(inputs=var_inputs))
        if not props.reset_cond(reset_on)
        else single_sample(sim_step.duration, var.start)
    )
