from tests.system import (
    angular_velocity,
    angular_velocity_tau,
    input_current,
    engine_efficiency,
    load,
    deps,
)

from libsim.run import (
    one_step,
)

import numbers

def test_all_keys_present():
    """
    New value table should only have state variable keys
    """
    process_table = {
        angular_velocity: 300,
        input_current: 3
    }
    user_table = {
        load: 2,
        engine_efficiency: 70
    }
    new_process_table = one_step(
        process_table, user_table, deps, 5*angular_velocity_tau
    )

    assert set(new_process_table.keys()) == set(process_table.keys())
    print(new_process_table)

def test_new_process_table_each_key_stores_one_float():
    """
    Every key in the process table should have just one numeric value
    """
    process_table = {
        angular_velocity: 300,
        input_current: 3
    }
    user_table = {
        load: 2,
        engine_efficiency: 70
    }
    new_process_table = one_step(
        process_table, user_table, deps, 5*angular_velocity_tau
    )
    print(new_process_table)

    assert all(isinstance(v, numbers.Number)
               for _,v in new_process_table.items())
