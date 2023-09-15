"""
Created on Sep 01 2021

@author: Pierre Royer

GOAL

Create a new CSLReferenceFrameModel from an excel file delivered by CSL
Load it in the Setup
Configure the Hexapod to be in synch with the new model


PRECONDITION

Make sure the hexapod controller is powered on and the control server was switched on.
The SWON script camtest.commanding.csl_swon takes care to switch on all essential services



CHECKPOINTS

The operator of this script is supposed to intervene at a few key points.
These are marked with the word "CHANGE" in capital


"""


###############################
# IMPORT
###############################

import os

import numpy as np

# Scripts
from camtest import load_setup, execute  # building_block
from camtest.analysis.convenience import printm
from camtest.commanding.csl_gse import is_model_sync
from camtest.commanding.csl_gse import check_and_move_relative_user

# egse
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.coordinates.refmodel import get_vectors, print_vectors
from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy
# Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator

rot_config = "sxyz"

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")

time_step = 1.

verbose = True


#################################
# LOAD THE SETUP IN THIS SESSION
#################################
# Optional if done already, e.g. in csl_swon

#setup = load_setup(site_id="CSL", from_disk=True)
setup = load_setup()
print(setup)


###############################
# PREDEFINED REFERENCES
###############################

# Every ref. frame is attached to a "reference" reference frame
# Those references are not mentioned in the excel sheet, they must be pre-existing in the setup
# This section sets it for all reference frames present in the



# All ReferenceFrames measured or defined in CSL, i.e. all in the excelll sheet are expressed wrt gliso
predef_refs = {}
predef_refs['Master'] = 'Master'

# CSL GSE
predef_refs['gliso'] = 'Master'  # csl
predef_refs['glfix'] = 'glrot'  # csl
predef_refs['glrot'] = 'gliso'  # csl

# HEXAPOD
predef_refs['hexiso'] = 'gliso'  # csl (originally hex_mec)
predef_refs['hexplt'] = 'gliso'  # csl
predef_refs['hexobj'] = 'gliso'  # csl
predef_refs['hexusr'] = 'gliso'  # csl
# predef_refs['hexmec'] = 'hexiso'
# predef_refs['hexobusr'] = 'hexusr'

# FPA
predef_refs['fpaaln'] = 'gliso'  # csl
predef_refs['fpamec'] = 'gliso'  # csl
predef_refs['fpasen'] = 'gliso'  # csl

# TOU
predef_refs['toumec'] = 'gliso'  # csl
predef_refs['toualn'] = 'gliso'  # csl
predef_refs['toulos'] = 'gliso'  # csl
predef_refs['toul6'] = 'gliso'  # csl

predef_refs['toubipcoords'] = 'gliso'  # csl
predef_refs['toubip'] = 'gliso'  # csl
predef_refs['bolt'] = 'gliso'  # csl

# HARTMANN PLANE
predef_refs['hartmann'] = 'gliso'  # csl

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

# CHANGE : name of the excel file to be loaded
#filexls = "/Users/pierre/plato/006_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"
filexls = "/data/CSL/conf/006_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"


# Read the excel file
refFrames = laser_tracker_to_dict(filexls, setup)  # -> dict

# for k,v in zip(refFrames.keys(), refFrames.values()):
#    print(f"{k:>10} -- {v.split('|')[-3]}[{v.split('|')[-2]}]")

# Assemble the model
model = CSLReferenceFrameModel(refFrames)

# CHECK. At this stage, the ref. frames from the excel sheet are in the model, but only those.
# The frames have the proper reference, but not links
print(model.summary())

###########################
# COMPLETE THE  MODEL
###########################

"""
The hexapod frames hex_plt, hex_obj, hex_usr must be explicitly defined wrt hex_mec
So they are deleted from the excel sheet and set to I (hex_plt) or derived from fpasen (hexobj) and toul6 (hexusr)

For the hexapod simulator to work, HEX_MEC must be defined as the identity matrix, so in the excel sheet, the name
hex_mec is replace with hex_iso, an additional frame encapsulating the transformation between the rest 


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

# FLAT @ level of Hartmann plane
# translation = [0., 0., -6.8062e+01]
# rotation = [-5.5000e-02, -9.0000e-03, 1.2200e-02]
# model.add_frame(name="hartflat", translation=translation, rotation=rotation, ref="toumec")

# CHECK. At this stage, all ref. frames are in the model, but not links they have no links
# The links specify which frames are tied together, and for a solid body,
# i.e. essentially the TOU on one side, the FPA+hexapod on the other
print(model.summary())



###########################
# INCLUDE THE LINKS
###########################

model.add_link("Master", "gliso")
model.add_link("glrot", "gliso")

# # HEXAPOD
model.add_link("hexiso", "gliso")
model.add_link("hexmec", "hexiso")
model.add_link("hexobj", "hexplt", )
model.add_link("hexobj", "hexobusr")
model.add_link("hexusr", "hexmec")

model.add_link("fpasen", "hexobj", )
model.add_link("fpasen", "fpamec")
model.add_link("fpamec", "fpaaln")

model.add_link("toul6", "hexusr")
model.add_link("toul6", "toumec")
model.add_link("toumec", "gliso")
model.add_link("toumec", "toualn")
model.add_link("toulos", "toualn")
model.add_link("toubipcoords", "toumec")
model.add_link("toubip", "toumec")
model.add_link("bolt", "toumec")

model.add_link("hartmann", "toumec")

# WE MUST STILL DEFINE MARI_ALN & CAM_BOR

print(model.summary())



#############################
# SAVE THE  MODEL - OPTIONAL
#############################

csl_dict = model.serialize()

setup.csl_model.model = csl_dict

"""
setup = submit_setup(setup,"CSLReferenceFrameModel EM 003")

setup = load_setup()
"""

########################################################
# SANITY CHECK & CROSS CHECK WITH LASER TRACKER SOFTWARE
########################################################

# printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))

printm(model.get_frame("hexobusr").getTranslationRotationVectors())
printm(model.get_frame("fpasen").getTranslationRotationVectors())
printm(model.get_frame("toubip").getTranslationRotationVectors())

rounding = 4
print_vectors('gliso', 'fpasen', model=model)
print_vectors('gliso', 'hexobj', model=model)

print_vectors('fpasen', 'hexobj', model=model)
print_vectors('fpasen', 'hexobj', model=model)

print_vectors('fpasen', 'toumec', model=model)
print_vectors('fpasen', 'toul6', model=model)
print_vectors('fpasen', 'toulos', model=model)
print_vectors('fpasen', 'toubip', model=model)

print_vectors('toubip', 'fpasen', model=model)
print_vectors("toubip", "toumec", model=model)
print_vectors("toumec", "toubip", model=model)
print_vectors("toumec", "toulos", model=model)
print_vectors("toumec", "toualn", model=model)
print_vectors("toualn", "toulos", model=model)

print_vectors("toumec", "toubip", model=model)
print_vectors("toumec", "hartmann", model=model)
print_vectors("hartmann", "toumec", model=model)
print_vectors("hartmann", "toubip", model=model)

print_vectors('hexobusr', 'toul6', model=model)
print_vectors('hexobj', 'toul6', model=model)
print_vectors("toubip", "bolt", model=model)
print_vectors("bolt", "toumec", model=model)

# PRINT COMPLETE MODEL WRT GLISO
# HEXAPOD
# print_vectors('gliso', 'hexiso', model=model)
print_vectors('gliso', 'hexmec', model=model)
print_vectors('gliso', 'hexusr', model=model)
print_vectors('gliso', 'hexplt', model=model)
print_vectors('gliso', 'hexobj', model=model)
print_vectors('gliso', 'hexobusr', model=model)

# FPA
print_vectors('gliso', 'fpasen', model=model)
print_vectors('gliso', 'fpamec', model=model)
print_vectors('gliso', 'fpaaln', model=model)

# TOU
print_vectors('gliso', 'toumec', model=model)
print_vectors('gliso', 'toualn', model=model)
print_vectors('gliso', 'toulos', model=model)
print_vectors('gliso', 'toubip', model=model)
print_vectors('gliso', 'bolt', model=model)
print_vectors('gliso', 'hartmann', model=model)

# EM 006
# gliso    -> fpasen   : Trans [ 1.5400e-01,  1.0610e+00,  5.2039e+02]    Rot [-8.5700e-02, -4.5700e-02, -1.2017e+02]
# gliso    -> hexobj   : Trans [ 1.5400e-01,  1.0610e+00,  5.2039e+02]    Rot [-8.5700e-02, -4.5700e-02, -1.2017e+02]
# fpasen   -> hexobj   : Trans [ 0.0000e+00, -0.0000e+00,  0.0000e+00]    Rot [ 0.0000e+00, -0.0000e+00,  0.0000e+00]
# fpasen   -> hexobj   : Trans [ 0.0000e+00, -0.0000e+00,  0.0000e+00]    Rot [ 0.0000e+00, -0.0000e+00,  0.0000e+00]
# fpasen   -> toumec   : Trans [ 1.0801e+00,  2.5250e-01,  8.5983e+01]    Rot [ 5.9800e-02,  4.7300e-02,  1.3700e-02]
# fpasen   -> toul6    : Trans [ 1.2498e+00,  3.2270e-01,  2.1369e+01]    Rot [ 5.9800e-02,  4.7300e-02,  1.3700e-02]
# fpasen   -> toulos   : Trans [ 1.0801e+00,  2.5250e-01,  8.5983e+01]    Rot [ 4.2300e-02,  2.4500e-02,  2.6470e-01]
# fpasen   -> toubip   : Trans [ 1.0235e+00,  3.2440e-01,  1.7691e+01]    Rot [ 2.4900e-02,  4.0200e-02,  2.5900e-02]
# toubip   -> fpasen   : Trans [-1.0112e+00, -3.3170e-01, -1.7691e+01]    Rot [-2.4900e-02, -4.0200e-02, -2.5900e-02]
# toubip   -> toumec   : Trans [ 8.7000e-03, -4.2300e-02,  6.8292e+01]    Rot [ 3.4900e-02,  7.2000e-03, -1.2200e-02]
# toumec   -> toubip   : Trans [-1.0000e-04,  7.0000e-04, -6.8292e+01]    Rot [-3.4900e-02, -7.2000e-03,  1.2200e-02]
# toumec   -> toulos   : Trans [ 0.0000e+00,  0.0000e+00,  0.0000e+00]    Rot [-1.7700e-02, -2.2500e-02,  2.5100e-01]
# toumec   -> toualn   : Trans [-8.3149e+01, -8.3335e+01,  1.3022e+02]    Rot [-9.7000e-03, -8.6500e-02,  2.5100e-01]
# toualn   -> toulos   : Trans [ 8.3316e+01,  8.2992e+01, -1.3033e+02]    Rot [-8.0000e-03,  6.4000e-02,  0.0000e+00]
# toumec   -> toubip   : Trans [-1.0000e-04,  7.0000e-04, -6.8292e+01]    Rot [-3.4900e-02, -7.2000e-03,  1.2200e-02]
# toumec   -> hartmann : Trans [-1.0000e-04,  6.0000e-04, -6.8062e+01]    Rot [-8.7400e-02,  1.8700e-02,  1.2200e-02]
# hartmann -> toumec   : Trans [-2.2100e-02, -1.0440e-01,  6.8062e+01]    Rot [ 8.7400e-02, -1.8700e-02, -1.2200e-02]
# hartmann -> toubip   : Trans [ 1.0000e-04,  5.0000e-04, -2.3000e-01]    Rot [ 5.2500e-02, -2.5900e-02, -0.0000e+00]
# hexobusr -> toul6    : Trans [ 1.2498e+00,  3.2270e-01,  2.1369e+01]    Rot [ 5.9800e-02,  4.7300e-02,  1.3700e-02]
# hexobj   -> toul6    : Trans [ 1.2498e+00,  3.2270e-01,  2.1369e+01]    Rot [ 5.9800e-02,  4.7300e-02,  1.3700e-02]
# toubip   -> bolt     : Trans [ 5.0000e-04, -8.0000e-04, -7.5000e-02]    Rot [-0.0000e+00, -0.0000e+00, -0.0000e+00]
# bolt     -> toumec   : Trans [ 8.2000e-03, -4.1500e-02,  6.8367e+01]    Rot [ 3.4900e-02,  7.2000e-03, -1.2200e-02]
# toumec   -> hartflat : Trans [ 0.0000e+00,  0.0000e+00, -6.8062e+01]    Rot [-5.5000e-02, -9.0000e-03,  1.2200e-02]
# toumec   -> hartmann : Trans [-1.0000e-04,  6.0000e-04, -6.8062e+01]    Rot [-8.7400e-02,  1.8700e-02,  1.2200e-02]
# gliso    -> hexmec   : Trans [ 2.3000e-01,  1.3600e-01,  2.3019e+02]    Rot [-7.3000e-03, -1.5200e-02,  3.3900e-02]
# gliso    -> hexusr   : Trans [-1.5900e-01, -1.8300e-01,  5.4176e+02]    Rot [-2.5900e-02,  1.7000e-03, -1.2016e+02]
# gliso    -> hexplt   : Trans [ 2.3000e-01,  1.3600e-01,  2.3019e+02]    Rot [-7.3000e-03, -1.5200e-02,  3.3900e-02]
# gliso    -> hexobj   : Trans [ 1.5400e-01,  1.0610e+00,  5.2039e+02]    Rot [-8.5700e-02, -4.5700e-02, -1.2017e+02]
# gliso    -> hexobusr : Trans [ 1.5400e-01,  1.0610e+00,  5.2039e+02]    Rot [-8.5700e-02, -4.5700e-02, -1.2017e+02]
# gliso    -> fpasen   : Trans [ 1.5400e-01,  1.0610e+00,  5.2039e+02]    Rot [-8.5700e-02, -4.5700e-02, -1.2017e+02]
# gliso    -> fpamec   : Trans [ 3.3000e-01,  1.0760e+00,  5.8163e+02]    Rot [-7.6800e-02, -3.3900e-02, -1.1972e+02]
# gliso    -> fpaaln   : Trans [-1.0567e+02,  9.0368e+01,  5.2380e+02]    Rot [-8.6400e-02, -4.6600e-02, -1.2018e+02]
# gliso    -> toumec   : Trans [-2.5000e-02, -5.0000e-03,  6.0637e+02]    Rot [-2.5900e-02,  1.7000e-03, -1.2016e+02]
# gliso    -> toualn   : Trans [-3.0253e+01,  1.1372e+02,  7.3663e+02]    Rot [-3.5600e-02, -8.4700e-02, -1.1991e+02]
# gliso    -> toulos   : Trans [-2.5000e-02, -5.0000e-03,  6.0637e+02]    Rot [-4.3600e-02, -2.0700e-02, -1.1991e+02]
# gliso    -> toubip   : Trans [-5.0000e-02,  1.2000e-02,  5.3808e+02]    Rot [-6.0800e-02, -5.5000e-03, -1.2015e+02]
# gliso    -> bolt     : Trans [-5.1000e-02,  1.2000e-02,  5.3800e+02]    Rot [-6.0800e-02, -5.5000e-03, -1.2015e+02]
# gliso    -> hartmann : Trans [-5.0000e-02,  1.2000e-02,  5.3831e+02]    Rot [-1.1330e-01,  2.0400e-02, -1.2015e+02]




###############################################################################
#
# CONNECT TO HEXAPOD
#
###############################################################################



try:
    # hexhw = PunaController()
    # hexhw.connect()
    hexhw = PunaProxy()
    hexhw.info()
except HexapodError:
    hexhw = PunaSimulator()
except NotImplementedError:
    hexhw = PunaSimulator()

print(f"Hexapod HW is simulator: {hexhw.is_simulator()}")

# execute(hexapod_puna_homing,wait=True)

# execute(hexapod_puna_goto_zero_position,wait=True)




###############################################################################
#
# CONFIGURE HEX_USR WRT THE MEASURED POSITION OF TOU L6S2 (Laser Tracker)
#
###############################################################################


usrtrans, usrrot = model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
objtrans, objrot = model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

rounding = 6
usrtrans = np.round(usrtrans, rounding)
usrrot = np.round(usrrot, rounding)
objtrans = np.round(objtrans, rounding)
objrot = np.round(objrot, rounding)

hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)



###############################################################################
#
# VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
#
###############################################################################

is_model_sync(model, hexhw)


###############################################################################
#
# READY TO EXECUTE HEXAPOD MOVEVEMENTS
#
###############################################################################






#########################################################
# EXAMPLE MOVEMENT
#########################################################

is_model_sync(model, hexhw)

# trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip"))

trans, rot = get_vectors('fpasen', 'toubip', model)
printm([trans,rot])

# The following lines correct the x-y translations and the rotation  between fpasen onto toubip in a single movement
vtrans = [trans[0], trans[1], 0.]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = get_vectors('fpasen', 'toubip', model)
printm([trans,rot])




