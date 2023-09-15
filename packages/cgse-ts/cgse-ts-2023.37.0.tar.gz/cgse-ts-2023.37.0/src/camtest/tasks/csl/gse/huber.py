from pathlib import Path
from typing import List

from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest.commanding import mgse
from camtest.commanding.csl_gse import rotation_stage_move, sma_rotation_move, sma_translation_move
from camtest import end_observation, start_observation
from egse.settings import Settings
from egse.stages.huber import is_smc9300_cs_active
from egse.stages.huber.smc9300 import HuberSMC9300Interface, untangle_status
from egse.stages.huber.smc9300_devif import HuberError
from egse.state import GlobalState
from camtest import execute

UI_MODULE_DISPLAY_NAME = "3 — HUBER Stages"
ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"
HC_SETTINGS = Settings.load("Huber Controller")
DEGREE_SIGN = u'\u00b0'


@exec_ui(display_name="Point source to FOV")
def point_source_to_fov(theta: float, phi: float, wait: bool = False):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms such that the illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - wait: Whether to wait for the stages to reach the commanded positions.
    """

    print(f"Point source to FOV: (theta, phi) = ({theta}{DEGREE_SIGN}, {phi}{DEGREE_SIGN})")
    execute(mgse.point_source_to_fov, theta=theta, phi=phi, wait=wait)


@exec_ui(display_name="Status", immediate_run=True, use_script_app=True)
def print_status_stages():
    """ Print table with the status of the different components of the Huber Stages."""

    from rich.console import Console
    from rich.table import Table

    stages: HuberSMC9300Interface

    try:
        with GlobalState.setup.gse.stages.device as stages:

            status_big_rot_stage = untangle_status(stages.get_status(axis=HC_SETTINGS.BIG_ROTATION_STAGE))
            status_small_rot_stage = untangle_status(stages.get_status(axis=HC_SETTINGS.SMALL_ROTATION_STAGE))
            status_trans_stage = untangle_status(stages.get_status(axis=HC_SETTINGS.TRANSLATION_STAGE))

            table = Table(title="Huber Stages Status Report")

            table.add_column("Parameter")
            table.add_column("Big rotation stage", no_wrap=True, justify="right")
            table.add_column("Small rotation stage", no_wrap=True, justify="right")
            table.add_column("Translation stage", no_wrap=True, justify="right")

            table.add_row("Error number", str(status_big_rot_stage["err_no"]), str(status_small_rot_stage["err_no"]),
                          str(status_trans_stage["err_no"]))
            table.add_row("Error message", str(status_big_rot_stage["err_msg"]) or "NA",
                          str(status_small_rot_stage["err_msg"]) or "NA", str(status_trans_stage["err_msg"]) or "NA")
            table.add_row("Position", str(status_big_rot_stage["pos"]), str(status_small_rot_stage["pos"]),
                          str(status_trans_stage["pos"]))
            table.add_row("Encoder position", str(status_big_rot_stage["epos"]), str(status_small_rot_stage["epos"]),
                          str(status_trans_stage["epos"]))
            table.add_row("End/limit status", str(status_big_rot_stage["elimit"]),
                          str(status_small_rot_stage["elimit"]), str(status_trans_stage["elimit"]))
            table.add_row("Reference status", str(status_big_rot_stage["ref"]), str(status_small_rot_stage["ref"]),
                          str(status_trans_stage["ref"]))
            table.add_row("Encoder reference status", str(status_big_rot_stage["eref"]),
                          str(status_small_rot_stage["eref"]), str(status_trans_stage["eref"]))
            table.add_row("Controller ready", str(status_big_rot_stage["ctrl"]), str(status_small_rot_stage["ctrl"]),
                          str(status_trans_stage["ctrl"]))
            table.add_row("Oscillation status", str(status_big_rot_stage["osc"]), str(status_small_rot_stage["osc"]),
                          str(status_trans_stage["osc"]))
            table.add_row("Programme running", str(status_big_rot_stage["prog"]), str(status_small_rot_stage["prog"]),
                          str(status_trans_stage["prog"]))

            console = Console(width=200)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Huber Stages.[/]")


@exec_ui(display_name="Emergency stop",
         immediate_run=True,
         use_script_app=True,
         icons=(ICON_PATH / "stop.svg", ICON_PATH / "stop.svg"))
def emergency_stop():
    """ Emergency stop of the Huber stages.

    This task runs as a script (which is needed to interrupt the movement in a function / building block that waits),
    as a consequence of which this command will not be logged.
    """

    stages: HuberSMC9300Interface

    try:
        with GlobalState.setup.gse.stages.device as stages:
            stages.quit()
            if stages.is_in_position(HC_SETTINGS.BIG_ROTATION_STAGE) \
                    and stages.is_in_position(HC_SETTINGS.SMALL_ROTATION_STAGE) \
                    and stages.is_in_position(HC_SETTINGS.TRANSLATION_STAGE):
                print("[red bold]Huber Stages were stopped![/]")
            else:
                print(f"[red]ERROR:")
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Huber SMC9300 Control Server, "
              "check in the PM GUI if it's running.[/]")
    except HuberError as exc:
        print("[red]ERROR: {exc}[/]")


def movement_types() -> List:
    return ["absolute", "relative"]


@exec_ui(display_name="Move big rotation stage")
def move_big_rotation_stage(movement_type: Callback(movement_types, name="movement type"), position: float):
    """ Move the big rotation stage.

    Args:
        - movement_type: Indicates whether the movement is defined in absolute or relative terms
        - position: In case of an absolute movement, this is the angle to move to.  In case of a relative movement,
                    this is the angle to move over.  Expressed in degrees.
    """

    if is_smc9300_cs_active():
        try:
            if movement_type == "absolute":
                start_observation(f"Moving big rotation stage to {position} degrees")
                rotation_stage_move(angle=position)

            else:
                start_observation(f"Moving big rotation stage over {position} degrees")

                stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device
                stages.move(HC_SETTINGS.BIG_ROTATION_STAGE, position, False)
        finally:
            end_observation()
    else:
        print("The Stages Control Server is not active: The movement of the big rotation stage could not be performed.")


@exec_ui(display_name="Move small rotation stage")
def move_small_rotation_stage(movement_type: Callback(movement_types, name="movement type"), position: float):
    """ Move the small rotation stage.

    Args:
        - movement_type: Indicates whether the movement is defined in absolute or relative terms
        - position: In case of an absolute movement, this is the angle to move to.  In case of a relative movement,
                    this is the angle to move over.  Expressed in degrees.
    """

    if is_smc9300_cs_active():
        try:
            if movement_type == "absolute":
                start_observation(f"Moving small rotation stage to {position} degrees")
                sma_rotation_move(angle=position)

            else:
                start_observation(f"Moving small rotation stage over {position} degrees")
                stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device
                stages.move(HC_SETTINGS.SMALL_ROTATION_STAGE, position, False)
        finally:
            end_observation()
    else:
        print("The Stages Control Server is not active: The movement of the small rotation stage could not be "
              "performed.")


@exec_ui(display_name="Move translation stage")
def move_translation_stage(movement_type: Callback(movement_types, name="movement type"), position: float):
    """ Move the translation stage.

    Args:
        - movement_type: Indicates whether the movement is defined in absolute or relative terms
        - position: In case of an absolute movement, this is the distance to move to.  In case of a relative movement,
                    this is the distance to move over.  Expressed in mm.
    """

    if is_smc9300_cs_active():
        try:
            if movement_type == "absolute":
                start_observation(f"Moving translation stage to {position}mm")
                sma_translation_move(distance=position)
            else:
                start_observation(f"Moving translation stage over {position}mm")
                stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device
                stages.move(HC_SETTINGS.TRANSLATION_STAGE, position, False)
        finally:
            end_observation()
    else:
        print("The Stages Control Server is not active: The movement of the translation stage could not be performed.")
