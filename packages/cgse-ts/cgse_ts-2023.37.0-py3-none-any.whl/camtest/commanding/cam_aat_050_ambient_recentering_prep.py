import logging

from camtest import list_setups, load_setup, execute
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
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

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
                                                                 [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
                                                                 reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1

####################################################
# OGSE INTENSITY
####################################################

# OGSE attenuation level : 0 = dark; 1 = no attenuation.
ogse_attenuation = 1.
ogse.set_relative_intensity(relative_intensity=ogse_attenuation)

####################################################
# PARAMETERS
####################################################

# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5


# sma_correction   = False
# theta_correction = False

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)#, theta_correction=theta_correction, sma_correction=sma_correction)
