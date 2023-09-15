"""
This test starts a measurement of the N-FEE, waits for N cycles and then performs a movement of the Hexapod.

The purpose of this test is

    1. to determine N for an exact number of full cycles, and
    2. when the movement starts with respect to the timecode sync pulse
"""
from rich.console import Console

from camtest import building_block, start_observation, end_observation

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.hexapod.symetrie.puna import PunaProxy
from egse.state import GlobalState

N_FEE_EXT_SYNC_MODE = 0
N_FEE_INT_SYNC_MODE = 1


def test_move_on_long_pulse(setup_camera_access):

    console = Console()
    print()

    @building_block
    def move():
        console.log("Execute move_relative_user 0, 0, 10, 0, 0, 0.")
        puna.move_relative_user(*[0, 0, 10, 0, 0, 0])

    start_observation("pytest: test_move_on_long_pulse")

    try:
        with DPUProxy() as dpu_proxy, DPUMonitoring() as moni, PunaProxy() as puna:

            console.log("Command internal sync mode.")
            moni.on_frame_number_do(3, dpu_proxy.n_fee_set_internal_sync, n_fee_parameters={"int_sync_period": 2000})

            for dither in range(5):
                console.log("Wait 2 cycle...")
                moni.wait_num_cycles(num_cycles=2)

                console.log("Moving a mechanism...")
                moni.on_long_pulse_do(move)

            console.log("Wait 3 cycle...")
            moni.wait_num_cycles(num_cycles=3)

            console.log("Go to external sync mode...")
            dpu_proxy.n_fee_set_external_sync(n_fee_parameters={})

    except Exception as exc:
        console.log(exc)
    finally:
        console.log(GlobalState.get_command_sequence())
        end_observation()
