"""
Execute this test as:

    $ cd ~/git/plato-test-scripts
    $ pytest --setup-show -s --show-capture=no src/tests/test_n_cam_sync_mode.py

"""

import time

from rich.console import Console
from camtest import start_observation, end_observation
from camtest.commanding import dpu


def test_n_cam_sync_mode(setup_camera_access):

    console = Console()
    print()

    start_observation("pytest: test_n_cam_sync_mode")

    console.log("N-CAM to STANDBY mode...")

    dpu.n_cam_to_standby_mode()

    assert dpu.n_cam_is_ext_sync(), "Expected N-CAM in external sync mode"

    while not dpu.n_cam_is_standby_mode():
        time.sleep(1.0)

    console.log("N-CAM to DUMP mode internal sync on FN 3...")
    dpu.on_frame_number_do(3, dpu.n_cam_to_dump_mode_int_sync)

    dpu.wait_for_timecode()

    assert dpu.n_cam_is_int_sync(), "Expected N-CAM in external sync mode"

    console.log("N-CAM to STANDBY mode...")
    dpu.n_cam_to_standby_mode()
    dpu.wait_for_long_pulse()

    end_observation()
