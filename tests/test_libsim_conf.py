from zcsim.libsim.run import (
    system_from_module,
)
from tests.system import (
    system as test_system,
    incomplete_system as incomplete_test_system
)
import pytest


def test_all_processes_should_have_inputs():
    system = system_from_module('tests.system')
    assert set(system['processes']) == set(system['dependencies'].keys())


def test_error_raised_when_insufficient_inputs_defined():
    with pytest.raises(ValueError):
        system_from_module('tests.system', 'incomplete_system')


def test_undefined_inputs_should_be_listed_in_error_msg():
    missing_inputs = set(test_system['dependencies'].keys()) - \
        set(incomplete_test_system['dependencies'].keys())
    try:
        system_from_module('tests.system', 'incomplete_system')
    except ValueError as e:
        assert all(i.name in str(e) for i in missing_inputs)
