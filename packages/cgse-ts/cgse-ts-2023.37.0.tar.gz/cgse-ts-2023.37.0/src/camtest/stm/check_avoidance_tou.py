#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 09:30:19 2020

@author: pierre


CSL FPA AVOIDANCE VOLUME TEST  ---  INCL 2 METAL PLATES

bottom plate on the hexapod = "fpasen"   (-> hexobj)
top    plate attached higher = "toul6s2" (-> hexusr)

The two plates are ~ squares of ~ 150mm
They are located ~ 20 mm apart at the hexapod homing position

"""


import os
import numpy as np
import time

from camtest import *

# egse
from egse.coordinates.cslmodel import CSLReferenceFrameModel

#from egse.coordinates.avoidance import is_avoidance_ok

# Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy

# Scripts
from camtest.commanding.csl_gse import hexapod_puna_homing, hexapod_puna_goto_zero_position, hexapod_puna_goto_retracted_position
from camtest.commanding.csl_gse import check_and_move_absolute, check_and_move_relative_user, check_and_move_relative_object

from camtest import execute
from camtest import list_setups, load_setup, submit_setup #building_block

from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict


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

setup = load_setup(9)

print(setup)


#########   CHECK FOR CLEARANCE IN SETUP

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
setup.camera.fpa.avoidance.vertices_radius = 100.
setup.camera.fpa.avoidance.clearance_xy = 2.
setup.camera.fpa.avoidance.clearance_z = 2.


#########   INJECT AVOIDANCE VOLUME - SPECIFIC ReferenceFrameModel in setup

"""
predef_refs={}
predef_refs['gltab']  = 'glfix'
predef_refs['glfix']  = 'glrot'
predef_refs['glrot']  = 'gliso'

predef_refs['gliso']  = 'Master'
predef_refs['Master'] = 'Master'

predef_refs['hexiso'] = 'gliso'
predef_refs['hexmec'] = 'hexiso'
predef_refs['hexplt'] ='hexmec'
predef_refs['hexobj'] = 'hexplt'
predef_refs['hexobusr'] = 'hexusr'
predef_refs['hexusr'] = 'hexmec'
predef_refs['fpaaln'] = 'gliso'
predef_refs['toumec'] = 'gliso'
predef_refs['toul6'] = 'toumec'
predef_refs['toualn'] = 'toumec'
predef_refs['touopt'] = 'toualn'
predef_refs['marialn'] = 'toualn'
predef_refs['cammec'] = 'toualn'
predef_refs['cambor'] = 'toualn'

###  Not Standard !!!
predef_refs['fpamec'] = 'gliso'
predef_refs['toul6s2'] = 'gliso'
predef_refs['fpasen'] = 'gliso'
predef_refs['fpaaln0deg'] = 'gliso'

setup.csl_model = {}
setup.csl_model.default_refs = predef_refs

"""


###############################################################################
#
# LOAD XLS FILE & ASSEMBLE CSLREFERENCEFRAMEMODEL
#
###############################################################################

# Run csl_model up to the definition of HEX_OBUSR, or : simplified version below

###########################
# INITIALIZE MODEL FROM XLS
###########################


filexls = "/Users/pierre/plato/csl_refFrames_avoidance_test_tou.xls"
#filexls = input("Name of the laser tracker xls file ?")


refFrames = laser_tracker_to_dict(filexls,setup)  # -> dict

#for k,v in zip(refFrames.keys(), refFrames.values()):
#    print(f"{k:>10} -- {v.split('|')[-3]}[{v.split('|')[-2]}]")

model = CSLReferenceFrameModel(refFrames)

print(model.summary())


###########################
# COMPLETE THE  MODEL
###########################

# Missing Links so far
model.add_link("Master","gliso")
model.add_link("hexiso","gliso")
model.add_link("toul6s2","gliso")
model.add_link("toumec","gliso")

model.add_link("fpamec","fpaaln0deg")
model.add_link("fpasen","fpaaln0deg")


zeros = [0,0,0]

# HEX_MEC
model.add_frame(name="hexmec", translation=zeros, rotation=zeros, ref="hexiso")
model.add_link("hexmec","hexiso")

# HEX_PLT --> HEX_MEC -- no link
model.add_frame(name="hexplt", translation=zeros, rotation=zeros, ref="hexmec")

# HEX_USR --> HEX_MEC
transformation = model.get_frame("hexmec").getActiveTransformationTo(model.get_frame("toul6s2"))
model.add_frame(name="hexusr", transformation=transformation, ref="hexmec")
model.add_link("hexusr","hexmec")

# HEX_OBJ == FPA_SEN--> HEX_PLT 
transformation = model.get_frame("hexplt").getActiveTransformationTo(model.get_frame("fpasen"))
model.add_frame(name="hexobj", transformation=transformation, ref="hexplt")
model.add_link("hexobj","hexplt",)
model.add_link("hexobj","fpasen")

# HEX_OBUSR
transformation = model.get_frame("hexusr").getActiveTransformationTo(model.get_frame("hexobj"))
model.add_frame(name="hexobusr", transformation=transformation, ref="hexusr")
model.add_link("hexobj","hexobusr")

print(model.summary())

###########################
# SAVE THE  MODEL
###########################

csl_dict =  model.serialize()

setup.csl_model.model =  csl_dict


"""
submit_setup(setup,"Include basic CSLReferenceFrameModel (avoidance check with plate)")
"""

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


execute(hexapod_puna_homing,wait=True)

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

usrtrans = np.round(usrtrans,4)
usrrot = np.round(usrrot,4)
objtrans = np.round(objtrans,4)
objrot = np.round(objrot,4)

hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)



###############################################################################
#
# VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
#
###############################################################################

is_model_sync(model,hexhw)





###############################################################################
#
# TEST 1 : VERTICAL CHECK, NO TILT
#
###############################################################################

### POSITION AT STARTING POSITION (absolute)

# Move up 2 mm below the avoidance volume

verbose = True

vtrans = [1,1,-4]
vrot   = [0,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)


### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep UP --> enter avoidance volume

### Vertical tolerance set to 5mm  => must crash at -5mm 

vtrans = [0,0,0.1]
vrot   = [0,0,0]


for step in range(40):

    print(f"\nStep {step}")

    move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

    is_model_sync(model, hexhw, " "*4)

    time.sleep(time_step)

    if not move_ok: break

### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model, hexhw)

###############################################################################
#
# TEST 2 : HORIZONTAL CHECK
#
###############################################################################

### POSITION AT STARTING POSITION (absolute)

# Move to 2 mm from the avoidance volume

verbose = True

vtrans = [1,1,-7]
vrot   = [0,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep in x or y --> enter avoidance volume

### Horizontal tolerance = 2mm ; starting from [x,y] = [1,1] => must crash on [1, 1.8]
### Horizontal tolerance = 3mm ; starting from [x,y] = [2,2] => must crash on [2, 2.3]
### Horizontal tolerance = 5mm ; starting from [x,y] = [3,3] => must crash on [3, 4.1]

vtrans = [0, 0.1, 0]
vrot   = [0, 0,   0]

for step in range(40):

    print(f"\nStep {step}")    

    move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

    is_model_sync(model, hexhw, " "*4)

    time.sleep(time_step)
    
    if not move_ok: break


### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model, hexhw)


###############################################################################
#
# TEST 3 : VERTICAL CHECK, TILT THE OBJ, THEN APPROACH L6
#
###############################################################################
#
# Largest deviation from the plane given a 
#      radius of 100  mm  --   150 mm 
# 1 degree  --> 1.746 mm  -- 2.691 mm
# 2 degrees --> 3.492 mm  -- 5.238 mm
# 3 degrees --> 5.241 mm  -- 7.8615mm
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

hex_positions(hexhw)

### POSITION AT STARTING POSITION (absolute)

# Move up 2 mm below the avoidance volume

verbose = True

vtrans = [0,0,-14]
vrot   = [1,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep UP --> enter avoidance volume

# OBJ tilted 1 deg wrt USR ==> should crash at -6.8 (--> -6.7 refused)
#  5.00 mm = definition of avoidance volume
#  1.75 mm = vertical displacement of edges wrt center due to the tilt between hexusr and hexobj
#  6.75 mm = vertical distance "between the origins" when a point at the edge enters the avoidance volume


vtrans = [0,0,0.1]
vrot   = [0,0,0]

for step in range(100):

    print(f"\nStep {step}")    

    move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

    is_model_sync(model,hexhw, " "*4)

    time.sleep(time_step)

    if not move_ok: break

is_model_sync(model,hexhw)

### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model,hexhw)



###############################################################################
#
# TEST 4 : VERTICAL CHECK, TILT THE PLATE, THEN APPROACH L6 - MOVE RELATIVE OBJ
#
###############################################################################


### POSITION AT STARTING POSITION (absolute)

# Move up 8 mm below the avoidance volume

verbose = True

vtrans = [0,0,-14]
vrot   = [1,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep UP --> enter avoidance volume

# OBJ tilted wrt USR ==> should crash at -10.3 (--> -10.2 refused)

vtrans = [0,0,0.1]
vrot   = [0,0,0]

for step in range(100):

    print(f"\nStep {step}")    

    move_ok = execute(check_and_move_relative_object, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

    is_model_sync(model,hexhw, " "*4)

    time.sleep(time_step)

    if not move_ok: break



### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### TEST RETRACTED POSITION

model.hexapod_goto_retracted_position()

execute(hexapod_puna_goto_retracted_position,wait=True)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### RESET AT ZERO POSITION

model.hexapod_goto_zero_position()

execute(hexapod_puna_goto_zero_position,wait=True)

is_model_sync(model,hexhw)

hex_positions(hexhw)



