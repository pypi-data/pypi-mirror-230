import logging

import pytest

from camtest.core.exec import (
    building_block, get_bbid_for_func, execute, ObservationContext, generate_command_sequence
)
from egse.confman import is_configuration_manager_active
from egse.settings import Settings

LOGGER = logging.getLogger(__name__)

Settings.set_profiling(False)

from tests.helper import load_test_setup, set_bbid_yaml_filename

load_test_setup()
set_bbid_yaml_filename()


confman_available = True if is_configuration_manager_active() else False


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_plain_function():
    """Test execution of a plain function.

    A plain function is a function that is not defined as a building block. Execute can run such a function,
    but nog BBID will appear in the output nor in the execution sequence.
    """

    def not_a_building_block(msg):
        LOGGER.info(msg)

    execute(not_a_building_block, "execution of not_a_building_block()")


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_generate_command_sequence():

    @building_block
    def bb_1(msg):
        LOGGER.info(f"called bb_1({msg})")
        bb_1_1(a1=1, a2=2, a3=3)

    @building_block
    def bb_1_1(*, a1, a2, a3):
        LOGGER.info(f"called bb_1_1({a1}, {a2}, {a3})")

    @building_block
    def bb_2(msg=None):
        LOGGER.info(f"called bb_2({msg})")

    @building_block
    def ts_12345(msg):
        LOGGER.info(f"called ts_12345({msg})")
        bb_1(msg="initialise bb_1")
        bb_2(msg="move mechanism")

    generate_command_sequence(ts_12345, msg="Hello, World!")
    execute(ts_12345, msg="Hello, World!")


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_building_block_function():

    @building_block
    def empty_bb(wait_time=10):
        LOGGER.info(f"Executing function empty_bb(wait_time={wait_time}).")

    assert ObservationContext.get_level() == -1
    execute(empty_bb, wait_time=42)
    assert ObservationContext.get_level() == -1

    assert get_bbid_for_func(empty_bb) == 'BBID093F81A2BA032A19'

    # test calling the function outside of the observation context

    with pytest.raises(RuntimeError):
        empty_bb(wait_time=5)


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_recursion():

    @building_block
    def empty_bb(wait_time=10):
        LOGGER.info(f"Executing function empty_bb(wait_time={wait_time}).")

    @building_block
    def bb_2():
        bb_1()

    @building_block
    def bb_1():
        bb_2()

    with pytest.raises(ValueError):
        execute(bb_1)


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_default_arguments():

    @building_block
    def func(arg1=None, arg2=False):
        LOGGER.info(f"Executing function func1({arg1}, {arg2})")

    with pytest.raises(ValueError):
        execute(func, 3)

    with pytest.raises(ValueError):
        execute(func, arg1=3)

    execute(func, arg1=3, arg2=True)


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_func_with_some_defaults():

    @building_block
    def func_with_some_defaults(arg1=None, arg2=None, wait=None):
        LOGGER.info(f"args=({arg1}, {arg2}, {wait})")

    execute(func_with_some_defaults, arg1=1, arg2=2)
    execute(func_with_some_defaults, arg1=3, arg2=4, wait=False)


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_calling_func_with_none():

    @building_block
    def func(arg1=None, arg2=None):
        LOGGER.info(f"args=({arg1}, {arg2})")
        assert arg1 is None
        assert arg2 is not None

    execute(func, arg1=None, arg2=2)

    @building_block
    def func_with_a_none_default(arg1=None, arg2=None, wait=None):
        LOGGER.info(f"args=({arg1}, {arg2}, {wait})")
        assert arg1 is None
        assert arg2 is not None
        assert wait is True

    execute(func_with_a_none_default, arg1=None, arg2=2)


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_positional_arguments():

    @building_block
    def func1(*, arg1, arg2):
        LOGGER.info(f"Executing function func1({arg1}, {arg2})")

    @building_block
    def func2(arg1=None, arg2=None):
        LOGGER.info(f"Executing function func2({arg1}, {arg2})")

    @building_block
    def func3(arg1, arg2=None):
        LOGGER.info(f"Executing function func3({arg1}, {arg2})")

    with pytest.raises(ValueError):
        execute(func1, 1, 2)
    execute(func1, arg1=1, arg2=2)

    with pytest.raises(ValueError):
        execute(func2, 3, 4)
    execute(func2, arg1=3, arg2=4)

    with pytest.raises(ValueError):
        execute(func3, 5, 6)
    execute(func3, arg1=5, arg2=6)