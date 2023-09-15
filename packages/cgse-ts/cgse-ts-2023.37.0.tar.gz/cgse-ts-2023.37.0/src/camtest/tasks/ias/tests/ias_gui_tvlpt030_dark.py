# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 17:33:51 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "3 — TVLPT030 — Dark"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvlpt030_dark(
        num_bias: int = 10,
        num_dark: int = 10,
        description: str = 'TVLPT030 Dark current in cold conditions',
):
    """
    Runs the TVLPT030 dark current measurement described in the PLATO CAM Test Plan
    Args:
        num_bias: number of bias images acquired at the shortest possible exposure time for RON evaluation
        num_dark: number of dark acquired at nominal ext_sync exposure time (25 s)
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvlpt_030_test_673_dark_ncam import cam_tvlpt_030
    from camtest import execute

    execute(cam_tvlpt_030, num_bias=num_bias, num_dark=num_dark, description=description)
