#! /usr/bin/env python3
import logging

from camtest.commanding import ogse
from camtest import start_observation, end_observation
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    attenuation_level = 0.8

    setup = load_setup()

    obsid = start_observation("Switch ON the OGSE")
    print("Switching ON the OGSE..")
    ogse.ogse_swon()
    print(f"Setting attenuation level to {attenuation_level}")
    ogse.ogse_set_attenuation_level(fwc_fraction=attenuation_level)
    print(f"OGSE switched ON ({obsid=!s})")

    end_observation()
