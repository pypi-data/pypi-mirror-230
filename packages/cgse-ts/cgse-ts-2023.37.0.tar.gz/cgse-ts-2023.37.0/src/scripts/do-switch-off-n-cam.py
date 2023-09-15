#! /usr/bin/env python3
import logging
import time

from camtest.commanding import aeu
from camtest import start_observation, end_observation
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    setup = load_setup()

    obsid = start_observation("Switch OFF the N-CAM")

    print("Disable syncing for N-CAM..", end="")

    aeu.n_cam_sync_disable()

    while aeu.n_cam_is_syncing():
        time.sleep(3.0)
        print(".", end="", flush=True)

    print()
    print("Switching OFF the N-CAM..", end="")

    aeu.n_cam_swoff()

    while aeu.n_cam_is_on():
        time.sleep(3.0)
        print(".", end="", flush=True)

    print()
    print(f"N-CAM switched OFF ({obsid=!s})")

    end_observation()
