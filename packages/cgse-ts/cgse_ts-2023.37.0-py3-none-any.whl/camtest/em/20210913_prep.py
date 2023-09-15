import logging
import os

import numpy as np
from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest import submit_setup  # building_block
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.csl_gse import check_and_move_relative_user
# from camtest.commanding import system_to_idle, system_test_if_idle, system_to_initialized, system_test_if_initialized
from camtest.commanding.csl_gse import csl_point_source_to_fov
# Scripts
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy
# Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.settings import Settings

# from egse.coordinates.avoidance import is_avoidance_ok


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

verbose = True

################
## LOAD SETUP
################

# MUST CONTAIN NEW EXCELL SHEET
setup = load_setup()
print(setup)  # Setup 75+

GlobalState.load_setup()
GlobalState.setup.get_id()


################
## SYSTEM SWON
################



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

### COMMANDS TO BE PASSED ON THE TERMINAL:
# Start DPU CS
# Start FITS generator
# $python -m egse.fee.n_fee_hk -platform offscreen




################
## SEND THE HEXAPOD BACK TO ZERO POSITION, TO HAVE ITS POSITION IN SYNC WITH THE MODEL (WE'LL INGEST A NEW MODEL)
################

is_model_sync(model, hexhw)

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

execute(hexapod_puna_goto_zero_position, wait=True)  # obsid

is_model_sync(model, hexhw)

hex_positions(hexhw)  # hex plate should be at zero position

# THE HEXAPOD IS AT ZERO-POSITION




################################################
## INGESTING THE NEW REF. FRAME MODEL
################################################

### Equivalent to  csl_alignment_fpa_prealignement_as_run_20210909
### UNTIL STATEMENT "READY" on line 463


# All ReferenceFrames measured or defined in CSL, i.e. all in the excelll sheet are expressed wrt gliso
predef_refs={}
predef_refs['Master'] = 'Master'

# CSL GSE
predef_refs['gliso']  = 'Master'     # csl
predef_refs['glfix']  = 'glrot'      # csl
predef_refs['glrot']  = 'gliso'      # csl

# HEXAPOD
predef_refs['hexiso'] = 'gliso'      # csl (originally hex_mec)
#predef_refs['hexplt'] ='gliso'       # csl
#predef_refs['hexobj'] = 'gliso'     # csl
#predef_refs['hexusr'] = 'gliso'      # csl
#predef_refs['hexmec'] = 'hexiso'
#predef_refs['hexobusr'] = 'hexusr'

# FPA
predef_refs['fpaaln'] = 'gliso'      # csl
predef_refs['fpamec'] = 'gliso'      # csl
predef_refs['fpasen'] = 'gliso'      # csl

# TOU
predef_refs['toumec'] = 'gliso'      # csl
predef_refs['toualn'] = 'gliso'      # csl
predef_refs['toulos'] = 'gliso'      # csl
predef_refs['toul6']  = 'gliso'      # csl

predef_refs['toubip'] = 'gliso'     # csl
predef_refs['bipcoord'] = 'gliso'     # csl
predef_refs['bipxls'] = 'gliso'     # csl
predef_refs['bolt'] = 'gliso'     # csl

# HARTMANN PLANE
predef_refs['hartmann'] = 'toumec'

# CAMERA
predef_refs['marialn'] = 'toualn'
predef_refs['camint'] = 'toumec'
predef_refs['cammec'] = 'toumec'
predef_refs['cammec'] = 'toumec'
predef_refs['cambor'] = 'toualn'


setup.csl_model = {}
setup.csl_model.default_refs = predef_refs

filexls = "/data/CSL/conf/004_csl_refFrames_EM_TOU_alignment_final_after_torque_with_BIP_coord.xls"

refFrames = laser_tracker_to_dict(filexls,setup)  # -> dict

#for k,v in zip(refFrames.keys(), refFrames.values()):
#    print(f"{k:>10} -- {v.split('|')[-3]}[{v.split('|')[-2]}]")

model = CSLReferenceFrameModel(refFrames)

print(model.summary())


###########################
# COMPLETE THE  MODEL
###########################

"""
The hexapod frames hex_plt, hex_obj, hex_usr must be explicitly defined wrt hex_mec
So they are deleted from the excell sheet and set to I (hex_plt) or derived from fpasen (hexobj) and toul6 (hexusr)
"""

zeros = [0,0,0]

# HEX_MEC
model.add_frame(name="hexmec", translation=zeros, rotation=zeros, ref="hexiso")

# HEX_PLT --> HEX_MEC -- no link
model.add_frame(name="hexplt", translation=zeros, rotation=zeros, ref="hexmec")

# HEX_USR --> HEX_MEC
transformation = model.get_frame("hexmec").getActiveTransformationTo(model.get_frame("toul6"))
model.add_frame(name="hexusr", transformation=transformation, ref="hexmec")

# HEX_OBJ == FPA_SEN--> HEX_PLT
transformation = model.get_frame("hexplt").getActiveTransformationTo(model.get_frame("fpasen"))
model.add_frame(name="hexobj", transformation=transformation, ref="hexplt")

# HEX_OBUSR
transformation = model.get_frame("hexusr").getActiveTransformationTo(model.get_frame("hexobj"))
model.add_frame(name="hexobusr", transformation=transformation, ref="hexusr")

print(model.summary())

# INCLUDE THE LINKS
model.add_link("Master", "gliso")
model.add_link("glrot", "gliso")

# # HEXAPOD
model.add_link("hexiso", "gliso")
model.add_link("hexmec", "hexiso")
model.add_link("hexobj", "hexplt",)
model.add_link("hexobj", "hexobusr")
model.add_link("hexusr", "hexmec")

model.add_link("fpasen", "hexobj",)
model.add_link("fpasen", "fpamec")
model.add_link("fpamec", "fpaaln")

model.add_link("toul6", "hexusr")
model.add_link("toul6", "toumec")
model.add_link("toumec", "gliso")
model.add_link("toumec", "toualn")
model.add_link("toulos", "toualn")
model.add_link("toubip", "toumec")
model.add_link("bipcoords", "toumec")
model.add_link("bipxls", "toumec")
model.add_link("bolt", "toumec")

model.add_link("hartmann", "toumec")

model.add_link("camint", "toumec")

# WE MUST STILL DEFINE MARI_ALN & CAM_BOR

print(model.summary())

###########################
# SAVE THE  MODEL
###########################

csl_dict =  model.serialize()

setup.csl_model.model =  csl_dict

"""
setup = submit_setup(setup,"CSLReferenceFrameModel EM 004 - zero position")

setup = load_setup()
"""

###########################
# SANITY CHECKS ON THE NEW MODEL
###########################

printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
#[0,0,0][0,0,0]

printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
printm(model.get_frame("hexobj").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
# After torquing
# [[ 1.4073  0.5034 21.3677]
#  [ 0.2624 -0.173   0.2486]]
# Before torquing
# [[ 1.3971  0.5508 21.3297]
#  [ 0.2717 -0.1728  0.2595]]
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec")))
# [[ 0.9901  0.2022 86.1116]
#  [ 0.2624 -0.173   0.2486]]
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toulos")))
# [[-8.21854e+01 -8.40897e+01  2.15693e+02]
#  [ 7.53000e-02  3.99000e-02  5.00500e-01]]
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# After torquing
# [[ 1.3727  0.6868 17.852 ]
#  [ 0.2275 -0.1801  0.2363]]
# Before torquing
# [[ 1.8054  0.6348 18.1375]
#  [ 0.2594 -0.1427  0.4101]]
printm(model.get_frame("toubip").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))
# After torquing
# [[ -1.4316  -0.752  -17.8447]
#  [ -0.2282   0.1791  -0.237 ]]
# Before torquing
# [[ -1.8551  -0.7039 -18.13  ]
#  [ -0.2604   0.1408  -0.4108]]
printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# After torquing
# [[ 1.7860e-01  1.7030e-01 -6.8262e+01]
#  [-3.4900e-02 -7.2000e-03 -1.2200e-02]]
printm(model.get_frame("camint").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# After torquing

printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")))
# After torquing
# [[-3.0300e-01 -3.3000e-02 -6.8062e+01]
#  [-8.7400e-02  1.8700e-02 -1.2400e-02]]
# Before torquing
# [[-3.0300e-01 -3.3000e-02 -6.8062e+01]
#  [-8.7400e-02  1.8700e-02 -1.2400e-02]]
printm(model.get_frame("hartmann").getActiveTranslationRotationVectorsTo(model.get_frame("toumec")))
# After torquing
# [[ 2.80800e-01 -7.08000e-02  6.80621e+01]
#  [ 8.74000e-02 -1.87000e-02  1.23000e-02]]
# Before torquing
# [[ 2.80800e-01 -7.08000e-02  6.80621e+01]
#  [ 8.74000e-02 -1.87000e-02  1.23000e-02]]
printm(model.get_frame("hartmann").getActiveTranslationRotationVectorsTo(model.get_frame("camint")))
# After torquing
# [[ 0.1712 -0.1149 66.831 ]
#  [ 0.0934 -0.1022  0.    ]]
# Before torquing
# [[ 0.1712 -0.1149 66.831 ]
#  [ 0.0934 -0.1022  0.    ]]
printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"),4))
# After torquing
# [[ 1.519000e-01  4.780000e-02  5.384386e+02]
#  [ 8.910000e-02 -1.996000e-01 -1.199378e+02]]
# Before torquing
# [[ 1.976000e-01  3.250000e-02  5.384006e+02]
#  [ 9.840000e-02 -1.993000e-01 -1.199269e+02]]
printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("toulos"),4))
# After torquing
# [[-3.086700e+01  1.143630e+02  7.361420e+02]
#  [-1.080000e-02 -5.000000e-03 -1.196739e+02]]
# Before torquing
# [[-3.08710e+01  1.14357e+02  7.36091e+02]
#  [-1.50000e-03 -4.80000e-03 -1.19663e+02]]
printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("toualn"),4))
# After torquing
# [[-3.086700e+01  1.143630e+02  7.361420e+02]
#  [ 1.658000e-01 -3.056000e-01 -1.196747e+02]]
# Before torquing
# [[-3.087100e+01  1.143570e+02  7.360910e+02]
#  [ 1.751000e-01 -3.054000e-01 -1.196639e+02]]
printm(model.get_frame('hartmann').getActiveTranslationRotationVectorsTo(model.get_frame("toubip"),4))
# After torquing
# [[ 4.816e-01  2.037e-01 -1.996e-01]
#  [ 5.250e-02 -2.580e-02  1.000e-04]]
printm(model.get_frame('toualn').getActiveTranslationRotationVectorsTo(model.get_frame("toulos"),4))
# [[-0.      0.      0.    ]
#  [-0.1766  0.3006 -0.    ]]
printm(model.get_frame('toumec').getActiveTranslationRotationVectorsTo(model.get_frame("toualn"),4))
# [[-8.31489e+01 -8.33347e+01  1.30216e+02]
#  [-9.70000e-03 -8.65000e-02  2.51000e-01]]


###############################################################################
#
# CONNECT TO HEXAPOD
#
###############################################################################

try:
    #hexhw = PunaController()
    #hexhw.connect()
    hexhw  = PunaProxy()
    hexhw.info()
except HexapodError:
   hexhw = PunaSimulator()
except NotImplementedError:
   hexhw = PunaSimulator()

print(f"Hexapod HW is simulator: {hexhw.is_simulator()}")


###############################################################################
#
# CONFIGURE HEX_USR WRT THE MEASURED POSITION OF TOU L6S2 (Laser Tracker)
#
###############################################################################

# Abs position of L6S2, in mm above the hexmec (== zero position)

usrtrans,usrrot = model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
objtrans,objrot = model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

rounding = 6
usrtrans = np.round(usrtrans,rounding)
usrrot = np.round(usrrot,rounding)
objtrans = np.round(objtrans,rounding)
objrot = np.round(objrot,rounding)

hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

###############################################################################
#
# VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
#
###############################################################################

is_model_sync(model,hexhw)

#
# READY - THE HEXAPOD IS AT ZERO-POSITION, THE MODEL IS IN SYNC
#

###############################################################################
#
# MOVE THE HEXAPOD TO THE HARTMANN PLANE
#
###############################################################################

# CORRECTING THE ROTATIONS

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

##
## UPATE THE Z-TRANSLATIONS TO YOUR LIKINGS
##

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

## MOVING UP -- THIS TIME WE INCLUDE THE COMPLETE TRANSLATION VECTOR
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])
# [[ 0.0057  0.0258  1.    ]
#  [-0.     -0.     -0.    ]]

vtrans = trans
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


## FINAL MINI-TRANSLATION WITH THE COMPLETE TRANSLATION VECTOR
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

is_model_sync(model, hexhw)

#
# THE HEXAPOD IS AT THE HARTMANN PLANE
#

### SAVING THE CSL_MODEL AT THE HARTMANN POSITION
is_model_sync(model,hexhw)
csl_dict = model.serialize()
setup.csl_model.model = csl_dict
print(setup)
setup = submit_setup(setup, "CSLReferenceFrameModel EM 004 20210909 EOB - FPA at Hartmann plane")
print(setup)



########################################################
# PERFORM THE '8-DEG CIRCLE' as a reference measurement
########################################################


# Test position - test image to confirm everything is alright
# obsid
execute(csl_point_source_to_fov, theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False)

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

sma_correction   = False
theta_correction = True


# obsid
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)






#########################################################
# FULL HARTMANN VERIFICATION,
#########################################################
# 'PRE-UNDOING' THE OPTICAL DISTORTION (i.e. avoid to incl. it twice in the meas wrt LDO)

distorted = True
distorted_input = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,[ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1


# obsid
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)


#########################################################
# ROTATE // TO TOU_MECH
#########################################################

is_model_sync(model, hexhw)

## ADJUST THE ROTATION VECTOR TO SET THE DETECTOR PERPENDICULAR TO THE OPTICAL AXIS
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec"))
printm([trans,rot])

vtrans = [0,0,0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# REPEAT THE 8-DEG CIRCLE AT THE BIP
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)



#########################################################
# MOVE TO THE BIP
#########################################################

is_model_sync(model, hexhw)

## FINAL MINI-TRANSLATION WITH THE COMPLETE TRANSLATION VECTOR
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# REPEAT THE 8-DEG CIRCLE AT THE BIP
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)


#########################################################
# MOVE TO THE BOLT
#########################################################


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# REPEAT THE 8-DEG CIRCLE AT THE BOLT
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)





################
## SYSTEM SWOFF
################

execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)
execute(ogse.ogse_swoff)

# Stop DPU CS
# Stop FITS generator
# Stop    python -m egse.fee.n_fee_hk -platform offscreen
