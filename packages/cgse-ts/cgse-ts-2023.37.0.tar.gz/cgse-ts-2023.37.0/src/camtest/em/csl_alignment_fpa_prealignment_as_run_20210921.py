"""
This script will regenerate the hexapod model based on a reference frame model provided by CSL.

"""

import numpy as np

from camtest import execute
from camtest import list_setups
from camtest import load_setup
from camtest.analysis.convenience import printm
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import hex_positions
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position
from camtest.commanding.csl_gse import is_model_sync
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.setup import submit_setup

###############################################################################
#
# CONFIGURE LARGER AVOIDANCE VOLUME
#
###############################################################################

list_setups()

setup = load_setup()
print(setup)


#########   CHECK FOR CLEARANCE IN SETUP

print(f"{setup.camera.fpa.avoidance.clearance_xy=}")
print(f"{setup.camera.fpa.avoidance.clearance_z=}")
print(f"{setup.camera.fpa.avoidance.vertices_nb=}")
print(f"{setup.camera.fpa.avoidance.vertices_radius=}")

"""
clearance_xy = 3
clearance_z = 0.3
vertices_nb = 60
vertices_radius = 100

setup.camera={}
setup.camera.fpa = {}
setup.camera.fpa.avoidance = {}
setup.camera.fpa.avoidance.clearance_xy = clearance_xy
setup.camera.fpa.avoidance.clearance_z = clearance_z
setup.camera.fpa.avoidance.vertices_nb = vertices_nb
setup.camera.fpa.avoidance.vertices_radius = vertices_radius

submit_setup(setup,"Incl fpa avoidance volume")
"""

# Clearance above HEX_OBJ : 5 mm
# setup.camera.fpa.avoidance.vertices_radius = 100.
# setup.camera.fpa.avoidance.clearance_xy = 2.
# setup.camera.fpa.avoidance.clearance_z = 2.


#########   INJECT AVOIDANCE VOLUME - SPECIFIC ReferenceFrameModel in setup


### All ReferenceFrames measured or defined in CSL, i.e. all in the excel sheet
### are expressed wrt gliso

predef_refs = {}
predef_refs['Master'] = 'Master'

# CSL GSE
predef_refs['gliso']  = 'Master'     # csl
predef_refs['glfix']  = 'glrot'      # csl
predef_refs['glrot']  = 'gliso'      # csl

# HEXAPOD
predef_refs['hexiso'] = 'gliso'      # csl (originally hex_mec)
predef_refs['hexplt'] = 'gliso'      # csl
predef_refs['hexobj'] = 'gliso'      # csl
predef_refs['hexusr'] = 'gliso'      # csl
#predef_refs['hexmec'] = 'hexiso'    # ?????????????????????????????????????????????????????????????
#predef_refs['hexobusr'] = 'hexusr'  # ?????????????????????????????????????????????????????????????

# FPA
predef_refs['fpaaln'] = 'gliso'      # csl
predef_refs['fpamec'] = 'gliso'      # csl
predef_refs['fpasen'] = 'gliso'      # csl

# TOU
predef_refs['toumec'] = 'gliso'      # csl
predef_refs['toualn'] = 'gliso'      # csl
predef_refs['toulos'] = 'gliso'      # csl
predef_refs['toul6']  = 'gliso'      # csl

predef_refs['toubip'] = 'gliso'      # csl
predef_refs['bolt'] = 'gliso'        # csl

# HARTMANN PLANE
predef_refs['hartmann'] = 'gliso'    # csl

# CAMERA
predef_refs['marialn'] = 'toualn'
predef_refs['camint'] = 'toumec'
predef_refs['cammec'] = 'toumec'
predef_refs['cambor'] = 'toualn'


setup.csl_model = {}
setup.csl_model.default_refs = predef_refs


###############################################################################
#
# LOAD XLS FILE & ASSEMBLE CSLREFERENCEFRAMEMODEL
#
###############################################################################

# Run csl_model up to the definition of HEX_OBUSR, or : simplified version below

###########################
# INITIALIZE MODEL FROM XLS
###########################


#filexls = input("Name of the laser tracker xls file ?")
#filexls = "/Users/pierre/plato/csl_refFrames_avoidance_test_tou.xls"
#filexls = "/Users/pierre/plato/csl_refFrames_TOU_alignment_EM_001.xls"
#filexls = "/Users/pierre/plato/csl_refFrames_TOU_alignment_EM_002_nohex.xls"
#filexls = "/Users/pierre/plato/003_csl_refFrames_TOU_alignment_EM_HartmannPlane.xls"
#filexls = "/Users/pierre/plato/004_csl_refFrames_EM_TOU_alignment_final_after_torque_with_BIP_coord.xls"
#filexls = "/Users/pierre/plato/005_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"

filexls = "/data/CSL/conf/005_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"

refFrames = laser_tracker_to_dict(filexls, setup)  # -> dict

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

zeros = [0, 0, 0]

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
#model.add_link("toumec", "toualn")   ??????????????????????????????????????????
#model.add_link("toulos", "toualn")
model.add_link("toubip", "toumec")
model.add_link("bolt", "toumec")

model.add_link("hartmann", "toumec")

#model.add_link("camint", "toumec")

# WE MUST STILL DEFINE MARI_ALN & CAM_BOR

print(model.summary())

#############################
# ADD THE MODEL TO THE SETUP
#############################

csl_dict = model.serialize()

setup.csl_model.model =  csl_dict

# ??????????????????????????????????????????????????????????????????????????????????????????????????
# ????? is model now at zero position?

setup = submit_setup(setup,"CSLReferenceFrameModel EM 005")
setup = load_setup()

###########################
# CROSS CHECK WITH LASER TRACKER SOFTWARE
###########################

# Before torquing = EM model 003
# After torquing = EM model 004
# Realign = EM model 005
printm(model.get_frame("hexobusr").getTranslationRotationVectors())
printm(model.get_frame("fpasen").getTranslationRotationVectors())
printm(model.get_frame("toubip").getTranslationRotationVectors())

printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))
printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))


printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
#[0,0,0][0,0,0]

printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")),4)
printm(model.get_frame("hexobj").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
# Realign
# [[1.25330e+00 3.52400e-01 2.14406e+01]
#  [8.62000e-02 4.40000e-02 1.37000e-02]]
# After torquing
# [[ 1.4073  0.5034 21.3677]
#  [ 0.2624 -0.173   0.2486]]
# Before torquing
# [[ 1.3971  0.5508 21.3297]
#  [ 0.2717 -0.1728  0.2595]]
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toumec")))
# Realign
# [[1.08010e+00 2.52300e-01 8.60536e+01]
#  [8.62000e-02 4.40000e-02 1.37000e-02]]
# [[ 0.9901  0.2022 86.1116]
#  [ 0.2624 -0.173   0.2486]]

#printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toulos")))
# Realign -- no TOU LOS in model 005
# After torquing
# [[-8.21854e+01 -8.40897e+01  2.15693e+02]
#  [ 7.53000e-02  3.99000e-02  5.00500e-01]]

printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# Realign
# [[1.0274  0.3555 17.7617]
#  [0.0513  0.0368  0.026]]
# After torquing
# [[ 1.3727  0.6868 17.852 ]
#  [ 0.2275 -0.1801  0.2363]]
# Before torquing
# [[ 1.8054  0.6348 18.1375]
#  [ 0.2594 -0.1427  0.4101]]
printm(model.get_frame("toubip").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))
# Realign
# [[ -1.0162  -0.3709 -17.7621]
#  [ -0.0512  -0.0369  -0.0259]]
# After torquing
# [[ -1.4316  -0.752  -17.8447]
#  [ -0.2282   0.1791  -0.237 ]]
# Before torquing
# [[ -1.8551  -0.7039 -18.13  ]
#  [ -0.2604   0.1408  -0.4108]]
printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# Realign
# [[-2.0000e-04  4.0000e-04 -6.8292e+01]
#  [-3.5000e-02 -7.2000e-03  1.2300e-02]]
# After torquing
# [[ 1.7860e-01  1.7030e-01 -6.8262e+01]
#  [-3.4900e-02 -7.2000e-03 -1.2200e-02]]

#printm(model.get_frame("camint").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# No CAM INT in model EM 005

printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")))
# Realign
# [[-2.0000e-04  4.0000e-04 - 6.8062e+01]
#  [-8.7400e-02  1.8700e-02  1.2200e-02]]
# After torquing
# [[-3.0300e-01 -3.3000e-02 -6.8062e+01]
#  [-8.7400e-02  1.8700e-02 -1.2400e-02]]
# Before torquing
# [[-3.0300e-01 -3.3000e-02 -6.8062e+01]
#  [-8.7400e-02  1.8700e-02 -1.2400e-02]]
printm(model.get_frame("hartmann").getActiveTranslationRotationVectorsTo(model.get_frame("toumec")))
# Realign
# [[-2.20000e-02 -1.04200e-01  6.80619e+01]
#  [ 8.74000e-02 -1.86000e-02 -1.22000e-02]]
# After torquing
# [[ 2.80800e-01 -7.08000e-02  6.80621e+01]
#  [ 8.74000e-02 -1.87000e-02  1.23000e-02]]
# Before torquing
# [[ 2.80800e-01 -7.08000e-02  6.80621e+01]
#  [ 8.74000e-02 -1.87000e-02  1.23000e-02]]

#printm(model.get_frame("hartmann").getActiveTranslationRotationVectorsTo(model.get_frame("camint")))
# Realign : no CAM INT in model EM 005
# After torquing
# [[ 0.1712 -0.1149 66.831 ]
#  [ 0.0934 -0.1022  0.    ]]
# Before torquing
# [[ 0.1712 -0.1149 66.831 ]
#  [ 0.0934 -0.1022  0.    ]]

printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"),4))
#Realign
# [[-2.500000e-02 - 7.000000e-03  5.383810e+02]
#  [-8.690000e-02  1.700000e-02 - 1.201485e+02]]
# After torquing
# [[ 1.519000e-01  4.780000e-02  5.384386e+02]
#  [ 8.910000e-02 -1.996000e-01 -1.199378e+02]]
# Before torquing
# [[ 1.976000e-01  3.250000e-02  5.384006e+02]
#  [ 9.840000e-02 -1.993000e-01 -1.199269e+02]]

#printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("toulos"),4))
# Realign : no TOU LOS in model EM 005
# After torquing
# [[-3.086700e+01  1.143630e+02  7.361420e+02]
#  [-1.080000e-02 -5.000000e-03 -1.196739e+02]]
# Before torquing
# [[-3.08710e+01  1.14357e+02  7.36091e+02]
#  [-1.50000e-03 -4.80000e-03 -1.19663e+02]]

#printm(model.get_frame('gliso').getActiveTranslationRotationVectorsTo(model.get_frame("toualn"),4))
# Realign : no TOU ALN in model EM 005
# After torquing
# [[-3.086700e+01  1.143630e+02  7.361420e+02]
#  [ 1.658000e-01 -3.056000e-01 -1.196747e+02]]
# Before torquing
# [[-3.087100e+01  1.143570e+02  7.360910e+02]
#  [ 1.751000e-01 -3.054000e-01 -1.196639e+02]]
printm(model.get_frame('hartmann').getActiveTranslationRotationVectorsTo(model.get_frame("toubip"),4))
# Realign
# [[ 1.00e-04  3.00e-04 -2.30e-01]
#  [ 5.24e-02 -2.58e-02  0.00e+00]]
# After torquing
# [[ 4.816e-01  2.037e-01 -1.996e-01]
#  [ 5.250e-02 -2.580e-02  1.000e-04]]

#printm(model.get_frame('toualn').getActiveTranslationRotationVectorsTo(model.get_frame("toulos"),4))
# [[-0.      0.      0.    ]
#  [-0.1766  0.3006 -0.    ]]
#printm(model.get_frame('toumec').getActiveTranslationRotationVectorsTo(model.get_frame("toualn"),4))
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


#execute(hexapod_puna_homing,wait=True)

#execute(hexapod_puna_goto_zero_position,wait=True)


###############################################################################
#
# CONFIGURE HEX_USR WRT THE MEASURED POSITION OF TOU L6S2 (Laser Tracker)
#
###############################################################################

# Abs position of L6S2, in mm above the hexmec (== zero position)

"""
#gl=0
mec = plt = 230.19
obj = 312.49
usr = 332.428

usr - obj # = 19.938
model.get_frame("hexobusr").getTranslationRotationVectors()

obj - plt # = 82.300
model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

usr - mec # = 102.238
model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
"""

usrtrans,usrrot = model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
objtrans,objrot = model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

rounding = 6
usrtrans = np.round(usrtrans,rounding)
usrrot = np.round(usrrot,rounding)
objtrans = np.round(objtrans,rounding)
objrot = np.round(objrot,rounding)


# ??????????????????????????????????????????????????????????????????????????????????????????????????
# ??? do we have to do this?
hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)


###############################################################################
#
# VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
#
###############################################################################

is_model_sync(model,hexhw)





###############################################################################
#
# READY
#
###############################################################################

verbose = True


"""
### ABSOLUTE MOVEMENT

vtrans = [0., 0., 0.]
vrot   = [0., 0., 0.]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)
"""

### RELATIVE MOVEMENTS


### Correct the rotations

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])

vtrans = [0,0,0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### Correct the X-Y translation

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot])

vtrans = [trans[0],trans[1],0]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### Correct the Z translation & residual translations caused by the rotation

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))
printm([trans,rot],6)

vtrans = trans
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# [[-0.  0. -0.]
#  [ 0. -0.  0.]]
printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))
# [-1.74000e-01 -8.20000e-01  5.38527e+02]
#  [ 1.73400e-01 -1.87700e-01 -1.19764e+02]]


### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model, hexhw)
