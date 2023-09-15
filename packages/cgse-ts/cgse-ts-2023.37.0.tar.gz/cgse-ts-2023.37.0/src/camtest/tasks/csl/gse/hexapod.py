from pathlib import Path

import time
from gui_executor.exec import exec_ui

from camtest import end_observation
from camtest import start_observation
from egse.control import Failure
from egse.hexapod import HexapodError
from egse.hexapod.symetrie.puna import PunaInterface
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "2 — PUNA Hexapod"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


ACTUATOR_STATE_LABELS = [
    "In position",
    "Control loop on servo motors active",
    "Homing done",
    "Input “Home switch”",
    "Input “Positive limit switch”",
    "Input “Negative limit switch”",
    "Brake control output",
    "Following error (warning)",
    "Following error",
    "Actuator out of bounds error",
    "Amplifier error",
    "Encoder error",
    "Phasing error (brushless engine only)",
]

GENERAL_STATE_LABELS = [
    "Error",
    "System Initialized",
    "In position",
    "Amplifier enabled",
    "Homing done",
    "Brake on",
    "Emergency stop",
    "Warning FE",
    "Fatal FE",
    "Actuator Limit Error",
    "Amplifier Error",
    "Encoder error",
    "Phasing error",
    "Homing error",
    "Kinematic error",
    "Abort input error",
    "R/W memory error",
    "Temperature error",
    "Homing done (virtual)",
    "Encoders power off",
    "Limit switches power off"
]


@exec_ui(display_name="Homing", use_kernel=True,
         icons=(ICON_PATH / "hexapod-homing.svg", ICON_PATH / "hexapod-homing-selected.svg"))
def home_hexapod():
    """ Perform a Homing of the PUNA Hexapod and waits until the Homing is finished.
    """

    puna: PunaInterface

    start_observation("Homing the Hexapod PUNA")

    try:
        with GlobalState.setup.gse.hexapod.device as puna:
            puna.homing()

            while not puna.is_homing_done():
                time.sleep(1.0)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Hexapod Control Server, check in the PM GUI if it's running.[/]")
    except HexapodError as exc:
        print("[red]ERROR: {exc}[/]")
    else:
        print("[green]PUNA Hexapod has now been homed.[/]", flush=True)

    end_observation()


@exec_ui(display_name="Retract", use_kernel=True,
         icons=(ICON_PATH / "hexapod-retract.svg", ICON_PATH / "hexapod-retract-selected.svg"))
def retract_hexapod():
    """ Bring the PUNA Hexapod to retracted position.
    """

    puna: PunaInterface

    start_observation("Retracting the Hexapod PUNA")

    try:
        with GlobalState.setup.gse.hexapod.device as puna:
            puna.goto_retracted_position()

            while not puna.is_in_position():
                time.sleep(1.0)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Hexapod Control Server, check in the PM GUI if it's running.[/]")
    except HexapodError as exc:
        print("[red]ERROR: {exc}[/]")
    else:
        print("[green]PUNA Hexapod is now in retracted position.[/]", flush=True)

    end_observation()


@exec_ui(display_name="Zero Position", use_kernel=True,
         icons=(ICON_PATH / "hexapod-zero.svg", ICON_PATH / "hexapod-zero-selected.svg"))
def zero_hexapod():
    """ Bring the PUNA Hexapod to the zero position.
    """
    puna: PunaInterface

    start_observation("Bring the Hexapod PUNA to zero position")

    try:
        with GlobalState.setup.gse.hexapod.device as puna:
            puna.goto_zero_position()

            while not puna.is_in_position():
                time.sleep(1.0)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Hexapod Control Server, check in the PM GUI if it's running.[/]")
    except HexapodError as exc:
        print("[red]ERROR: {exc}[/]")
    else:
        print("[green]PUNA Hexapod is now in zero position.[/]", flush=True)

    end_observation()


@exec_ui(display_name="Emergency stop",
         immediate_run=True,
         use_kernel=True,
         icons=(ICON_PATH / "stop.svg", ICON_PATH / "stop.svg"))
def emergency_stop():
    """ Emergency stop of the PUNA hexapod."""

    puna: PunaInterface

    try:
        with GlobalState.setup.gse.hexapod.device as puna:
            rc = puna.stop()
            if isinstance(rc, Failure):
                print(f"[red]ERROR: {rc.cause}")
            else:
                print("[red bold]PUNA Hexapod was stopped![/]")
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Hexapod Control Server, check in the PM GUI if it's running.[/]")
    except HexapodError as exc:
        print("[red]ERROR: {exc}[/]")


@exec_ui(display_name="General state", immediate_run=True, use_script_app=True)
def print_general_state_hexapod():
    """ Print table with the general state of the hexapod."""

    from rich.console import Console
    from rich.table import Table

    hexapod: PunaInterface

    general_state_table = Table(title="Hexapod General Status Report", show_header=False, show_lines=True)

    try:
        with GlobalState.setup.gse.hexapod.device as hexapod:

            general_status = hexapod.get_general_state()[1]

            for index in range(len(GENERAL_STATE_LABELS)):

                if general_status[index]:
                    general_state_table.add_row(GENERAL_STATE_LABELS[index], "x")
                else:
                    general_state_table.add_row(GENERAL_STATE_LABELS[index], "")

    except ConnectionError:
        print("[red]ERROR: Could not connect to the PUNA hexapod.[/]")

    console = Console(width=200)
    console.print(general_state_table)


@exec_ui(display_name="Actuator state", immediate_run=True, use_script_app=True)
def print_actuator_state_hexapod():
    """ Print table with the status of the actuators of the hexapod."""

    from rich.console import Console
    from rich.table import Table

    hexapod: PunaInterface

    actuator_status_table = Table(title="Hexapod Actuators Status Report", show_lines=True)
    actuator_status_table.add_column("Actuator state")
    actuator_status_table.add_column("1", no_wrap=True)
    actuator_status_table.add_column("2", no_wrap=True)
    actuator_status_table.add_column("3", no_wrap=True)
    actuator_status_table.add_column("4", no_wrap=True)
    actuator_status_table.add_column("5", no_wrap=True)
    actuator_status_table.add_column("6", no_wrap=True)

    try:
        with GlobalState.setup.gse.hexapod.device as hexapod:

            actuator_statuses = hexapod.get_actuator_state()
            for index in range(len(ACTUATOR_STATE_LABELS)):

                actuator_status_row = [ACTUATOR_STATE_LABELS[index]]
                for actuator_index in range(6):
                    actuator_status = actuator_statuses[actuator_index][0]

                    if index in actuator_status:
                        actuator_status_row.append("x")
                    else:
                        actuator_status_row.append(None)

                actuator_status_table.add_row(*actuator_status_row)

    except ConnectionError:
        print("[red]ERROR: Could not connect to the PUNA hexapod.[/]")

    console = Console(width=200)
    console.print(actuator_status_table)
