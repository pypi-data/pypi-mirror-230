# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:41:12 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "8 — TVPT080B — Persistence"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt080b_persistence(
        num_frames: int = 10,
        num_predark: int = 10,
        num_postdark: int = 50,
        mag: float = 1.14,
        fov_list: ListList([float, float], [15, 145]) = None,
        description: str = 'TVPT080 B Persistence and Crosstalk',
):
    """
    Runs the TVPT080 B test described in PLATO CAM Test Plan
    Args:
        num_frames: number of images
        num_predark: number of dark images acquired before the persistence is tested
        num_postdark: number of dark images acquired after the persistence is tested, ie after saturation of the detector
        mag: stellar magnitude to be imitated by the source and attenuators to saturate the detector
        fov_list: list of [theta, phi] positions in the focal plane
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_080_B_persistence_crosstalk import cam_tvpt_080_B
    from camtest import execute

    execute(cam_tvpt_080_B, num_frames=num_frames, num_predark=num_predark,
            num_postdark=num_postdark, mag=mag, fov_list=fov_list,
            description=description)