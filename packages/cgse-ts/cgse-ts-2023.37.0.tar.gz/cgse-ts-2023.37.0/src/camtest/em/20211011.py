from camtest import start_observation, end_observation, execute
from camtest.commanding import ogse, dpu
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from egse.setup import load_setup

setup = load_setup()

# AEU already powered on + syncing

# DPU already in dump mode

# OGSE switch-on

start_observation("Switch on procedure: OGSE")  # obsid = 844

ogse.ogse_swon()
ogse.ogse_set_attenuation_level(fwc_fraction=0.8)

print(ogse.att_get_factor())
print(ogse.att_is_ready())

end_observation()

# DPU to internal sync mode

execute(dpu.n_cam_to_dump_mode_int_sync)


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE -------------------------------------------------

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(
    anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

sma_correction = False
theta_correction = False

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width)  # obsid = 846

# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

# aeu.n_cam_sync_disable()
# aeu.n_cam_swoff()

ogse.ogse_swoff()

end_observation()
