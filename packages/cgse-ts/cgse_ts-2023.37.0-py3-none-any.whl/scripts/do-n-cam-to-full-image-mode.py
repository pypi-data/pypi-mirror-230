#! /usr/bin/env python3
import logging

import click

from camtest import end_observation
from camtest import start_observation
from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.logger import set_all_logger_levels
from egse.setup import load_setup

set_all_logger_levels(level=logging.WARNING)


@click.command()
@click.option('--num_cycles', default=0, help="The number of cycles in this mode")
@click.option('--int_sync', is_flag=True, help="Use internal sync mode")
def cli(num_cycles, int_sync):

    from rich import print

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    obsid = start_observation(f"Switch the N-CAM to FULL-IMAGE mode with {num_cycles=}, {int_sync=}")

    if int_sync:
        dpu_dev.n_fee_set_full_image_mode_int_sync(
            n_fee_parameters=dict(num_cycles=num_cycles, v_start=0, v_end=4509)
        )
    else:
        dpu_dev.n_fee_set_full_image_mode(
            n_fee_parameters=dict(num_cycles=num_cycles, v_start=0, v_end=4509)
        )

    if num_cycles == 0:
        print(f"N-CAM switched to FULL-IMAGE mode ({obsid=!s})")
    else:
        try:
            with DPUMonitoring() as moni:
                moni.wait_until_synced_num_cycles_is_zero()
        except TimeoutError as exc:
            print(f"[red]{exc}[/red]")

    end_observation()


if __name__ == "__main__":
    cli()
