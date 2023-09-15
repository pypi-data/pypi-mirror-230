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

    obsid = start_observation("Switch ON the N-CAM")

    print("Switching ON the N-CAM..", end="")

    aeu.n_cam_swon()

    while not aeu.n_cam_is_on():
        time.sleep(3.0)
        print(".", end="", flush=True)

    print()
    print("Enable synchronisation on N-CAM..", end="")

    aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

    while not aeu.n_cam_is_syncing():
        time.sleep(3.0)
        print(".", end="", flush=True)

    print()
    print(f"N-CAM switched ON and syncing ({obsid=!s})")
    end_observation()
