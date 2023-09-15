import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "Lamp EQ99"
ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

def values_lamp() -> List:
    return [False, True]

def default_lamp() -> int:
    return 0


@exec_ui(display_name="Set Value", use_kernel=True,
         icons=(ICON_PATH / "lamp.svg", ICON_PATH / "lamp-selected.svg"))
def enabled_lamp(ChangeStatus: Callback(values_lamp, name=List, default=default_lamp)):
    """
    This function enabled or disabled a Lamp EQ99.
    """
    start_observation("Set Lamp Status")
    try:
        with GlobalState.setup.gse.lamp.device as lamp:
            lamp.set_lamp(ChangeStatus)
            status = lamp.get_lamp()    
            if(ChangeStatus == status):
               print(f"[green]Lamp is {status}.[/]", flush=True)
            else:
                print(f"[red]ERROR: The Lamp not change now it's in {status} position.[/]")
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Lamp Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_lamp():
    """This function prints a table with the status of the Lamp EQ99."""
    from rich.console import Console
    from rich.table import Table
    try:
        with GlobalState.setup.gse.lamp.device as lamp:
            status = lamp.get_lamp()
            time = lamp.get_lamp_time()
            table = Table(title="Lamp Status Report")

            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            table.add_row("Lamp Status", str(status))
            table.add_row("Lamp Time (in hours)", str(time))

            console = Console(width=80)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Lamp.[/]")