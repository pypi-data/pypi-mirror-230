#! /usr/bin/env python3
import logging

from camtest import end_observation
from camtest import start_observation
from egse.dpu import DPUProxy
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    obsid = start_observation("Reset the N-CAM to it's default settings")

    dpu_dev.n_fee_reset()

    print(f"N-CAM reset ({obsid=!s})")

    end_observation()
