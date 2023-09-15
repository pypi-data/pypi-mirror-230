import logging

import numpy as np

from camtest import list_setups, load_setup, execute
from camtest.commanding.cam_aat_050_ambient_visit_ccd_xys import cam_aat_050_ambient_visit_ccd_xys
from camtest.commanding.functions.fov_test_geometry import ccd_coordinates_to_angles
from egse.settings import Settings

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

####################################################
# SETUP
####################################################

list_setups()

setup = load_setup()

####################################################
# DEFINITION OF FOV LOCATIONS TO VISIT
####################################################
verbose = True

ccdxys = np.array([[250,150], [1250, 150], [2250,150], [3250,150], [4250,150],
                    [250,1150], [1250, 1150], [2250,1150], [3250,1150], [4250,1150],
                    [250,2150], [1250, 2150], [2250,2150], [3250,2150], [4250,2150]])
ccdrows = ccdxys[:,0]
ccdcols = ccdxys[:,1]

ccdcodes = np.array([3 for i in range(len(ccdrows))])
fee_side = setup.camera.fee.ccd_sides.enum
ccdsides = np.array([fee_side.LEFT_SIDE.name for i in range(len(ccdrows))])
ccdsides[np.where(ccdcols > 2254)[0]] = fee_side.RIGHT_SIDE.name

angles = ccd_coordinates_to_angles(ccdrows, ccdcols, ccdcodes, verbose=verbose)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1

####################################################
# PARAMETERS
####################################################

# Nb of rows to readout
width = 1000

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_times = [0.1, 0.2, 0.4, 0.5, 1., 2., 3., 4., 5., 7.5, 10.]

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

sma_correction   = False
theta_correction = False

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_visit_ccd_xys, num_cycles=num_cycles, exposure_times=exposure_times, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)
