"""Camera Test for the optical alignment of the FPA with respect to the TOU.

See Test Specification PLATO-KUL-PL-TS-0001.

Usage:

    >>> execute(cam_aat_050, <args>)

"""

import numpy as np
from scipy.interpolate import interp1d

from egse.settings import Settings
from egse.visitedpositions import visit_field_angles

CCD_SETTINGS = Settings.load("Field-Of-View")


from camtest import building_block, GlobalState
from camtest.commanding import dpu
from camtest.commanding.mgse import point_source_to_fov

from camtest.commanding.functions.csl_functions import focus_sweep

from camtest.commanding.functions.fov_test_geometry import equi_surface_fov_geometry

####################################################
## FOV GEOMETRY DEFINITION
####################################################

cells = [1,2,3,4,5]
boost, boostFactor = 1, 3
distorted = False

ccdrows, ccdcols, ccdcodes, ccd_sides, angles = equi_surface_fov_geometry(cells=cells, boost=boost, boostFactor=boostFactor, distorted=distorted, verbose=True)

# PLATO-KUL-PL-TN-0012
z_array = np.arange(-2.5, -7.6, -0.1)

exposure_times = np.array([2.5 for i in range(len(z_array))])


@building_block
def cam_aat_050_ambient_optical_alignment(z_array=None, num_cycles=None, exposure_times=None, angles=None,
                                          ccd_rows=None, ccd_cols=None, ccd_codes=None, ccd_sides=None,
                                          ogse_attenuations=None, setup=None):
    """
    z_array         : focus positions to visit, with respect to HEX_USER. Array of size nz
    exposure_times : exposure time for every z-position. Array of size nz
    angles         : field angles to be visited
                     [theta,phi] (commanding manual)
                     array [n,2] with n = nb of FoV positions to visit
    ccd_rows, ccd_cols, ccd_codes, ccd_sides : (distorted) CCD coordinates corresponding to the FoV positions in 'angles'
    ogse_attenuations : attenuation factors for the OGSE, for each position
                        if ommitted, it is computed from setup.ogse.ambient_attenuations_cal (nearest value after interpolation)

    """

    # DATA PREPARATION
    ##################

    # FOV Locations
    npos = len(ccd_rows)
    theta_array, phi_array = angles[:, 0], angles[:, 1]

    if angles.shape[0] != npos:
        print("Size Mismatch in 'angles'")
        return None
    if (len(ccd_sides) != npos) or (len(ccd_cols) != npos) or (len(ccd_codes) != npos):
        print("Size mismatch on CCD coordinates")
        return None

    # OGSE attenuations vs z-location

    if ogse_attenuations is None:
        if setup is None:
            setup = GlobalState.setup

            ogse_cal = setup.ogse.ambient_attenuations_cal

            cal_z = ogse_cal[:, 0]
            cal_att = ogse_cal[:, 1]

            interpolator = interp1d(cal_z, cal_att, kind='linear')

            attenuation_array = interpolator(zs)

    # CORE OF THE TEST
    ##################

    #for theta, phi in zip(theta_array,phi_array):
    for pos in range(npos):

            # Move the stages to illuminate pixel (theta, phi)
            theta, phi = theta_array[pos], phi_array[pos]

            point_source_to_fov(theta, phi, wait=True)
            visit_field_angles(theta, phi)

            n_fee_parameters = dict()
            n_fee_parameters["num_cycles"] = num_cycles
            n_fee_parameters["row_start"] = ccd_rows[pos]-width//2
            n_fee_parameters["row_end"] = ccd_rows[pos]+width//2
            n_fee_parameters["col_end"] = 2254
            n_fee_parameters["rows_final_dump"] = 4510
            n_fee_parameters["ccd_order"] = [ccd_codes[pos], ccd_codes[pos], ccd_codes[pos], ccd_codes[pos]]
            n_fee_parameters["ccd_side"] = [ccd_sides[pos], ccd_sides[pos], ccd_sides[pos], ccd_sides[pos]]

            # Perform the focus-sweep at current FoV location

            focus_sweep(zvalues=z_array, ogse_attenuations=attenuation_array, exposure_times=None,
                        n_fee_parameters=None, cslmodel=None, setup=None, ogse_to_default=None, verbose=True)
            # focus_sweep's calling this:
            #dpu.n_cam_partial_int_sync(num_cycles=None, row_start=None, row_end=None, col_end=None,rows_final_dump=None, ccd_order=None, ccd_side=None,exposure_time=None)

            cycle_time = n_fee_parameters["cycle_time"]
            ccd_order = n_fee_parameters["ccd_order"]
            dpu.n_cam_to_dump_mode_int_sync(cycle_time=cycle_time, ccd_order=ccd_order)
