"""
Execute this test as:

    $ cd ~/git/plato-test-scripts
    $ pytest --setup-show -s --show-capture=no src/tests/test_n_cam_partial_ccd_timing.py

"""
from rich.console import Console

from camtest import end_observation
from camtest import start_observation
from camtest.commanding import dpu
from egse.dpu import DPUProxy


def test_partial_ccd_timing_low_level(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_partial_ccd_timing_low_level")

    with DPUProxy() as dpu_proxy:

        dpu.on_frame_number_do(2, dpu_proxy.n_fee_set_standby_mode)
        # dpu.on_frame_number_do(2, dpu_proxy.n_fee_set_standby_mode)
        dpu_proxy.n_fee_set_standby_mode()

        dpu.on_long_pulse_do(
            dpu_proxy.n_fee_set_full_image_mode,
            n_fee_parameters={
                'num_cycles': 2, 'v_start': 200, 'v_end': 500, 'n_final_dump': 4509,
                'ccd_readout_order': 78, 'sensor_sel': 3
            }
        )

        dpu.wait_until_num_cycles_is_zero()

    end_observation()


def test_partial_ccd_timing_high_level(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_partial_ccd_timing_high_level")

    dpu.on_frame_number_do(2, dpu.n_cam_to_standby_mode)

    dpu.on_long_pulse_do(
        dpu.n_cam_partial_ccd,
        num_cycles=2, row_start=200, row_end=500, rows_final_dump=4509, ccd_order=[1, 2, 3, 4], ccd_side="BOTH"
    )

    end_observation()
