#! /usr/bin/env python3
import logging

from camtest.commanding import ogse
from camtest import start_observation, end_observation
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    setup = load_setup()

    obsid = start_observation("Switch OFF the OGSE")
    print("Switching OFF the OGSE..")
    ogse.ogse_swoff()
    print(f"OGSE switched OFF ({obsid=!s})")
    end_observation()
