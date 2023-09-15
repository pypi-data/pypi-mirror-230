from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "7.- CAM-TVPT-100 Vignetting "

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="dataset#100-2",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_100_2(
        num_subpix: int = 5, 
        num_frames: int = 6, 
        num_bck: int = 2, 
        n_rows: int = 250, 
        exposure_time: float = 0.1, 
        clearout: bool = True, 
        dith_amp: float = 0.012, 
        fwc_fraction: float = 0.0, 
        fov_selection: list = None, 
        bandpass: int =None, 
        fov_table: str="reference_partial_diagonals", 
        description: str="TP#16 Vignetting_Partial Diagonals - CAM-TVPT-100"):

    """
    Runs the TVPT100 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub-positions to be acquired for dithering
        num_frames: number of images
        num_bck: number of background images
        n_rows: number of detector rows to be read (central row determined automatically from hexpaod position)
        exposure_time: integration time in seconds
        clearout: reset the CCD or not (boolean)
        dith_amp: maximum amplitude of the dithering moves in degrees
        fwc_fraction: illumination intensity expressed in terms of full well fraction
        fov_selection: list of indexes in the complete FOV nominal positions list in the Setup.py file to select which areas should be covered
        bandpass: if 0 or None, normal behaviour with both wheels used to obtain the requested fwc_fraction. If 1,2,3 selects green, red, NIR colors and thus reduces the range of available attenuations
        fov_table: name of the (theta, phi) positions to be used in the setup file
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    
    from camtest.commanding.cam_tvpt_010_best_focus_determination_int_sync import cam_tvpt_010_int_sync
    from camtest import execute


    execute(cam_tvpt_010_int_sync, 
            num_subpix=num_subpix, 
            num_frames=num_frames, 
            num_bck=num_bck, 
            n_rows=n_rows, 
            exposure_time=exposure_time, 
            clearout=clearout, 
            dith_amp=dith_amp, 
            fwc_fraction=fwc_fraction, 
            fov_selection=fov_selection, 
            bandpass=bandpass, 
            fov_table=fov_table, 
            description=description)




    
    