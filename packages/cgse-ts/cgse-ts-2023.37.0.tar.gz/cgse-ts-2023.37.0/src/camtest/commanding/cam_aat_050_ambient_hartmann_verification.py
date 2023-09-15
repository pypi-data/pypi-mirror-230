"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR HARTMANN VERIFICATION TEST AT AMBIENT

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    CAM in DUMP mode or DUMP mode internal sync

End status
    CAM in DUMP mode internal sync
    MGSE with the source at the last visited FoV position

Synopsis:

Authors: P. Royer

Versions:
    2020 10 27 : Creation from cam_aat_050_ambient_hartmann_verification_prep [ran multiple times in CSL at EM level]


"""
import logging

from camtest import GlobalState, building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import equi_surface_fov_geometry, sort_on_azimuth
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table

LOGGER = logging.getLogger(__name__)


@building_block
def cam_aat_050_ambient_hartmann_verification(num_cycles=None, exposure_time=None,n_rows=None, table_name=None, use_angles=None, sort_fov_pos_in_azimuth=None, reverse_azimuth_order=None):
    """
    SYNOPSIS
    cam_aat_050_ambient_hartmann_verification(num_cycles=None, exposure_time=None,n_rows=None, table_name=None, use_angles=None)

    GOAL
    Visit the 40 FoV positions defined in setup.fov_positions[table_name]
    At every position, acquire num_cycles images, with partial readout of n_rows rows and an exposure time
    of exposure_time

    INPUTS
    num_cycles = 5: nb of images to be acquired at every FoV position
    exposure_time : exposure time, used by the DPU mode for FEE-internal-synchronization to compute the image cycle_time
    n_rows=1500   : nb of rows to read (partial readout). n_rows//2 above and below the computed source position
    table_name = 'reference_full_40' : setup table defining the positions
    use_angles = True : [theta, phi] are read from the table [elevation, azimuth, in degrees]
               = False : x,y are read from the table [focal plane coordinates, in mm]
    sort_fov_pos_in_azimuth: if True, the positions will be visited in ascending azimuth, from -180 to +180 deg
    reverse_azimuth: if sort_fov_pos_in_azimuth and reverse_azimuth_order are True, the positions will be visited in
        descending azimuth, from +180 to -180 deg

    EXAMPLES:

        CSL :
            . compute the input coordinates from the TOU_MEC xy coordinates observed in LDO --> use_angles=False
            . FoV positions sorted in azimuth --> sort_fov_pos_in_azimuth=True)

            cam_aat_050_ambient_hartmann_verification(num_cycles=5, exposure_time=0.2,n_rows=1000,
            table_name='reference_full_40', use_angles=False, sort_fov_pos_in_azimuth=True, reverse_azimuth_order=False)

        THs :
            . use field angles as input coordinates --> use_angles = True
            . FoV positions order defined by the setup (traveling salesman) --> sort_fov_pos_in_azimuth=False

            cam_aat_050_ambient_hartmann_verification(num_cycles=5, exposure_time=0.2,n_rows=1000,
            table_name='reference_full_40', use_angles=True, sort_fov_pos_in_azimuth=False, reverse_azimuth_order=False)

    """
    setup = GlobalState.setup

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    # MAKE SURE THE OGSE SHUTTER IS OPEN
    ogse.shutter_open()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    # FOV GEOMETRY DEFINITION
    ####################################################

    verbose = True

    # distorted_ccdcoords is used to compute the resulting CCD coordinates
    distorted_ccdcoords = True

    # Compute FoV positions rather than using the setup - False
    use_computed_fov_pos = False

    if use_computed_fov_pos:

        setup.camera.fov.radius_mm = 81.52

        cells = [1, 2, 3, 4]
        boost, boostFactor = 1, 1

        ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = equi_surface_fov_geometry(cells=cells, \
                                    boost=boost, boostFactor=boostFactor, distorted=distorted_ccdcoords, verbose=True)
    else:

        if use_angles:
            distorted_input = False
        else:
            distorted_input = True

        ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted_ccdcoords, distorted_input=distorted_input, table_name=table_name, use_angles=use_angles, verbose=verbose)

    if sort_fov_pos_in_azimuth:
        angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,[ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],reverse=reverse_azimuth_order)
    else:
        angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig]

    LOGGER.info(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
    c = 0
    for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
        LOGGER.info(
            f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
        c += 1

    ####################################################
    # CORE OF THE TEST
    ####################################################

    cam_aat_050_ambient_recentering(num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
                                    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
                                    n_rows=n_rows)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
