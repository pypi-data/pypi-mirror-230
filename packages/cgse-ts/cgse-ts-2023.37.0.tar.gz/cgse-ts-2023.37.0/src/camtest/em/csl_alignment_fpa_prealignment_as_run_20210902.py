#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 01 2021

@author: pierre

"""


import os

import numpy as np

from camtest import execute
from camtest import list_setups, load_setup  # building_block
from camtest.commanding.csl_gse import check_and_move_relative_user
# Scripts
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position
# egse
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy
# Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator


# from camtest import *
# from egse.coordinates.avoidance import is_avoidance_ok


# Convenience functions
def printm(matrix,rounding=4):
    print(np.round(matrix,rounding))
    
def positions_match(hexapod,hexsim,atol=0.0001,rtol=0.0001):
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)

def is_model_sync(model,hexhw,verbose=None,rounding=4,atol=0.0001,rtol=0.0001):
    
    if verbose is None: verbose=""
    
    coohex = hexhw.get_user_positions()
    coomodtr,coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(model.get_frame('hexobj'))
    coomod = np.concatenate([coomodtr,coomodrot])
    
    print(f"{verbose}Hexapod   : {np.round(coohex,rounding)}")
    print(f"{verbose}Model     : {np.round(coomod,rounding)}")
    print(f"{verbose}Diff      : {np.round(coohex-coomod,rounding)}")

    print(f"{verbose}In synch  : {np.allclose(coohex,coomod,atol=atol,rtol=rtol)}")

    return


def hex_positions(hexapod,rounding=3):
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

time_step        = 1.

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


# All ReferenceFrames measured or defined in CSL, i.e. all in the excelll sheet are expressed wrt gliso
predef_refs={}
predef_refs['Master'] = 'Master'

# CSL GSE
predef_refs['gliso']  = 'Master'     # csl
predef_refs['glfix']  = 'glrot'      # csl
predef_refs['glrot']  = 'gliso'      # csl

# HEXAPOD
predef_refs['hexiso'] = 'gliso'      # csl (originally hex_mec)
predef_refs['hexplt'] ='gliso'       # csl
predef_refs['hexobj'] = 'gliso'     # csl
predef_refs['hexusr'] = 'gliso'      # csl
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
predef_refs['toubip'] = 'gliso'      # csl
#predef_refs['touopt'] = 'toualn'

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
filexls = "/data/CSL/conf/003_csl_refFrames_TOU_alignment_EM_HartmannPlane.xls"

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
setup = submit_setup(setup,"CSLReferenceFrameModel EM 003")

setup = load_setup()
print(setup.get_id())
"""

print(setup.csl_model)

###########################
# CROSS CHECK WITH LASER TRACKER SOFTWARE
###########################

printm(model.get_frame("hexobusr").getTranslationRotationVectors())
printm(model.get_frame("fpasen").getTranslationRotationVectors())
printm(model.get_frame("toubip").getTranslationRotationVectors())

printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")))
printm(model.get_frame("gliso").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))


printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj")))
#[0,0,0][0,0,0]

printm(model.get_frame("hexobusr").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
printm(model.get_frame("hexobj").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
# [[ 1.3971  0.5508 21.3297]
#  [ 0.2717 -0.1728  0.2595]]
printm(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))
# [[ 1.8054  0.6348 18.1375]
#  [ 0.2594 -0.1427  0.4101]]
printm(model.get_frame("toubip").getActiveTranslationRotationVectorsTo(model.get_frame("fpasen")), 6)
# [[ -1.8551  -0.7039 -18.13  ]
#  [ -0.2604   0.1408  -0.4108]]
printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")), 6)
# [[-3.0300e-01 -3.3000e-02 -6.8062e+01]
#  [-8.7400e-02  1.8700e-02 -1.2400e-02]]

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

hex_positions(hexhw, 4)

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

print(usrtrans, usrrot)
print(objtrans, objrot)

# Values provided by Ann

hexhw.get_coordinates_systems()
# Out[28]:
# [-3.373,
#  -1.207,
#  311.971,
#  0.172763,
#  -0.22314,
#  -119.972658,
#  0.002,
#  0.887,
#  290.201,
#  -0.102532,
#  -0.047013,
#  -120.208281]

# Values extracted from the model

print(usrtrans, usrrot)
#  [-1.83545000e-01 -6.00556000e-01  3.11530986e+02] [   0.168934   -0.219299 -119.948512]

print(objtrans, objrot)
# [1.66700000e-03 8.88050000e-01 2.90201125e+02] [-1.02532000e-01 -4.70130000e-02 -1.20208281e+02]


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

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [0,0,0]
vrot   = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### Correct the X-Y translation

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot])

vtrans = [trans[0],trans[1],0]
vrot   = [0,0,0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### Correct the Z translation & residual translations caused by the rotation


### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model, hexhw)

