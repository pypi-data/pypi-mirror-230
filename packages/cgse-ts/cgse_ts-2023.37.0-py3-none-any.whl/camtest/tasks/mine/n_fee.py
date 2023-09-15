from typing import Dict

from camtest import start_observation, end_observation
from camtest.commanding import dpu

from egse.dpu import DPUProxy
from egse.setup import load_setup

from gui_executor.exec import exec_task


def expand_n_fee_parameters(pars: Dict):
    """Expand keyword arguments and their values as 'key=value' separated by comma."""
    return ", ".join(f"{k}={v}" for k, v in pars.items())


@exec_task()
def do_reference_image(num_cycles: int = 5, ccd_order: tuple = (1, 2, 3, 4)):

    setup = load_setup()

    dpu_dev: DPUProxy = setup.camera.dpu.device

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4509+30,
        rows_final_dump=0,
        ccd_order=ccd_order,
        ccd_side="BOTH",
    )

    start_observation(
        f"Taking a reference image: "
        f"n_cam_partial_ccd({expand_n_fee_parameters(n_fee_parameters)})"
    )

    dpu_dev.n_fee_set_clear_error_flags()

    dpu.n_cam_partial_ccd(**n_fee_parameters)

    end_observation()

    return 0
