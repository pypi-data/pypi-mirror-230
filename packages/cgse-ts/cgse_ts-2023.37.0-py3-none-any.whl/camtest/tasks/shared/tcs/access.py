import time
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table

from gui_executor.exec import exec_ui

from camtest import end_observation
from camtest import start_observation
from egse.control import Failure
from egse.state import GlobalState
from egse.tcs import OperatingMode
from egse.tcs.tcs import TCSInterface
from egse.tcs.tcs import is_tcs_cs_active

UI_MODULE_DISPLAY_NAME = "2 - Accessibility"

ICON_PATH = Path(__file__).parent.resolve() / "icons"


@exec_ui(immediate_run=True, display_name="Stop TCS EGSE",
         icons=(ICON_PATH / "stop.svg", ICON_PATH / "stop.svg")
         )
def stop_tcs():
    """ Stop the TCS EGSE and switch to CALIBRATION mode.

    When remote control is not active, it will be activated automatically.

    This is a TCS emergency switch-off in case of an out-gassing event.
    """

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    tcs_dev.request_remote_operation()
    if not tcs_dev.is_remote_operation_active():
        print("[red]ERROR: Remote mode could not be activated, cannot STOP the TCS EGSE![/]")
        return

    obsid = start_observation("Stop the TCS regulation by switching mode to Calibration")
    print(f"Observation started: {obsid}")

    print("1: ", tcs_dev.stop_task())
    print("... waiting 5s")
    time.sleep(5.0)  # empirically determined sleep time of 5s
    print("2: ", tcs_dev.set_operating_mode(mode=OperatingMode.CALIBRATION))
    print("3: ", tcs_dev.run_task())

    end_observation()

    print("TCS set to CALIBRATION mode")


@exec_ui(display_name="Start Remote Mode", immediate_run=True)
def start_remote_mode():
    """ Activate the remote mode in the TCS EGSE.
    """

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if tcs_dev.is_remote_operation_active():
        print("Remote Mode already activated.")
        return

    tcs_dev.request_remote_operation()
    print("[green]Remote Mode activated.[/]")


@exec_ui(display_name="Stop Remote Mode", immediate_run=True)
def stop_remote_mode():
    """ De-activate the remote mode in the TCS EGSE."""

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if not tcs_dev.is_remote_operation_active():
        print("Remote Mode already de-activated.")
        return

    tcs_dev.quit_remote_operation()
    print("Remote Mode de-activated.")
