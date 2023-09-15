"""
Functions that work with building block ids.
"""
import hashlib
import logging
from pathlib import Path
from typing import Callable

import yaml

from egse.config import find_file, find_root
from egse.settings import Settings

logger = logging.getLogger(__name__)

bbid_yaml_filename = find_file("bbid.yaml", root=str(Path(__file__).parent))

bbid_values = Settings.load("BBID", filename=str(bbid_yaml_filename))


def get_bbid_for_func(func: Callable) -> int:
    """Returns the building block identifier for the given function"""
    if not isinstance(func, Callable):
        raise ValueError("The given argument should be a function or method.")
    bb_name = _generate_bbid_name_for_func(func)
    try:
        bbid = bbid_values[bb_name]
    except KeyError:
        bbid_values[bb_name] = bbid = _generate_bbid_for_func(func)
        logger.info(
            f"Unknown building block ({bb_name}), defining and saving BBID ({bbid}) "
            f"in BBID YAML file."
        )
        _save_bbid_settings()
    return bbid


def _generate_bbid_name_for_func(func: Callable):
    func_name = func.__name__
    func_module = func.__module__
    bb_name = f"{func_name}".upper()
    return bb_name


def _generate_bbid_for_func(func: Callable):
    bb_name = _generate_bbid_name_for_func(func)
    return "BBID" + hashlib.md5(bb_name.encode()).hexdigest()[:16].upper()


def _save_bbid_settings():
    logger.info(f"Saving BBID {bbid_values}")

    with Path(bbid_yaml_filename).open("w") as stream:
        yaml.safe_dump({"BBID": dict(bbid_values)}, stream)
