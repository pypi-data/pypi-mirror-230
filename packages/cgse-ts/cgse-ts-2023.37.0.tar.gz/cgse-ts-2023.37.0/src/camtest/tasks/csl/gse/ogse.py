import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "1 — OGSE"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons/"


@exec_ui(display_name="Switch ON",
         icons=(ICON_PATH / "ogse-swon.svg", ICON_PATH / "ogse-swon-selected.svg"))
def switch_on_ogse():
    """ OGSE switch-on.

    This task will power on the OGSE as follows:

      * The power supply for the light source will be switched on,
      * the attenuation factor will be set to 0, i.e. blocking the light source,
      * the lamp and the laser will be switched on.

    The task will take between five and twenty seconds.

    Note that after the lamp is switched on, it takes ±30 minutes for the light source to stabilise.
    """

    start_observation("Switch ON the OGSE: attenuation set to 0 = blocking")

    try:
        with GlobalState.setup.gse.ogse.device as ogse:
            ogse.power_on()
            ogse.att_set_level_factor(factor=0)
            time.sleep(5)
            ogse.operate_on()
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the OGSE.[/]")

    end_observation()


@exec_ui(display_name="Switch OFF",
         icons=(ICON_PATH / "ogse-swoff.svg", ICON_PATH / "ogse-swoff-selected.svg"))
def switch_off_ogse():
    """ OGSE switch-off.

    This task will power off the OGSE as follows:

      * The lamp and the laser will be switched off,
      * the attenuation factor will be set to 0, i.e. blocking the light source,
      * the power supply unit will be switched off.
    """
    start_observation("Switch OFF the OGSE")

    try:
        with GlobalState.setup.gse.ogse.device as ogse:
            ogse.operate_off()
            ogse.att_set_level_factor(factor=0)
            ogse.power_off()
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the OGSE.[/]")

    end_observation()


def attenuation_factors() -> List:
    try:
        return list(GlobalState.setup.gse.ogse.calibration.relative_intensity_by_index.values())
    except AttributeError:
        return [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def default_factor() -> float:
    return 1.0


@exec_ui(display_name="Set Attenuation",
         icons=(ICON_PATH / "filter-wheel.svg", ICON_PATH / "filter-wheel-selected.svg"))
def set_attenuation(factor: Callback(attenuation_factors, name="float", default=default_factor)):
    """ Set the OGSE attenuation factor to the given value.

    Args:
        - factor (float): requested attenuation factor [0.0 - 1.0], to be chosen from a drop-down menu.
    """
    start_observation(f"Set attenuation to {factor = }")

    try:
        with GlobalState.setup.gse.ogse.device as ogse:
            ogse.att_set_level_factor(factor=factor)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the OGSE, check if the OGSE Control Server is running.[/]")

    end_observation()


@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_ogse():
    """ Print table with the status of the different components of the OGSE."""

    from rich.console import Console
    from rich.table import Table

    from egse.collimator.fcul.ogse import OGSEInterface
    ogse: OGSEInterface

    try:
        with GlobalState.setup.gse.ogse.device as ogse:
            status = ogse.status()

            table = Table(title="OGSE Status Report")

            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            for par, val in status.items():
                table.add_row(par, str(val))

            console = Console(width=80)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the OGSE.[/]")
