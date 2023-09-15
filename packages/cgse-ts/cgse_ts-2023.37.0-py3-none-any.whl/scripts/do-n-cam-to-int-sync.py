#! /usr/bin/env python3
import logging

from camtest import start_observation, end_observation
from egse.dpu import DPUProxy
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)

if __name__ == "__main__":

    from rich import print

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    obsid = start_observation("Switch the N-CAM to external sync")

    dpu_dev.n_fee_set_internal_sync({"int_sync_period": 6250})

    print(f"N-CAM switched to external sync ({obsid=!s})")

    end_observation()
