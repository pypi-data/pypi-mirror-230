from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "6.- CAM-TVPT-031 PSF at nominal focus temperature "

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="dataset#31-1",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_31_1(
        num_subpix: int = 25, 
        num_frames: int = 4, 
        num_bck: int = 2, 
        n_rows: int = 100, 
        exposure_time: float = 0.1, 
        clearout: bool = True, 
        dith_amp: float = 0.012, 
        fwc_fraction: float = 0.0, 
        fov_selection: list = [1,2,3,4,5,6,7,8,9,10,40], 
        bandpass: int =None, 
        fov_table: str="reference_full_44_confirmed", 
        description: str="TP#16 Performance test at nominal focus temperature - CAM-TVPT-031_31-1"):

    """
    Runs the TVPT031 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        clearout: reset of the CCD between each image, should be true to diminish persistence risks
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        bandpass: allows to select the color filter to be used (None: white light, 1: Green, 2: Red, 3: NIR)
        fov_table: provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')        
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


@exec_ui(display_name="dataset#31-2",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_31_2(
        num_subpix: int = 25, 
        num_frames: int = 4, 
        num_bck: int = 2, 
        n_rows: int = None, 
        mode: str = "full", 
        dith_amp: float = 0.012, 
        fwc_fraction: float = 0.0,
        fov_selection: list = [1,2,3,4,5,6,7,8,9,10,40],
        fov_table: str = "reference_full_44_confirmed", 
        bandpass: int = None, 
        description: str="CAM-TVPT-010 best focus search at -75degC external sync"):
   
   from camtest.commanding.cam_tvpt_010_best_focus_determination import cam_tvpt_010
   from camtest import execute

   """
    Runs the TVPT031 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        clearout: reset of the CCD between each image, should be true to diminish persistence risks
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        bandpass: allows to select the color filter to be used (None: white light, 1: Green, 2: Red, 3: NIR)
        fov_table: provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')        
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """


   execute(cam_tvpt_010, 
            num_subpix=num_subpix, 
            num_frames=num_frames, 
            num_bck=num_bck, 
            n_rows=n_rows, 
            mode=mode, 
            dith_amp=dith_amp, 
            fwc_fraction=fwc_fraction, 
            fov_table=fov_table, 
            fov_selection=fov_selection, 
            bandpass=bandpass,
            description=description)

@exec_ui(display_name="dataset#31-3",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_31_3(
        num_subpix: int = 25, 
        num_frames: int = 4, 
        num_bck: int = 2, 
        n_rows: int = 100, 
        exposure_time: float = 1.74, 
        clearout: bool = True, 
        dith_amp: float = 0.012, 
        fwc_fraction: float = 0.0, 
        fov_selection: list = [1,2,3,4,5,6,7,8,9,10,40], 
        bandpass: int =None, 
        fov_table: str="reference_full_44_confirmed", 
        description: str="TP#16 Performance test at nominal focus temperature - CAM-TVPT-031_31-3"):


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





    
    