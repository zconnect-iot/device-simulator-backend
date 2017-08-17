from itertools import chain
from .models import SimulationStep
from .util import latest_sample
import importlib
from functools import lru_cache


def _shallow_dict_merge(d1, d2):
    return {k: v for k, v in chain(d1.items(), d2.items())}


def one_step(process_table, props_table, dependencies_table, duration):
    common_table = _shallow_dict_merge(process_table, props_table)

    input_for = {
        var: tuple(common_table[i] for i in inputs)
        for var, inputs in dependencies_table.items()
    }
    new_process_table = {
        var: latest_sample(var(SimulationStep(
            x0=common_table[var],
            duration=duration,
            inputs=input_for[var]
        )))
        for var in process_table
    }

    return new_process_table


MISSING_DEPS_ERRMSG = (
    "Input dependencies for all "
    "processes must be defined. The following are missing: {}"
)


MISSING_SIGNALS_ERRMSG = (
    "The following signals are used "
    "as dependencies, but not defined as processes or properties: {}"
)


@lru_cache()
def system_from_module(name, object_name='system'):
    cfg = importlib.import_module(name)
    system = getattr(cfg, object_name)
    missing_inputs = (
        set(system.processes) - set(system.dependencies.keys())
    )
    all_deps = chain(*(deps for _, deps in system.dependencies.items()))
    all_signals = system.processes + system.properties
    missing_signals = set(all_deps) - set(all_signals)
    if missing_inputs:
        raise ValueError(MISSING_DEPS_ERRMSG.format(
            ", ".join(i.name for i in missing_inputs)
        ))
    if missing_signals:
        raise ValueError(MISSING_SIGNALS_ERRMSG.format(
            ", ".join(s.name for s in missing_signals)
        ))
    return system
