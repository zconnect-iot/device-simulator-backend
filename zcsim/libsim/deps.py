from itertools import chain
from zcsim.libsim.models import (
    SimulationStep,
    latest_sample
)

def _shallow_dict_merge(d1, d2):
    return {k: v for k,v in chain(d1.items(), d2.items())}

def one_step(process_table, props_table, dependencies_table, duration):
    common_table = _shallow_dict_merge(process_table, props_table)

    input_for = {
        var: var.fuse_inputs(*(common_table[i] for i in inputs))
        for var, inputs in dependencies_table.items()
    }
    new_process_table = {
        var: latest_sample(var(SimulationStep(
            x0=common_table[var],
            duration=duration,
            u=input_for[var]
        )))
        for var in process_table
    }

    return new_process_table
