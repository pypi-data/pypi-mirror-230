import logging
import os

from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest import submit_setup  # building_block
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
# Scripts
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates, fov_geometry_from_table
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth
from egse.settings import Settings

# from egse.coordinates.avoidance import is_avoidance_ok
# Hexapod


CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

# Convenience functions
def printm(matrix, rounding=4):
    print(np.round(matrix, rounding))


def positions_match(hexapod, hexsim, atol=0.0001, rtol=0.0001):
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)


def is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    if verbose is None: verbose = ""

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(model.get_frame('hexobj'))
    coomod = np.concatenate([coomodtr, coomodrot])

    print(f"{verbose}Hexapod   : {np.round(coohex, rounding)}")
    print(f"{verbose}Model     : {np.round(coomod, rounding)}")
    print(f"{verbose}Diff      : {np.round(coohex - coomod, rounding)}")

    print(f"{verbose}In synch  : {np.allclose(coohex, coomod, atol=atol, rtol=rtol)}")

    return


def hex_positions(hexapod, rounding=3):
    """
    Print User and machine coordinates of the input Hexapod

    Parameters
    ----------
    hexapod : Hexapod

    Returns
    -------
    None

    """
    print(f"OBJ vs USR: {np.round(hexapod.get_user_positions(), rounding)}")
    print(f"PLT vs MEC: {np.round(hexapod.get_machine_positions(), rounding)}")
    return


rot_config = "sxyz"

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")

time_step = 1.

setup = load_setup()
print(setup)  # Setup 63

GlobalState.load_setup()
GlobalState.setup.get_id()  # Setup 65
start_observation("Switch on procedure: AEU and N-FEE to STANDBY")  # obsid=CSL_00071_00448

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)


# On the server : dpu_cs start
dpu.n_cam_to_standby_mode()

end_observation()


execute(dpu.n_cam_to_dump_mode_int_sync)

execute(ogse.ogse_swon)
execute(ogse.set_fwc_fraction, fwc_fraction=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()


### RUN csl_alignment_fpa_prealignement_as_run_20210909
### UNTIL STATEMENT "READY" on line 463


execute(csl_point_source_to_fov, theta=0., phi=0., wait=True, theta_correction=False, sma_correction=False) # obsid 453

execute(csl_point_source_to_fov, theta=0., phi=0., wait=True, theta_correction=True, sma_correction=False) # obsid 454


### THE HEXAPOD IS AT ZERO-POSITION


is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0.8914  0.4805 18.0496]
#  [ 0.175  -0.1543  0.2363]]

vtrans = [0,0,0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# CORRECTING X-Y TRANSLATION
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [trans[0],trans[1],0]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# START MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 1.00000e-04 -2.00000e-04  1.80445e+01]
#  [-0.00000e+00 -0.00000e+00 -0.00000e+00]]

vtrans = [0,0,7]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 2.40000e-03  1.05000e-02  1.10445e+01]
#  [-0.00000e+00 -0.00000e+00 -0.00000e+00]]

vtrans = [0,0,5.0445]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 4.00e-03  1.82e-02  6.00e+00]
#  [-0.00e+00 -0.00e+00 -0.00e+00]]

vtrans = [0,0,3]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0.005   0.0228  3.    ]
#  [-0.     -0.     -0.    ]]

vtrans = [0,0,2]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0.0057  0.0258  1.    ]
#  [-0.     -0.     -0.    ]]

vtrans = trans
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0.0003  0.0015 -0.    ]
#  [-0.     -0.     -0.    ]]

vtrans = trans
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]

# Test position
execute(csl_point_source_to_fov, theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False) # obsid 425

n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid


#### COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE

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


# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

### UPDATE ambient_recentering script to include theta_correction

import camtest
import importlib

importlib.reload(camtest)
importlib.reload(camtest.commanding.cam_aat_050_ambient_recentering)

from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering


sma_correction   = False
theta_correction = True


# obsid 467
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

# CIRCLE at 12.4

boresight_angle = 12.4
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

# obsid 468
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

# CIRCLE at 3.1

boresight_angle = 3.1
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

# obsid 469
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

# CIRCLE at 16.33

boresight_angle = 16.33
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

# obsid 470
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)






# HARTMANN VERIFICATION


distorted = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,[ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1

# obsid 471 -- INTERRUPTED -- BIG RS STARTED IN THE WRONG DIRECTION, CROSSING -180.
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

# Manual commanding of relative moves of the BIG RS from Leuven

# obsid 472
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)


import numpy as np
# RADIAL - CCD1
thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])
phis = np.ones_like(thetas) * 135.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

# obsid 473
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

### SAVING THE CSL_MODEL AT THE HARTMANN POSITION
is_model_sync(model,hexhw)
csl_dict = model.serialize()
setup.csl_model.model = csl_dict
print(setup)
setup = submit_setup(setup, "CSLReferenceFrameModel EM 004 20210909 EOB - FPA at Hartmann plane")
print(setup)


# RADIAL - CCD4
thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])
phis = np.ones_like(thetas) * 45.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

# obsid 474
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)

# RADIAL - CCD3
thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])
phis = np.ones_like(thetas) * -45.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

# obsid 475
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)



# RADIAL - CCD2
thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])
phis = np.ones_like(thetas) * -135.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

# obsid 476
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)



execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)
execute(ogse.ogse_swoff)

# Stop DPU CS
# Stop FITS generator
# Stop    python -m egse.fee.n_fee_hk -platform offscreen
