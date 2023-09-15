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

    obsid = start_observation("Switch the N-CAM to DUMP mode")

    try:
        dpu_dev.n_fee_set_dump_mode({})

        print(f"N-CAM switched to DUMP mode ({obsid=!s})")
    finally:
        end_observation()
