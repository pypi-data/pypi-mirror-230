from egse.state import GlobalState

from egse.logger import create_new_zmq_logger

from .core import execute
from .core import building_block
from .core import generate_command_sequence
from .core import list_setups
from .core import load_setup
from .core import get_setup
from .core import submit_setup

# Allow importing start_ and end_observation from camtest,
# but don't automatically import
from .core.exec import start_observation
from .core.exec import end_observation

from .commanding import dpu

# We want all the PLATO test scripts to log their messages under camtest

camtest_logger = create_new_zmq_logger("camtest")


__all__ = [

    # imported from common-egse

    "GlobalState",

    # imported from camtest.core

    "execute",
    "building_block",
    "generate_command_sequence",
    "list_setups",
    "load_setup",
    "get_setup",
    "submit_setup",

    # imported from camtest.commanding

    "dpu",

    # The logger to be used for PLATO test scripts

    "camtest_logger",
]
