import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "Powermeter PM100"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_powermeter():
    """This function prints a table with the status of the Powermeter."""
    from rich.console import Console
    from rich.table import Table
    try:
        with GlobalState.setup.gse.powermeter.device as powermeter:
            table = Table(title="Powermeter Status Report")            
            value = powermeter.get_value()
            average = powermeter.get_average()
            wavelength = powermeter.get_wavelength()
            range = powermeter.get_range()
            diametre = powermeter.get_diameter()
            autozero = powermeter.get_autozero()
            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            table.add_row("Value", str(value))
            table.add_row("Average", str(average))
            table.add_row("Wavelength", str(wavelength))
            table.add_row("Range", str(range))
            table.add_row("Diametre", str(diametre))
            table.add_row("Autozero", str(autozero))

            console = Console(width=80)
            print(powermeter.info())

            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Powermeter.[/]")