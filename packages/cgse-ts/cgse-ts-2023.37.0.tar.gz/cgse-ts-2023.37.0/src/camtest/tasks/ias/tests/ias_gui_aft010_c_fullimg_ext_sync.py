# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 17:33:51 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "14 — AFT010C — Full image ext sync"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_aft010_c(
        num_cycles: int = 5,
        sleep_time: float = 15,
        description: str = 'CAM-AFT-010 C AD.8 Full Image external sync',
):
    """
    Runs the AFT_010 C measurement described in the PLATO CAM Test Plan
    Args:
        num_cycles: number of acquired images
        sleep_time: delay time in seconds between images
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_aft_010_C_full_image_ext_sync import cam_aft_010_C_full_image_ext_sync
    from camtest import execute

    execute(cam_aft_010_C_full_image_ext_sync, num_cycles=num_cycles, sleep_time=sleep_time, description=description)
