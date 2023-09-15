from pathlib import Path
import time
from gui_executor.exec import exec_ui
from camtest.commanding.mgse import enable, point_source_to_fov, point_source_to_fp
from camtest import execute

UI_MODULE_DISPLAY_NAME = "2 — ZONDA Hexapod"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Initialise", use_kernel=True,
         icons=(ICON_PATH / "hexapod-init.svg", ICON_PATH / "hexapod-init-selected.svg"))
def enable_hexapod(description: str = "Initialisation of Zonda hexapod"):
    """ Starts and brings the hexapod to its initial state (in particular performs a go to zero position):
    1) clear errors
    2) activate Control On
    3) configure coordinates system
    4) enable limits if they are disable
    5) go to zero position.

    Args:
        description: description of the command executed (default description can be change to add details)

    """

    execute(enable, description=description)


@exec_ui(display_name="Point source to FOV", use_kernel=True,
         icons=(ICON_PATH / "hexapod-point-fov.svg", ICON_PATH / "hexapod-point-fov-selected.svg"))
def point_source_to_fov_hexapod(theta: float,
                                phi: float,
                                wait: bool = True,
                                description: str = 'Moving to fov coordinates (theta, phi)'):

    """
    Moves the hexapod to angular position (theta, phi).
    Args:
        theta: theta angle in degrees,
        phi: phi angle in degrees,
        wait: Whether or not to wait for the stages to reach the commanded positions.
        description: description of the command executed (default description can be change to add details)
    """

    execute(point_source_to_fov, theta=theta, phi=phi, wait=wait, description=description)


@exec_ui(display_name="Point source to FP", use_kernel=True,
         icons=(ICON_PATH / "hexapod-point-fp.svg", ICON_PATH / "hexapod-point-fp-selected.svg"))
def point_source_to_fp_hexapod(x: float,
                               y: float,
                               wait: bool = True,
                               description: str = 'Moving to pixel coordinates (x, y)'):

    """
    Moves the hexapod to pixel position (x, y).
    Args:
        x: x pixel index along horizontal axis,
        y: y pixel index along vertical axis,
        wait: Whether or not to wait for the stages to reach the commanded positions.
        description: description of the command executed (default description can be change to add details)
    """

    execute(point_source_to_fp, x=x, y=y, wait=wait, description=description)