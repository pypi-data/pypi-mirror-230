#! /usr/bin/env python3

from typing import Dict

import click
import sys

from camtest.commanding import dpu
from camtest import start_observation, end_observation
from egse.dpu import DPUProxy
from egse.setup import load_setup


def expand_n_fee_parameters(pars: Dict):
    """Expand keyword arguments and their values as 'key=value' separated by comma."""
    return ", ".join(f"{k}={v}" for k, v in pars.items())


@click.command()
@click.option('--num_cycles', default=5, help="The number of cycles in this mode")
def main(num_cycles):

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=999,
        rows_final_dump=4510,
        ccd_order=[4, 3, 2, 1],
        ccd_side="BOTH",
        exposure_time=10.0,
    )

    start_observation(
        f"Taking a reference image: "
        f"n_cam_partial_int_sync({expand_n_fee_parameters(n_fee_parameters)})"
    )

    dpu_dev.n_fee_set_clear_error_flags()

    dpu.n_cam_partial_int_sync(**n_fee_parameters)

    end_observation()

    return 0


if __name__ == "__main__":
    sys.exit(main())
