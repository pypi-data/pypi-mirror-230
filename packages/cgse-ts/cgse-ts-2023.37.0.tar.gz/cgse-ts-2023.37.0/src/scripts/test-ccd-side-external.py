#! /usr/bin/env python3
import logging
import multiprocessing

import sys

multiprocessing.current_process().name = "test-ccd-side-external"

from egse.logger import set_all_logger_levels
set_all_logger_levels(level=logging.DEBUG)

from camtest import start_observation, end_observation
from camtest.commanding import dpu
from egse.setup import load_setup


USAGE = """
Prerequisites for running this script:

  * core services must be running
  * AEU cRIO PSU[1-7] and AWG[1-2] must be running
  * OGSE must be running and ON
  * DPU must be running

You can use the `check-system-state.py` script for checking the above.
"""


def main():

    if "-h" in sys.argv or "--help" in sys.argv:
        print(USAGE)
        return 0

    # Always load the current setup in your session

    setup = load_setup()

    start_observation("Test CCD BOTH sides on external pulses.")

    for side in "E", "F", "BOTH":
        for row_end in 99, 999, 1999, 2999, 3999, 4509, 4509+30:
            n_fee_parameters = dict(
                num_cycles=3,
                row_start=0,
                row_end=row_end,
                rows_final_dump=4510,
                ccd_order=[3, 3, 3, 3],
                ccd_side=side,
            )

            # dpu.n_cam_partial_int_sync(**n_fee_parameters)
            dpu.n_cam_partial_ccd(**n_fee_parameters)

    end_observation()


if __name__ == "__main__":
    sys.exit(main())
