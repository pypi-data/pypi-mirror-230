from pathlib import Path
import time
from gui_executor.exec import exec_ui
from camtest.commanding.ogse import ogse_swon, ogse_swoff
from camtest import execute

UI_MODULE_DISPLAY_NAME = "1 — OGSE"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Switch ON", use_kernel=True,
         icons=(ICON_PATH / "ogse-swon.svg", ICON_PATH / "ogse-swon-selected.svg"))
def switch_on_ogse(description: str = "OGSE Switch ON"):
    """ Turns the OGSE ON by:
    - closing the shutter and
    - homing the filter wheel to (1,1).

    Args:
        description: description of the command executed (default description can be change to add details)

    """

    execute(ogse_swon, description=description)


@exec_ui(display_name="Switch OFF", use_kernel=True,
         icons=(ICON_PATH / "ogse-swoff.svg", ICON_PATH / "ogse-swoff-selected.svg"))
def switch_off_ogse(description: str = "OGSE Switch OFF"):
    """ Turns the OGSE OFF by:
    - closing the shutter

    Args:
        description: description of the command executed (default description can be change to add details)

    """

    execute(ogse_swoff, description=description)