from collections import namedtuple as T
from .util import single_sample


class __Base():
    def __getattr__(self, name):
        """
        Forward any unknown attributes to wrapped component
        """
        if name not in (set(self._fields) - set(('var',))):
            return getattr(self.var, name)


class Bounded(__Base, T('Bounded', 'var min max')):
    def _ensure_in_range(self, v):
        if v >= self.max:
            return self.max
        elif v <= self.min:
            return self.min
        else:
            return v

    def __call__(self, sim_step):
        ts, xs = self.var(sim_step)
        return (ts, tuple(self._ensure_in_range(x) for x in xs))


def bounded(min, max):
    def get(var):
        return Bounded(var=var, min=min, max=max)
    return get


class ResetWhen(__Base, T('ResetWhen', 'var cond')):
    def __call__(self, sim_step):
        reset_on, *var_inputs = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=var_inputs))
            if not self.cond(reset_on)
            else single_sample(sim_step.duration, self.var.start)
        )


def reset_when(cond):
    def get(var):
        return ResetWhen(var=var, cond=cond)
    return get


class PauseWhen(__Base, T('PauseWhen', 'var cond')):
    def __call__(self, sim_step):
        pause_on, *var_input = sim_step.inputs
        return (
            self.var(sim_step._replace(inputs=var_input))
            if not self.cond(pause_on)
            else single_sample(sim_step.duration, sim_step.x0)
        )


def pause_when(cond):
    def get(var):
        return PauseWhen(var=var, cond=cond)
    return get
