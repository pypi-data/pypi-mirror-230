# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 12:00:10 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "7 — TVPT080 — Dynamic"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt080_dynamic(
        num_frames: int = 6,
        num_subpix: int = 5,
        mag_list: list = [4, 5.9, 7, 8, 9.6, 10.8, 14.85],
        fov_list: ListList([float, float], [4, 45]) = None,
        description: str = 'TVPT080 Dynamic range',
):
    """
    Runs the TVPT080 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub-positions to be acquired for dithering
        num_frames: number of images
        mag_list: list of stellar magnitudes to be imitated by the source and attenuators
        fov_list: list of [theta, phi] positions in the focal plane
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_080_dynamic_range import cam_tvpt_080
    from camtest import execute

    execute(cam_tvpt_080, num_frames=num_frames, num_subpix=num_subpix,
            mag_list=mag_list, fov_list=fov_list,
            description=description)