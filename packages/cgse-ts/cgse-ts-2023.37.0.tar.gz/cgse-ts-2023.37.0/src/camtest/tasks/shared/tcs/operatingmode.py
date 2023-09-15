import time
from pathlib import Path

from gui_executor.exec import exec_ui
from rich import print
from rich.console import Console
from rich.table import Table


from camtest import end_observation
from camtest import start_observation
from egse.control import Failure
from egse.state import GlobalState
from egse.tcs import OperatingMode
from egse.tcs.tcs import TCSInterface
from egse.tcs.tcs import is_tcs_cs_active

UI_MODULE_DISPLAY_NAME = "4 - Operating Mode"

ICON_PATH = Path(__file__).parent.resolve() / "icons"


@exec_ui(display_name="Set Operating Mode")
def set_operating_mode(mode: OperatingMode):
    """ Set the TCS operating mode.

    Potential operating modes are:
        - Normal mode
        - Safe mode
        - Decontamination mode
        - Calibration mode
        - EMC mode
        - Self-test mode
        - Extended mode

    Args:
        - mode: Operating mode to switch to.
    """

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if not tcs_dev.is_remote_operation_active():
        print("[red]Remote Mode is not activated, activate it before proceeding.[/]")
        return

    obsid = start_observation(f"Set the operating mode to {mode.name}")
    print(f"Observation started: {obsid}")

    print("1: ", tcs_dev.stop_task())
    print("... waiting 5s")
    time.sleep(5.0)  # empirically determined sleep time of 5s
    print("2: ", tcs_dev.set_operating_mode(mode=mode))
    print("3: ", tcs_dev.run_task())

    end_observation()

    print(f"TCS set to {mode.name} mode")


@exec_ui(display_name="Retrieve Configuration", immediate_run=True)
def get_configuration():
    """ Print the last valid configuration as a table."""

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    response = tcs.get_configuration()

    if isinstance(response, Failure):
        print(f"[red bold]{response}[/]")
        return

    table = Table(title="TCS Configuration Parameters")

    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="green")

    for name, value in sorted(response.items()):
        table.add_row(name, value)

    console = Console(width=120)
    console.print(table)
