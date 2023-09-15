from camtest import load_setup, submit_setup, start_observation, end_observation, execute
from camtest.commanding import aeu, dpu, ogse, _convert_n_fee_parameters
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position, csl_point_source_to_fov
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth, fov_geometry_from_table
from egse.hexapod.symetrie.puna import PunaProxy

import numpy as np

setup = load_setup()    # setup 84

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_00080_00591

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()

# On the client: dpu_ui

execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode

print(dpu.n_cam_is_standby_mode())

execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())

start_observation("Switch on procedure: OGSE")  # obsid = 624

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())

end_observation()

# Move the hexapod to the zero position

execute(hexapod_puna_goto_zero_position, wait=True)

# Now run csl_alignment_fpa_prealigment

hexhw = PunaProxy()

usrtrans,usrrot = model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
objtrans,objrot = model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

rounding = 6
usrtrans = np.round(usrtrans, rounding)
usrrot = np.round(usrrot, rounding)
objtrans = np.round(objtrans, rounding)
objrot = np.round(objrot, rounding)

hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

is_model_sync(model, hexhw)

verbose = True

# Compensate rotation

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [0,0,0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


# Just for fun :)

trans, rot = model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

# Compensate x, y

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [trans[0], trans[1],0]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Move up

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 6.9212]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Move up

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 6.0]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Change the speed of the hexapod movements

hexhw.set_speed(0.1, 0.1)

# Move up

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 4.0]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Move up

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 1.0]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Last adjustment

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# WE ARE AT HARTMAN NOW

# Take a reference image

execute(csl_point_source_to_fov,
        theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False)  # obsid = 634


n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid = 635


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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 636



# FULL HARTMANN VERIFICATION -----------------------------------------------------------------------

# 'PRE-UNDOING' THE OPTICAL DISTORTION (i.e. avoid to incl. it twice in the meas wrt LDO)

distorted = True
distorted_input = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 637 (aborted)

# Big rotation stage started moving in the wrong direction
# Do relative movement of the big rotation stage over 90 degrees (done from the stages UI)
# Do absolute movement of the big rotation stage to 0 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 638 (aborted)


# Big rotation stage started moving in the wrong direction
# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  #  obsid = 639


# Move to the bolting plane

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("bolt"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

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

# Do a relative movement of the big rotation stage over 180 degrees (from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 641



# FULL HARTMANN VERIFICATION -----------------------------------------------------------------------

# 'PRE-UNDOING' THE OPTICAL DISTORTION (i.e. avoid to incl. it twice in the meas wrt LDO)

distorted = True
distorted_input = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 642




# Move to the Hartmann plane

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# At the Hartmann plane, use the tilt of TOU_BIP

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE -------------------------------------------------

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 645


# At the Hartmann plane, use the tilt of TOU_MECH

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

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

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 647

# At the Hartmann plane, use the tilt of TOU_LOS

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toulos"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

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

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 649


# Go back to the Hartmann plane

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Move half a pixel in x

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0.009, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 652


# Move half a pixel in y (we keep the shift over half a pixel in x)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0.009, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 654

# Go back to the Hartmann plane

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE (17 cycles) -------------------------------------------------

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
num_cycles = 17

sma_correction = False
theta_correction = False

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 656


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE at 12.4 degrees -------------------------------------------------

boresight_angle = 12.4
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

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 657


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE at 16.33 degrees -------------------------------------------------

boresight_angle = 16.33
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

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 658


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE at 3.1 degrees -------------------------------------------------

boresight_angle = 3.1
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

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 659

# At the Hartmann plane, use the tilt of TOU_BIP

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# Do relative movement of the big rotation stage over 180 degrees (done from the stages UI)

# Execute cam_aat_050_ambient_visit_ccd_xys_prep.py (9 positions, 11 exposure times)   obsid: 661

# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()
ogse.ogse_swoff()

end_observation()


# Move to the bolting plane

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("bolt"))
printm([trans, rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


csl_dict = model.serialize()
setup.csl_model.model = csl_dict
setup.csl_model.laser_tracker_data = "006_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"
print(setup)
setup = submit_setup(
    setup, "CSLReferenceFrameModel EM 006 20210927 - bringing FPA at bolting plane"
)
print(setup)    # 86


setup = load_setup()




from egse.dpu import DPUProxy
dpu_proxy = DPUProxy()
dpu_proxy.n_fee_set_internal_sync({})


start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_00080_00591

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()

# On the client: dpu_ui

execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode

print(dpu.n_cam_is_standby_mode())

n_fee_parameters = dict(
    row_start=0,
    row_end=10,
    rows_final_dump=4509,
    ccd_order=[1, 2, 3, 4],
    ccd_side='BOTH',
    cycle_time=2.5,
)
dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
dpu_proxy.n_fee_set_internal_sync(dpu_pars)


execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())



execute(dpu.n_cam_to_on_mode)
execute(dpu.n_cam_to_standby_mode)
execute(dpu.n_cam_to_dump_mode_int_sync)


start_observation("Switch on procedure: OGSE")

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())

end_observation()



boresight_angle = 8.3
n_pos = 4

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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 682


# FULL HARTMANN VERIFICATION -----------------------------------------------------------------------

# 'PRE-UNDOING' THE OPTICAL DISTORTION (i.e. avoid to incl. it twice in the meas wrt LDO)

distorted = True
distorted_input = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = 683 (aborted)

# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()

ogse.ogse_swoff()

end_observation()
