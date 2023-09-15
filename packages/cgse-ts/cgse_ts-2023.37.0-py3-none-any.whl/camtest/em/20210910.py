# Test day 10/09/2021
#
# Running ambient_recentering at 8.3 degree, with theta_correction = False and True…
import logging
import os

import numpy as np
from rich import print

from camtest import GlobalState
from camtest import end_observation
from camtest import execute
from camtest import load_setup
from camtest import start_observation
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth
from egse.coordinates.cslmodel import CSLReferenceFrameModel
# Hexapod
from egse.hexapod.symetrie.puna import PunaProxy
from egse.settings import Settings

# from egse.coordinates.avoidance import is_avoidance_ok
# Scripts


CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)


# Convenience functions
def printm(matrix, rounding=4):
    print(np.round(matrix, rounding))


def positions_match(hexapod, hexsim, atol=0.0001, rtol=0.0001):
    return np.allclose(
        hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol
        )


def is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    if verbose is None:
        verbose = ""

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(
        model.get_frame('hexobj')
        )
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
print(setup)  # Should be Setup 73

GlobalState.load_setup()
GlobalState.setup.get_id()  # Should be Setup 73

start_observation("Switch on procedure: AEU and N-FEE to STANDBY")  # obsid=

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

# Load the current model

hexhw = PunaProxy()

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(
    model.get_frame("hartmann")
)
printm([trans, rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


#### COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = circle_fov_geometry(
    n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True
)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(
    anglesorig,
    [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
    reverse=reverse_order
)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")

for line_nr, (angle, crow, ccol, ccode, ccd_side) in enumerate(
        zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(
        f"{line_nr:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   "
        f"[{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}"
    )

sma_correction = False
theta_correction = True

# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

execute(
    cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time,
    angles=angles,
    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width,
    theta_correction=theta_correction, sma_correction=sma_correction
    )  # obsid=484

# In the previous obs, the cover was still on the TOU

execute(
    cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time,
    angles=angles,
    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width,
    theta_correction=theta_correction, sma_correction=sma_correction
    )  # obsid=485


theta_correction = False

execute(
    cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time,
    angles=angles,
    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width,
    theta_correction=theta_correction, sma_correction=sma_correction
    )  # obsid=486



### RESET THE HEXAPOD AT ZERO POSITION

from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position

# First goto z=-20

vtrans = [0, 0, -20]
vrot = [0, 0, 0]
verbose = True

move_ok = execute(
    check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup,
    verbose=verbose
    )

is_model_sync(model, hexhw)

model.hexapod_goto_zero_position()

# Now goto zero position

execute(hexapod_puna_goto_zero_position, wait=True)  # obsid=488

is_model_sync(model, hexhw)

hex_positions(hexhw)  # hex plate should be at zero position


# MOVE BACK TO HARTMANN PLANE IN SMALL STEPS

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

# CORRECTING ROTATION
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
printm([trans, rot])

vtrans = [0,0,7]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0,0,5.0445]  # see if the small z-correction should be adapted
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [0,0,3]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [0,0,2]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

## MOVING UP
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = trans  # fix the correction after moving up
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = trans  # fix again a second time
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

# trans and rot shall be zero!


### LICHTEN UIT!!!!


theta_correction = True

execute(
    cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time,
    angles=angles,
    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width,
    theta_correction=theta_correction, sma_correction=sma_correction
    )  # obsid=497

theta_correction = False

execute(
    cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time,
    angles=angles,
    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width,
    theta_correction=theta_correction, sma_correction=sma_correction
    )  # obsid=498

# Now save the model in a new Setup

# No need to save the current model, as the FPA is at the Hartmann plane
# and the Hexapod and the model are in sync.

# setup = load_setup()
# print(setup)  # Should be Setup 74
#
# is_model_sync(model, hexhw)
#
# csl_dict = model.serialize()
# setup.csl_model.model = csl_dict
# rich.print(setup)
# setup = submit_setup(
#     setup, "CSLReferenceFrameModel EM 004 20210910 EOB - FPA at the Hartmann plane"
#     )
# rich.print(setup)  # Should be Setup 75


execute(aeu.n_cam_sync_disable)  # obsid=499
execute(aeu.n_cam_swoff)  # obsid=500
execute(ogse.ogse_swoff)  # obsid=501

# -eob-
