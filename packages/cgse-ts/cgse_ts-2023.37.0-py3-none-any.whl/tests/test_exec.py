import logging

import pytest

from camtest import building_block, execute
from egse.confman import is_configuration_manager_active

logger = logging.getLogger(__name__)

confman_available = True if is_configuration_manager_active() else False


@pytest.mark.skipif(not confman_available,
                    reason="requires the Configuration Manager Control Server to be available.")
def test_has_input_file():

    @building_block
    def func_one(arg_1=None):
        return arg_1

    @building_block
    def func_two(arg_1=None, arg_2=None):
        return ", ".join([str(x) for x in (arg_1, arg_2)])

    @building_block
    def func_two_star(*, arg_1, arg_2):
        return ", ".join([str(x) for x in (arg_1, arg_2)])

    @building_block
    def func_three(arg_1=None, arg_2=None, arg_3=None):
        return ", ".join([str(x) for x in (arg_1, arg_2, arg_3)])

    print()
    print(execute(func_one, arg_1=1))
    print(execute(func_one))

    print(execute(func_two))
    print(execute(func_two, arg_1=1))
    print(execute(func_two, arg_2=2))
    print(execute(func_two, arg_1=1, arg_2=2))

    print(execute(func_two_star))
    print(execute(func_two_star, arg_1=1))
    print(execute(func_two_star, arg_2=2))
    print(execute(func_two_star, arg_1=1, arg_2=2))

    with pytest.raises(ValueError):
        print(execute(func_three))
    with pytest.raises(ValueError):
        print(execute(func_three, arg_1="one"))
    with pytest.raises(ValueError):
        print(execute(func_three, arg_2="two"))
    with pytest.raises(ValueError):
        print(execute(func_three, arg_1="one", arg_2="two"))

    print(execute(func_three, arg_1="one", arg_2="two", arg_3="three"))

