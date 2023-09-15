#! /usr/bin/env python3

from typing import Dict

import sys

from camtest import camtest_logger
from camtest import end_observation
from camtest import start_observation
from camtest.commanding import dpu
from camtest.commanding.dpu import wait_cycles
from egse.dpu import DPUProxy
from egse.setup import load_setup


def expand_n_fee_parameters(pars: Dict):
    """Expand keyword arguments and their values as 'key=value' separated by comma."""
    return ", ".join(f"{k}={v}" for k, v in pars.items())


def main():

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    n_fee_parameters = dict(
        num_cycles=5,
        row_start=2000,
        row_end=4509+30,
        rows_final_dump=0,
        ccd_order=[1, 3, 2, 4],
        ccd_side="BOTH",
        ci_width=100,
        ci_gap=100,
        vgd=17
    )

    start_observation(
        f"Test Charge Injection: "
        f"n_cam_charge_injection_full({expand_n_fee_parameters(n_fee_parameters)})"
    )

    # Commanding FILL_IMAGE & DUMP mode to simulate the previous observation put us in dump mode

    if not dpu.n_cam_is_dump_mode():
        dpu.n_cam_to_standby_mode()
        dpu.n_cam_full_standard(num_cycles=0, ccd_side='BOTH')
        dpu.n_cam_to_dump_mode()

    camtest_logger.info("Commanding charge injection...")
    dpu.n_cam_charge_injection_full(**n_fee_parameters)

    end_observation()

    return 0


if __name__ == "__main__":
    sys.exit(main())
