"""Camera Test for the optical alignment of the FPA with respect to the TOU.

See Test Specification PLATO-KUL-PL-TS-0001.

Usage:

    >>> execute(cam_aat_050, <args>)
"""

from camtest import dpu
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.core.exec import building_block
from egse.visitedpositions import visit_field_angles


@building_block
def cam_aat_050_ambient_visit_ccd_xys(num_cycles=None, exposure_times=None, angles=None, ccd_rows=None, ccd_cols=None, ccd_codes=None, ccd_sides=None, n_rows=None, theta_correction=None, sma_correction=None):
    """
    SIGNATURE
    cam_aat_050_ambient_visit_ccd_xys(num_cycles=None, exposure_time=None, angles=None, ccd_rows=None, ccd_cols=None, ccd_codes=None, ccd_sides=None)

    INPUT
    num_cycles     : number of image cycles to be acquired at every position in the FoV
    exposure_time  : exposure time [cycle_time will be computed from it]
    angles         : field angles to be visited
                     [theta,phi] (commanding manual)
                     array [n,2] with n = nb of FoV positions to visit
    ccd_rows, ccd_cols, ccd_codes, ccd_sides : (distorted) CCD coordinates corresponding to the FoV positions in 'angles'

    n_rows         : number of rows read (partial readout)

    SYNOPSIS
    Visit each of the FoV positions defined by angles (must correspond to ccd_rows, ccd_cols, ccd_codes, ccd_sides)

    At each of these positions, acquire num_cycle images with an exposure time of "exposure_time".

    The FEEs are operated under partial readout. The region of interest is centered on "angles" and is made of n_rows rows

    """

    # TEST STARTING CONDITIONS (SYSTEM IN IDLE MODE)
    # system_test_if_idle()

    if num_cycles <= 0:
        print(f"ERROR: Forbidden value of parameter 'num_cycles' for this building block: {num_cycles=}. "
              f"Try a positive value")
        return None

    # DATA PREPARATION
    ##################

    # FOV Locations
    npos = len(ccd_rows)
    theta_array, phi_array = angles[:,0], angles[:,1]

    if angles.shape[0] != npos:
        print("Size Mismatch in 'angles'")
        return None
    if (len(ccd_sides)!= npos) or (len(ccd_cols)!=npos) or (len(ccd_codes)!=npos):
        print("Size mismatch on CCD coordinates")
        return None

    # CORE OF THE TEST
    ##################

    for pos in range(npos):

        # Move the stages to illuminate pixel (theta, phi)
        theta, phi = theta_array[pos],phi_array[pos]

        csl_point_source_to_fov(theta=theta, phi=phi, wait=True, theta_correction=theta_correction, sma_correction=sma_correction)
        visit_field_angles(theta, phi)

        n_fee_parameters = dict()
        n_fee_parameters["num_cycles"] = num_cycles
        n_fee_parameters["row_start"] = max(0, ccd_rows[pos] - n_rows // 2)
        n_fee_parameters["row_end"] = min(4509, ccd_rows[pos] + n_rows // 2)
        n_fee_parameters["rows_final_dump"] = 4510
        n_fee_parameters["ccd_order"] = [ccd_codes[pos], ccd_codes[pos], ccd_codes[pos], ccd_codes[pos]]
        # n_fee_parameters["ccd_side"] = [ccd_sides[pos], ccd_sides[pos], ccd_sides[pos], ccd_sides[pos]]
        n_fee_parameters["ccd_side"] = ccd_sides[pos]

        # Acquire images with diff exposure times

        for exposure_time in exposure_times:

            dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

        dpu.n_cam_to_dump_mode_int_sync()

    # RESET SYSTEM IN STANDARD CONDITIONS, i.e. IDLE MODE
    # system_to_idle()
