import logging
import os

from rich import print

from camtest import GlobalState
from camtest import end_observation
from camtest import execute
from camtest import load_setup
from camtest import start_observation
from camtest.analysis.convenience import printm
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.commanding.csl_gse import is_model_sync
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.hexapod.symetrie.puna import PunaProxy
from egse.settings import Settings

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

rot_config = "sxyz"

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")

time_step = 1.

verbose = True


# LOAD SETUP ---------------------------------------------------------------------------------------

setup = load_setup()
print(setup)  # Setup 75 ??

GlobalState.load_setup()
GlobalState.setup.get_id()


# SYSTEM SWITCH ON ---------------------------------------------------------------------------------

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = 556

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

# On the server: dpu_cs start
# On the server: fitsgen start
# On the server: python -m egse.fee.n_fee_hk -platform offscreen

# On the client: dpu_ui

dpu.n_cam_to_standby_mode()

# Wait until in standby mode

dpu.n_cam_to_dump_mode_int_sync()

end_observation()

start_observation("Switch on procedure: OGSE")  # obsid = 557

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()

end_observation()


# PERFORM THE '8-DEG CIRCLE' as a reference measurement --------------------------------------------


# Test position - test image to confirm everything is alright

execute(csl_point_source_to_fov,
        theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False)  # obsid = CSL_00080_00558

n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid = CSL_00080_00559


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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00560


# Load the model and check if in sync with Hexapod -------------------------------------------------

hexhw = PunaProxy()

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

is_model_sync(model, hexhw)


# Check if we are on Hartmann plane ----------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])





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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00562


#########################################################
# ROTATE // TO TOU_MECH
#########################################################

is_model_sync(model, hexhw)

## ADJUST THE ROTATION VECTOR TO SET THE DETECTOR PERPENDICULAR TO THE OPTICAL AXIS

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec"))
printm([trans, rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# REPEAT THE 8-DEG CIRCLE AT THE BIP

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00564


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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00565

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec"))
printm([trans, rot])
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])



# MOVE TO THE BIP ----------------------------------------------------------------------------------


is_model_sync(model, hexhw)

## FINAL MINI-TRANSLATION WITH THE COMPLETE TRANSLATION VECTOR

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans, rot])

vtrans = trans
vrot = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans, rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# REPEAT THE 8-DEG CIRCLE AT THE BIP

execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00567



# FULL HARTMANN VERIFICATION, AT THE BIP -----------------------------------------------------------

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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00568



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
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00569


# end of measurements on 20/09/2021 ------------------------------------------------------------------------------------
# NOT QUITE, we started up again to do one more measurement.... see further...


# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()
ogse.ogse_swoff()

end_observation()



# SYSTEM SWITCH ON ---------------------------------------------------------------------------------

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_00080_00571

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

# On the server: dpu_cs start
# On the server: fitsgen start
# On the server: python -m egse.fee.n_fee_hk -platform offscreen

# On the client: dpu_ui

dpu.n_cam_to_standby_mode()

# Wait until in standby mode

dpu.n_cam_to_dump_mode_int_sync()

end_observation()

start_observation("Switch on procedure: OGSE")  # obsid = CSL_00080_00572

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()

end_observation()

# Load the model and check if in sync with Hexapod --------------------------------------------------

hexhw = PunaProxy()

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

is_model_sync(model, hexhw)

# MODEL IS NOT IN SYNC ANYMORE AND I MADE THE MISTAKE NOT TO SAVE THE MODEL
# SO, GOING HOME AFTER ALL.
# WHEN BACK WE NEED TO PUT THE HEXAPOD INTO ZERO POSITION AND BRING IT STEPWISE BACKT TO HARTMANN

# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()
ogse.ogse_swoff()

end_observation()
