from collections import namedtuple as T
from .util import single_sample


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


class ResetWhen(T('ResetWhen', 'var cond')):
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in ('cond',):
            return getattr(self.var, name)

    def __call__(self, sim_step):
        reset_on, *var_inputs = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=var_inputs))
            if not self.cond(reset_on)
            else single_sample(sim_step.duration, self.var.start)
        )


class PauseWhen(T('PauseWhen', 'var cond')):
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in ('cond',):
            return getattr(self.var, name)

    def __call__(self, sim_step):
        pause_on, *var_input = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=var_input))
            if not self.cond(pause_on)
            else single_sample(sim_step.duration, sim_step.x0)
        )
