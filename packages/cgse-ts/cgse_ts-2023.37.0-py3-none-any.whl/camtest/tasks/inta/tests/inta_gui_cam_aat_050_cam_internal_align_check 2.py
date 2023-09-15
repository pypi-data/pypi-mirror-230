from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "1.- CAM-AAT-050 Quick Camera Interna Alignment Check"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="dataset#AAT050_A-1",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_aat050_a_1(
        theta: float = 8.3,
        phi: int = -9,
        num_cycles: int = 5,
        exposure_time: float = 0.2,
        attenuation: float = 0.0,
        n_rows: int = 500,
        description: str = 'CAM-AAT-050 - Ambient flux adjustment',):

    """
    Runs the AAT050 A-1 test described in PLATO CAM Test Plan
    Args:
        theta: theta angle in degrees to define the image (mask with 4 stars and extended source) position on the FOV
        phi: phi angle in degrees
        num_cycles: number of acquired images
        exposure_time: integration time in seconds for each image
        attenauation  : fwc_fraction, will be used to command the ogse
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)        
     """


    from camtest.commanding.cam_single_cube_int_sync import cam_single_cube_int_sync
    from camtest import execute

    execute(cam_single_cube_int_sync, 
            theta=theta, 
            phi=phi, 
            num_cycles=num_cycles, 
            exposure_time=exposure_time, 
            attenuation=attenuation, 
            n_rows=n_rows, 
            description=description)
    
@exec_ui(display_name="dataset#AAT050_B-1",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_aat050_b_1(
        num_cycles: int = 5, 
        exposure_time: float = 0.2, 
        n_rows: int = 500, 
        table_name: str = "reference_full_40", 
        use_angles: bool = True, 
        sort_fov_pos_in_azimuth: bool = True, 
        reverse_azimuth_order: bool  = False,
        description: str = 'CAM-AAT-050 - Ambient Hartmann Verif 40 positions',):

    """
    Runs the AAT050 B-1 test described in PLATO CAM Test Plan
    Args:
        num_cycles: number of acquired images
        exposure_time: integration time in seconds for each image
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        table_name: setup table defining the positions
        use_angles: from 'table_name', use the focal plane coordinates used by LDO (xy, in mm)
        sort_fov_pos_in_azimuth: if True, the positions will be visited in ascending azimuth, from -180 to +180 deg
        reverse_azimuth: if sort_fov_pos_in_azimuth and reverse_azimuth_order are True, the positions will be visited in descending azimuth, from +180 to -180 deg
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)        
     """

    from camtest.commanding.cam_aat_050_ambient_hartmann_verification import cam_aat_050_ambient_hartmann_verification
    from camtest import execute

    execute(cam_aat_050_ambient_hartmann_verification, 
            num_cycles=num_cycles, 
            exposure_time=exposure_time, 
            n_rows=n_rows, 
            table_name=table_name, 
            use_angles=use_angles, 
            sort_fov_pos_in_azimuth=sort_fov_pos_in_azimuth, 
            reverse_azimuth_order=reverse_azimuth_order, 
            description=description)
    

@exec_ui(display_name="dataset#AAT050_A-2",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_aat050_a_2(
        num_cycles: int = 5,
        exposure_time: float = 0.2,
        elevation: float = 8.3,
        n_pos: int = 20,
        n_rows: int = 500,
        reverse_order: bool = False,
        description: str = 'CAM-AAT-050 - Ambient. 1 atm. Reference circle at 8.3 deg of elevation',):

    """
    Runs the AAT050 A-2 test described in PLATO CAM Test Plan
    Args:
        num_cycles: number of acquired images
        exposure_time: integration time in seconds for each image
        elevation : boresight angle of all the fov positions to define
        n_pos: nb of FoV positions to visit.
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        reverse_order: if True, the order is inverted
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)        
     """

    from camtest.commanding.cam_aat_050_ambient_circle import cam_aat_050_ambient_circle
    from camtest import execute

    execute(cam_aat_050_ambient_circle, num_cycles=num_cycles, exposure_time=exposure_time, elevation=elevation,
            n_pos=n_pos, n_rows=n_rows, reverse_order=reverse_order, description=description)

