# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 11:25:06 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "6 — TVPT045 — Blooming"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt045_blooming(
        num_dark: int = 2,
        num_cycles: int = 2,
        mag_list: list = [9.6, 8, 7, 5.9, 4],
        fov_positions: ListList([float, float], [8.3, 135]) = None,
        num_subpix: int = 2,
        delta_column: float = 0.5,
        ccd_order: list = None,
        ccd_both: bool = False,
        description: str = 'TVPT045 tearing and blooming',
):
    """
    Runs the TVPT045 test described in PLATO CAM Test Plan
    Args:
        num_dark: number of dark images
        num_cycles: number of cycles of images acquisitions
        mag_list: list of stellar magnitudes to be imitated by the source and attenuators
        fov_positions: list of [theta, phi] positions in the focal plane
        num_subpix: number of sub-positions in case of dithering
        delta_column: ?
        ccd_order: order in which the 4 CCDs are read
        ccd_both: whether or not both sides, E and F, of each CCD are readout
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_045_ccd_tearing_blooming import cam_tvpt_ccd_tear_blooming
    from camtest import execute

    execute(cam_tvpt_ccd_tear_blooming, num_dark=num_dark, num_cycles=num_cycles,
            mag_list=mag_list, fov_positions=fov_positions, num_subpix=num_subpix,
            delta_column=delta_column, ccd_order=ccd_order, ccd_both=ccd_both,
            description=description)