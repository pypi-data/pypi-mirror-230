from pathlib import Path

from gui_executor.exec import exec_ui
from rich import print

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState
from egse.tcs.tcs import TCSInterface

UI_MODULE_DISPLAY_NAME = "3 - Tasks"

ICON_PATH = Path(__file__).parent.resolve() / "icons"


@exec_ui(display_name="Start Task", immediate_run=True)
def start_task():
    """ Store previously sent configuration parameters and run the task."""

    obsid = start_observation("Start a task on the TCS EGSE.")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    response = tcs.run_task()
    if response == "acknowledge_start":
        print("[green]Successfully started task[/]")
    else:
        print(f"[red]ERROR: {response}[/]")

    end_observation()


@exec_ui(display_name="Stop Task", immediate_run=True)
def stop_task():
    """ Stop the current running task (test, self-test, etc)."""

    obsid = start_observation("Stop a running task on the TCS EGSE.")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    response = tcs.stop_task()
    if response == "acknowledge_stop":
        print("[green]Successfully stopped running task[/]")
    else:
        print(f"[red]ERROR: {response}[/]")

    end_observation()
