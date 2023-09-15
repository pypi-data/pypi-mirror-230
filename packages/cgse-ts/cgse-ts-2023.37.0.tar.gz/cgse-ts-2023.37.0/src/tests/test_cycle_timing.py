from rich.console import Console

from camtest import building_block, start_observation, end_observation
from camtest.commanding import dpu

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.hexapod.symetrie.puna import PunaProxy
from egse.state import GlobalState

N_FEE_EXT_SYNC_MODE = 0
N_FEE_INT_SYNC_MODE = 1


def test_cycle_timing_low_level(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_cycle_timing_low_level")

    with DPUProxy() as dpu_proxy:

        dpu.on_frame_number_do(3, dpu_proxy.n_fee_set_standby_mode)

        # be careful, even with num_cycles=2, this method will immediately return

        dpu.on_long_pulse_do(
            dpu_proxy.n_fee_set_full_image_mode,
            n_fee_parameters={
                'num_cycles': 2, 'v_start': 200, 'v_end': 500, 'n_final_dump': 4509,
                'ccd_readout_order': 78, 'sensor_sel': 3
            }
        )

        dpu.wait_cycles(num_cycles=4)
        dpu_proxy.n_fee_set_standby_mode()
        dpu_proxy.n_fee_set_on_mode()

    end_observation()


def test_cycle_timing_int_sync_low_level(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_cycle_timing_low_level")

    with DPUProxy() as dpu_proxy:

        dpu.on_frame_number_do(3, dpu_proxy.n_fee_set_standby_mode)
        dpu.on_frame_number_do(0, dpu_proxy.n_fee_set_internal_sync, n_fee_parameters={'int_sync_period': 2000})

        dpu.on_long_pulse_do(
            dpu_proxy.n_fee_set_full_image_mode,
            n_fee_parameters={
                'num_cycles': 2, 'v_start': 200, 'v_end': 500, 'n_final_dump': 4509,
                'ccd_readout_order': 78, 'sensor_sel': 3
            }
        )

        dpu.wait_cycles(num_cycles=2)

        dpu_proxy.n_fee_set_external_sync({})
        dpu_proxy.n_fee_set_standby_mode()

        dpu.on_long_pulse_do(dpu_proxy.n_fee_set_on_mode)

    end_observation()


def test_cycle_timing_high_level(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_cycle_timing_high_level")

    dpu.on_frame_number_do(2, dpu.n_cam_to_standby_mode)

    dpu.on_long_pulse_do(
        dpu.n_cam_partial_ccd,
        num_cycles=2, row_start=200, row_end=500, rows_final_dump=4509, ccd_order=[1, 2, 3, 4], ccd_side="BOTH"
    )

    end_observation()


def test_cycle_timing_with_wait_cycles(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_cycle_timing_with_wait_cycles")

    try:
        with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

            console.log("Command internal sync mode.")
            moni.on_frame_number_do(2, dpu_proxy.n_fee_set_internal_sync, n_fee_parameters={"int_sync_period": 2000})

            for dither in range(3):
                console.log("Wait 2 cycle...")
                moni.wait_num_cycles(num_cycles=2)

                console.log("Command internal sync mode.")
                moni.on_long_pulse_do(dpu_proxy.n_fee_set_internal_sync, n_fee_parameters={"int_sync_period": 2000+dither})

            console.log("Wait 3 cycle...")
            moni.wait_num_cycles(num_cycles=3)

            for _ in range(4):
                console.log("Wait 2 cycle...")
                moni.wait_num_cycles(num_cycles=2)

                console.log("Command external sync mode.")
                moni.on_long_pulse_do(dpu_proxy.n_fee_set_external_sync, n_fee_parameters={})

            console.log("Wait 3 cycle...")
            moni.wait_num_cycles(num_cycles=3)

            console.log("Go to internal sync mode...")
            dpu_proxy.n_fee_set_internal_sync(n_fee_parameters={"int_sync_period": 3000})

            moni.on_long_pulse_do(dpu_proxy.n_fee_set_standby_mode)
            moni.wait_number_of_pulses(num_pulses=2)

    except Exception as exc:
        console.log(exc)
    finally:
        console.log(GlobalState.get_command_sequence())
        end_observation()
