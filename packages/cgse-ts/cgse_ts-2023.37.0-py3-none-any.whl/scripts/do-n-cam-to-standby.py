#! /usr/bin/env python3
import logging
import time

from camtest.commanding import aeu
from camtest import start_observation, end_observation
from egse.dpu import DPUProxy
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    obsid = start_observation("Switch the N-CAM to STANDBY mode")

    dpu_dev.n_fee_set_standby_mode()

    print(f"N-CAM switched to STANDBY mode ({obsid=!s})")

    end_observation()
