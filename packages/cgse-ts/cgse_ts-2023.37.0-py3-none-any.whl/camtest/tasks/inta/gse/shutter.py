import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "Shutter SC10"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

def values_shutter() -> List:
    return [False, True,]

def default_shutter() -> int:
    return 0


@exec_ui(display_name="Set Value", use_kernel=True,
         icons=(ICON_PATH / "shutter.svg", ICON_PATH / "shutter-selected.svg"))
def enabled_shutter(ChangeStatus: Callback(values_shutter, name=List, default=default_shutter)):
    """
    This function enabled or disabled a Shutter SC10.
    """
    start_observation("Set enabled the Shutter")
    try:
        with GlobalState.setup.gse.shutter.device as shutter:
            status = shutter.get_enable()    
            if(ChangeStatus == status):
               print(f"[green]Shutter is {ChangeStatus}.[/]", flush=True)
            else:
                shutter.toggle_enable()
                status = shutter.get_enable()    
                if(ChangeStatus == status):
                    print(f"[green]Shutter is {ChangeStatus}.[/]", flush=True)
                else:
                    print(f"[red]ERROR: The Shutter not change now it's in {status} position.[/]")
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Shutter Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_shutter():
    """This function prints a table with the status of the Shutter SC10."""
    from rich.console import Console
    from rich.table import Table
    try:
        with GlobalState.setup.gse.shutter.device as shutter:
            status = shutter.get_enable()
            table = Table(title="Shutter Status Report")

            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            table.add_row("Shutter Status", str(status))

            console = Console(width=80)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Shutter.[/]")