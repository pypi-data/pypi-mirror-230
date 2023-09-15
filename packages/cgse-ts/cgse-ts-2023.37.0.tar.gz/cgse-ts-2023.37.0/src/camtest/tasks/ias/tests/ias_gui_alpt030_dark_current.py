# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 17:33:51 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "16 — ALPT030 — Dark ambient"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_alpt030_darkambient(
        num_bias: int = 10,
        num_dark: int = 10,
        exposure_times: list = [1, 5, 10],
        description: str = 'ALPT030 Dark current in ambient conditions',
):
    """
    Runs the TVLPT030 dark current measurement described in the PLATO CAM Test Plan
    Args:
        num_bias: number of bias images acquired at the shortest possible exposure time for RON evaluation
        num_dark: number of dark acquired at each of the exposure_times listed
        exposure_times: list of exposure times to be used in a row, in seconds.
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_alpt_030_test_dark_ncam_ambient import cam_alpt_030
    from camtest import execute

    execute(cam_alpt_030, num_bias=num_bias, num_dark=num_dark, exposure_times=exposure_times, description=description)
