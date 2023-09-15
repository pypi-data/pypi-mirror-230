# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 16:04:34 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "10 — TVPT090 — Ghosts"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt090_ghosts(
        num_frames_sat: int = 6,
        num_frames_nonsat: int = 19,
        num_bck: int = 3,
        fwc_sat: float = 81,
        fwc_nonsat: float = 0.1,
        manual_visit: bool = False,
        angles_manual: list = None,
        fwc_manual: float = None,
        num_frames_manual: int = None,
        description: str = 'TVPT090 Ghosts',
):
    """
    Runs the TVPT090 test described in PLATO CAM Test Plan
    Args:
        num_frames_sat: number of images acquired with the saturated level of illumination corresponding to fwc_sat
        num_frames_nonsat:number of images acquired with the non saturated level of illumination corresponding to fwc_nonsat
        num_bck: number of background images
        fwc_sat: full well corresponding to the attenuator level for saturation
        fwc_nonsat: full well corresponding to the attenuator level for below saturation
        manual_visit: boolean to use the manual version where spatial position and fwc is given one at a time by the operator
        angles_manual: position in the FOV to be pointed in case manual_visit is true
        fwc_manual: illumination level to be used if manual_visit is true
        num_frames manual: number of images to acquire if the manual_visit is true
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_090_ghosts import cam_tvpt_090
    from camtest import execute

    execute(cam_tvpt_090, num_frames_sat=num_frames_sat, num_frames_nonsat=num_frames_nonsat,
            num_back = num_bck, fwc_sat = fwc_sat, fwc_nonsat = fwc_nonsat, manual_visit = manual_visit,
            angles_manual = angles_manual, fwc_manual = fwc_manual,
            num_frames_manual = num_frames_manual, description=description)