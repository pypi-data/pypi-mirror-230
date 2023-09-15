# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 11:44:33 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "4 — TVPT050 — EMC"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt050_emc(
        cam_num_frames: int = 10,
        cam_num_bck: int = 10,
        bck_sides: str = 'BOTH',
        ci_width: int = 200,
        ci_gap: int = 200,
        ci_vgd: int = 16,
        source: bool = True,
        fwc_fraction: float = 0.3,
        bandpass: int = None,
        ccd_code: int = 1,
        row: int = 2498,
        column: int = 1000,
        description: str = 'TVPT050 EMC autocompatibility',
):
    """
    Runs the TVPT050 test described in PLATO CAM Test Plan
    Args:
        cam_num_frames: number of images
        cam_num_bck: number of background images
        bck_sides: CCD side to acquire for background images. This can be 'BOTH' (acquire E and F at the same time), 'E', 'F, 'EF' (acquire E first, and then F) or 'FE'.
        ci_width: int, width in rows of the regions with charge injections, typically 100 (see ci_gap), or 4510 for full injection
        ci_gap: int, width in rows of the regions without charge injections, typically 100
        ci_vgd: V_GD voltage, driving charge-injection level
                    V_GD ~ 14 : FWC
                    V_GD = 15 ~ 70% FWC
                    V_GD = 16 ~ 50% FWC
                    V_GD = 17 ~ 30% FWC
        source: bool, True if we want a source during charge injection, False or not otherwise
        fwc_fraction : ogse attenuation (sent to ogse.set_fwc_fraction)
        bandpass: IAS: Index in filter wheel 1 of the bandpass filter that is requested (None: white light, 1: Green, 2: Red, 3: NIR)
        ccd_code: int, CCD code associated with the position of the source. This needs to be a single value
        row : int, row position of the source. This needs to be a single position
        column : column, column position of the source. This needs to be a single position
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_050_test_695_autocompatibility_ncam import cam_tvpt_050
    from camtest import execute

    execute(cam_tvpt_050, cam_num_frames=cam_num_frames, cam_num_bck=cam_num_bck, bck_sides=bck_sides,
            ci_width=ci_width, ci_gap=ci_gap, ci_vgd=ci_vgd, source=source,
            fwc_fraction=fwc_fraction, bandpass=bandpass, ccd_code=ccd_code,
            row=row, column=column, description=description)