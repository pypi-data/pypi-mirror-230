import logging

from camtest import list_setups, execute
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import equi_surface_fov_geometry, sort_on_azimuth
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from egse.settings import Settings
from egse.state import GlobalState

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

####################################################
# SETUP
####################################################

list_setups()

setup = GlobalState.setup

####################################################
# FOV GEOMETRY DEFINITION
####################################################

distorted_input = True
distorted = True

verbose = True
use_computed_fov_pos = False
sort_fov_pos_in_azimuth = True
reverse_azimuth_order = False

table_name = 'reference_full_40'
use_angles = False

if use_computed_fov_pos:

    setup.camera.fov.radius_mm = 81.52

    cells = [1, 2, 3, 4]
    boost, boostFactor = 1, 1
    distorted = True

    ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
        equi_surface_fov_geometry(cells=cells, boost=boost, boostFactor=boostFactor, distorted=distorted, verbose=True)
else:

    ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
        fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, table_name=table_name,
                                use_angles=use_angles, verbose=verbose)

if sort_fov_pos_in_azimuth:
    angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig,
                                                                                  ccdcodesorig, ccdsidesorig],
                                                                     reverse=reverse_azimuth_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1

####################################################
# PARAMETERS
####################################################

# OGSE attenuation level : 0 = dark; 1 = no attenuation.
#ogse_attenuation = 0.8

# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)
