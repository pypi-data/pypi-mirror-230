# -*- coding: utf-8 -*-
"""
Created on Tue May  9 10:38:31 2023

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "16 — TVPT080 — Dynamic int sync"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt080_dynamic_int_sync(
        num_frames: int = 100,
        num_subpix: int = 25,
        num_bck: int = 3,
        mag_list: list = [4, 7, 8, 9, 11, 16],
        exposure_time: float = 0.1,
        fov_list: ListList([float, float], [4, 45]) = None,
        description: str = 'TVPT080 Dynamic range int sync',
):
    """
    Runs the TVPT080 int sync test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub-positions to be acquired for dithering
        num_frames: number of images
        num_bck: number of background images to be acquired at beginning of each position
        mag_list: list of stellar magnitudes to be imitated by the source and attenuators
        exposure_time: integration time in s of each frame
        fov_list: list of [theta, phi] positions in the focal plane
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_080_dynamic_range_int_sync import cam_tvpt_080_int_sync
    from camtest import execute

    execute(cam_tvpt_080_int_sync, num_frames=num_frames, num_subpix=num_subpix,
            num_bck=num_bck, mag_list=mag_list, exposure_time=exposure_time, fov_list=fov_list,
            description=description)