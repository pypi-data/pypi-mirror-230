#! /usr/bin/env python3

from typing import Dict

import sys

from camtest import camtest_logger
from camtest import end_observation
from camtest import start_observation
from camtest.commanding import dpu
from egse.dpu import DPUProxy
from egse.setup import load_setup


def expand_n_fee_parameters(pars: Dict):
    """Expand keyword arguments and their values as 'key=value' separated by comma."""
    return ", ".join(f"{k}={v}" for k, v in pars.items())


def main():

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    n_fee_parameters = dict(
        num_cycles=3,
        clock_dir_serial="REV",
        ccd_order=[1, 2, 3, 4],
        ccd_side="BOTH",
    )

    start_observation(
        f"Test Reverse Clocking: "
        f"n_cam_reverse_clocking({expand_n_fee_parameters(n_fee_parameters)})"
    )

    # Commanding FILL_IMAGE & DUMP mode to simulate the previous observation put us in dump mode

    if not dpu.n_cam_is_dump_mode():
        dpu.n_cam_to_standby_mode()
        dpu.n_cam_full_standard(num_cycles=0, ccd_side='BOTH')
        dpu.n_cam_to_dump_mode()

    camtest_logger.info("Commanding reverse clocking...serial direction REV")
    dpu.n_cam_reverse_clocking(**n_fee_parameters)

    n_fee_parameters = dict(
        num_cycles=3,
        clock_dir_serial="FWD",
        ccd_order=[1, 2, 3, 4],
        ccd_side="BOTH",
    )

    camtest_logger.info("Commanding reverse clocking...serial direction FWD")
    dpu.n_cam_reverse_clocking(**n_fee_parameters)

    camtest_logger.info("Ending observation.")
    end_observation()

    return 0


if __name__ == "__main__":
    sys.exit(main())
