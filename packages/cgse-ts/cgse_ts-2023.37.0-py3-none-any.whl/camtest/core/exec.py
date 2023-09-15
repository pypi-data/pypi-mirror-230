"""
This module defines the building blocks in the PLATO Test Scripts.

Definitions:

    Building Block:
        a building block is a function that can only be executed within the context
        of an observation. Building blocks can be nested, but can not be called recursively.

    Observation:
        an observation is a single block of execution.
        All tests defined in the test specification are observations.
        Observations can not be nested and there can only be one observation running at any time.

Functions:

    @building_block - decorator: defines a function as a building block
    execute - top-level function that executes a test/observation
    generate_command_sequence - top-level function that generates a string representation
        of the commands to be executed
"""
import functools
import logging
from collections import deque
from collections import namedtuple
from inspect import signature
from typing import Callable

from camtest.core.bbid import get_bbid_for_func
from egse.config import find_file
from egse.config import find_root
from egse.confman import ConfigurationManagerProxy
from egse.control import Failure
from egse.control import Success
from egse.decorators import profile
from egse.settings import Settings
from egse.state import GlobalState
from egse.system import get_caller_info

LOGGER = logging.getLogger(__name__)


def has_input_file():
    """
    Checks if the building_block has a YAML input file and returns True if the input file exists,
    False otherwise.

    This function must be called from within the building_block itself.
    """
    func_name = get_caller_info(level=2).function
    input_name = find_file(
        f"{func_name}.yaml", in_dir="input", root=find_root(__file__, tests=("LICENSE",))
    )

    return True if input_name else False


def read_input_file():
    func_name = get_caller_info(level=2).function
    input_name = find_file(
        f"{func_name}.yaml", in_dir="input", root=find_root(__file__, tests=("LICENSE",))
    )

    return Settings.load("Args", filename=input_name)


class ObservationContext:
    """Keep record of the observation context."""

    level = -1
    bbid_count = 0
    bbids = deque()

    @classmethod
    def set_bbid(cls, bbid: int):
        """Set the current building block id."""
        if bbid in cls.bbids:
            raise ValueError(
                f"This building block ({bbid}) is already in execution, check dependencies "
                f"between building blocks."
            )
        if cls.level == -1:
            raise RuntimeError(
                f"This building block ({bbid}) is called outside the scope of an "
                f"observation context."
            )

        cls.bbids.append(bbid)
        cls.bbid_count += 1
        cls.level += 1

    @classmethod
    def unset_bbid(cls):
        """Unset the current building block id and go back to the previous level and bbid."""
        cls.bbids.pop()
        cls.level -= 1

    @classmethod
    def get_current_bbid(cls):
        return cls.bbids[-1]

    @classmethod
    def get_level(cls):
        return cls.level

    @classmethod
    def start_observation(cls, function_info: dict):
        if cls.level == -1:
            cls.level = 0
        else:
            raise Failure(f"An observation can only be started when no observation is running.")

        try:
            with ConfigurationManagerProxy() as cm:
                rc = cm.start_observation(function_info)
                if not rc.successful:
                    cls.level = -1
                    raise rc
                else:
                    return rc.return_code
        except ConnectionError as exc:
            cls.level = -1
            raise Failure("Couldn't connect to the Configuration Manager Control Server", exc)

    @classmethod
    def end_observation(cls):
        if cls.level > 0 or cls.bbids:
            LOGGER.warning(
                f"Observation contexts not empty at time of reset! (Level={cls.level}, "
                f"bbids={cls.bbids})"
            )
        cls.level = -1
        cls.bbid_count = 0
        cls.bbids.clear()

        with ConfigurationManagerProxy() as cm:
            rc = cm.end_observation()
            if not rc.successful:
                raise rc


@profile
def start_building_block(func: Callable, *args, **kwargs) -> int:
    """Start a commanding building block."""

    # * define a unique building block identifier
    # * return the building block identifier

    bbid = get_bbid_for_func(func)
    if GlobalState.dry_run:
        BuildingBlockStart = namedtuple(
            "BuildingBlockStart", ["level", "bbid", "name", "args", "kwargs"]
        )
        level = ObservationContext.get_level()
        GlobalState.add_command(BuildingBlockStart(level, bbid, func.__name__, args, kwargs))
    ObservationContext.set_bbid(bbid)
    return bbid


@profile
def end_building_block():
    """End a commanding building block."""
    ObservationContext.unset_bbid()
    if GlobalState.dry_run:
        BuildingBlockEnd = namedtuple("BuildingBlockEnd", ["level"])
        level = ObservationContext.get_level()
        GlobalState.add_command(BuildingBlockEnd(level))


def building_block(func: Callable) -> Callable:
    """
    Define the function `func` as a building block.

    Args:
        func: the function that is defined as a building block

    Returns:
        wrapper: wrapper around `func`
    """
    # LOGGER.debug(f"decorating: {func.__name__}")
    setattr(func, "BUILDING_BLOCK_FUNC", True)

    input_file_name = find_file(
        f"{func.__name__}.yaml", in_dir="input", root=find_root(__file__, tests=("LICENSE",))
    )

    # LOGGER.debug(f"{__file__=}")

    if input_file_name:
        setattr(func, "HAS_INPUT_FILE", True)
        func.INPUT_FILE_NAME = input_file_name
        # LOGGER.debug(f"{input_file_name=}")
    else:
        setattr(func, "HAS_INPUT_FILE", False)
        func.INPUT_FILE_NAME = None
        # LOGGER.debug(f"{input_file_name=}")

    def check_kwargs(**kwargs):
        sig = signature(func)
        missing = [par.name for par in sig.parameters.values() if par.name not in kwargs]
        # LOGGER.debug(f"missing={missing}")
        if missing:
            raise ValueError(
                f"Expected {len(sig.parameters)} keyword parameters for "
                f"building block {func.__name__}, missing arguments are {missing}."
            )

    def rewrite_kwargs(**kwargs):
        if func.HAS_INPUT_FILE:
            args = Settings.load("Args", filename=func.INPUT_FILE_NAME)
            args.update({k: None for k, v in args.items() if v == "None"})

            #
            kwargs = {k: v if v is not None else args[k] for k, v in kwargs.items()}
            # LOGGER.debug(f"kwargs={kwargs}")
            kwargs.update({k: v for k, v in args.items() if k not in kwargs.keys()})
            # LOGGER.debug(f"kwargs={kwargs} (updated)")

        # LOGGER.debug(f"{func.__name__}({kwargs})")
        return kwargs

    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):

        # Take steps to make the function `func` into a building block.
        #
        # * set its building block id based on the name of the function
        # * check if this building block is executed within the scope of an observation
        # * execute the function `func`

        # TODO: We should also check for args, there can be no args!!

        if args:
            raise ValueError(
                f"Building block {func.__name__} can not have positional arguments. "
                f"The following arguments {args} should be given as keyword arguments."
            )

        kwargs = rewrite_kwargs(**kwargs)
        check_kwargs(**kwargs)

        start_building_block(func, *args, **kwargs)

        try:
            result = func(*args, **kwargs)
        finally:
            # Take steps to end the building block
            end_building_block()

        return result

    return wrapper_func


def request_obsid():
    """Requests an `obsid` from the configuration manager.

    Returns:
        the current observation identifier.

    Raises:
        Failure with message and cause.
    """
    with ConfigurationManagerProxy() as cm:
        rc = cm.get_obsid()
        if isinstance(rc, Success):
            return rc.return_code

    raise rc


def stringify_args(args):

    s_args = []
    for arg in args:
        try:
            s_args.append(f"{arg.__module__}.{arg.__class__.__qualname__}")
        except AttributeError:
            s_args.append(repr(arg))

    return s_args


def stringify_kwargs(kwargs):

    s_kwargs = {}
    for k, v in kwargs.items():
        try:
            s_kwargs[k] = f"{v.__module__}.{v.__class__.__qualname__}"
        except AttributeError:
            s_kwargs[k] = repr(v)

    return s_kwargs


def execute(func: Callable, description=None, *args, **kwargs):
    """Execute a building block or observation."""

    try:
        ObservationContext.start_observation(
            {
                "func_name": func.__name__,
                "description": description,
                "args": stringify_args(args),
                "kwargs": stringify_kwargs(kwargs),
            }
        )

        obsid = request_obsid()
        LOGGER.info(f"OBSID = {obsid}")

    except (Failure, TypeError) as exc:
        LOGGER.error(f"Failed to start observation or test: {exc}")
        raise exc

    # can I check here if func is indeed a building_block?

    if not hasattr(func, "BUILDING_BLOCK_FUNC"):
        LOGGER.warning('Executing a function that is not a building block.')

    try:
        response = func(*args, **kwargs)
    finally:
        ObservationContext.end_observation()

    return response


def generate_command_sequence(func: Callable, *args, **kwargs):

    GlobalState.dry_run = True
    GlobalState.clear_command_sequence()

    try:
        execute(func, *args, **kwargs)
    except Exception:
        raise
    finally:
        command_sequence = GlobalState.get_command_sequence()

        indent = "    "
        level = 0

        for cmd in command_sequence:
            if isinstance(cmd, tuple) and hasattr(cmd, "level"):
                level = cmd.level
            print(f"{indent*level}{cmd}")

        GlobalState.dry_run = False
        GlobalState.clear_command_sequence()


def start_observation(description: str):
    try:
        ObservationContext.start_observation({"description": description})

        obsid = request_obsid()
        LOGGER.info(f"Observation started with obsid={obsid}")

    except Failure as exc:
        LOGGER.error(f"Failed to start observation or test: {exc}")
        raise exc

    return obsid


def end_observation():
    ObservationContext.end_observation()
