import logging

import numpy as np

from camtest import execute
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from egse.settings import Settings

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

distorted = True
verbose = True


# STRAIGHT LINES

thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])

phis = np.ones_like(thetas) * 135.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)



####################################################
# PARAMETERS
####################################################

# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = .2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)
