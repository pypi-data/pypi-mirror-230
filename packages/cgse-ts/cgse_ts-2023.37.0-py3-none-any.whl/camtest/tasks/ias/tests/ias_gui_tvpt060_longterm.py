# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 16:25:06 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "11 — TVPT060 — Long Term stability"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt060_longterm(
        time: int = 28,
        num_bck: int = 1,
        fwc_fraction: float = 0.119,
        theta: float = 8.3,
        phi: float = 45,
        cycles_per_fits: int = 100,
        delay: float = 1000,
        integration: float = 15000,
        description: str = 'TVPT060 Long Term Test',
):
    """
    Runs the TVPT060 test described in PLATO CAM Test Plan
    Args:
        time: test measurement full duration, in hours
        num_bck: number of background images acquired
        fwc_fraction: light intensity, in terms of full-well fraction, achieved by the filter wheels combination
        theta: theta angle in degrees to define the image (mask with 4 stars and extended source) position on the FOV
        phi: phi angle in degrees
        cycles_per_fits: number of images saved in the same fits file (for storage slicing)
        delay: time between "integration" acquisitions, in ms
        integration: time during which the long term mask should be illuminated for acquisition, in ms
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_060_longterm_stability import cam_tvpt_060
    from camtest import execute

    execute(cam_tvpt_060, time=time, num_bck=num_bck, fwc_fraction = fwc_fraction,
            theta=theta, phi=phi, cycles_per_fits=cycles_per_fits, delay=delay,
            integration=integration, description=description)