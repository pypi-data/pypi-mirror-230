# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 16:13:45 2022
 
@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "7 — TVPT100 — Vignetting"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="CAM-TVPT-100",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt100_vignetting(
        num_subpix: int = 12,
        num_frames: int = 4,
        num_bck: int = 2,
        thetas: list = [1,3,7,10,14.5,15,16,18,18.88,19,19.2,19.4,19.5,19.6,19.7,19.75,19.8,19.9],
        phis: float = -135.0,
        grid: bool = True,
        n_rows: int = 100,
        exposure_time: float = 0.1,
        clearout: bool = True,
        dith_amp: float = 0.012,
        fwc_fraction: float = 27.6,
        fov_selection: list = None,
        description: str = 'TVPT100 Vignetting',
):
    """
    Runs the TVPT100 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub-positions to be acquired for dithering
        num_frames: number of images
        num_bck: number of background images
        thetas: list of theta angles in degrees to be explored
        phis: scalar value in degree of the phi angle (diagonal) in the FOV to be explored at the thetas positions
        grid: whether to use a grid for movements or cylindrical reference frame (boolean)
        n_rows: number of detector rows to be read (central row determined automatically from hexpaod position)
        exposure_time: integration time in seconds
        clearout: reset the CCD or not (boolean)
        dith_amp: maximum amplitude of the dithering moves in degrees
        fwc_fraction: illumination intensity expressed in terms of full well fraction
        fov_selection: list of indexes in the complete FOV nominal positions list in the Setup.py file to select which areas should be covered
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_010_dither_int_sync_flexible import cam_tvpt_010_dither_int_sync_flexible
    from camtest import execute

    execute(cam_tvpt_010_dither_int_sync_flexible, num_subpix=num_subpix, 
            num_frames=num_frames, num_bck=num_bck, thetas=thetas, phis=phis,
            grid=grid, n_rows=n_rows, exposure_time=exposure_time, clearout=clearout,
            dith_amp=dith_amp, fwc_fraction=fwc_fraction, fov_slection=fov_selection,
            description=description)