import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "FilterWheel FS8SM4"
ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

def wheel_1_moves() -> List:
    try:
        return GlobalState.setup.gse.filterwheel.positions_wheel_1
    except AttributeError:
        return [0, 1, 2, 3, 4, 5, 6, 7]

def wheel_2_moves() -> List:
    try:
        return GlobalState.setup.gse.filterwheel.positions_wheel_2
    except AttributeError:
        return [0, 1, 2, 3, 4, 5, 6, 7]

def default_factor_wheel() -> int:
    return 0


@exec_ui(display_name="Homing", use_kernel=True,
         icons=(ICON_PATH / "filter-wheel-homing.svg", ICON_PATH / "filter-wheel-homing-selected.svg"))
def home_filterwheel():
    """
    This function performs a Homing of the Filter Wheel and waits until the Homing is finished.
    """
    start_observation("Homing the Filter Wheel")

    try:
        with GlobalState.setup.gse.filterwheel.device as filterwheel:
            filterwheel.homing()
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Filter Wheel Server, check in the PM GUI if it's running.[/]")
    else:
        print("[green]Filter Wheel has now been homed.[/]", flush=True)

    end_observation()



@exec_ui(display_name="Move Filter Wheel",
         icons=(ICON_PATH / "filter-wheel-move.svg", ICON_PATH / "filter-wheel-move-selected.svg"))
def move_filter_wheel(wheel1: Callback(wheel_1_moves, name=List, default=default_factor_wheel),
                      wheel2: Callback(wheel_2_moves, name=List, default=default_factor_wheel)):
    """This function sets the positions on wheel 1 and whewl 2 in the Filter Wheel.

    Args:
        Wheel 1 (List): Move position [1 - 8]
        Wheel 2 (List): Move position [1 - 8]

    """
    start_observation(f"Set Move wheel 1 to {wheel1} and Wheel 2 to {wheel2}")
    try:
        with GlobalState.setup.gse.filterwheel.device as filter_wheel:
            filter_wheel.set_position(pos_wheel1=wheel1, pos_wheel2=wheel2)
            time.sleep(2.0)
            while filter_wheel.get_status()[1] != 0:
                time.sleep(0.3)
            setup = GlobalState.setup
            fw_value = 0
            setup_relat = setup.gse.ogse.calibration.relative_intensity_by_wheel
            relat_int = sorted(list(setup_relat.keys()))
            for key in relat_int:
                if (int(key[1]) == wheel1 and int(key[4]) == wheel2):
                    fw_value = setup_relat.get_raw_value(key)
                    break
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Filter Wheel, check if the Filter Wheel Control Server is running.[/]")
    else:
        print(f"[green]Filter Wheel has now in Pos 1:{wheel1} and Pos 2: {wheel2} and the fw_value: {fw_value}.[/]", flush=True)

    end_observation()




@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_filterwheel():
    """This function prints a table with the status of the Filter Wheel."""
    from rich.console import Console
    from rich.table import Table
    try:
        with GlobalState.setup.gse.filterwheel.device as filter_wheel:
            status = filter_wheel.get_status()
            position = filter_wheel.get_position()
            parameters = ["Position(Steps)", "Wheel Speed", "Temperature(ºC)", "Engine Current(mA)", "Power Supply Voltage(V)", "Status Flag"]
            table = Table(title="Filter Wheel Status Report")

            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            for par, value in zip(parameters, status):
                table.add_row(str(par), str(value))
            table.add_row("Pos Wheel 1", str(position[0]))
            table.add_row("Pos Wheel 2", str(position[1]))

            console = Console(width=80)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Filter Wheel.[/]")