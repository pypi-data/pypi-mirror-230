#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 09:30:19 2020

@author: pierre


CSL FPA AVOIDANCE VOLUME TEST  ---  PURE SOFTWARE


"""


import os
import numpy as np
import time

from camtest import *

# egse
from egse.coordinates.cslmodel import CSLReferenceFrameModel
#from egse.coordinates.avoidance import is_avoidance_ok

# Hexapod
#from egse.hexapod.symetrie.puna import PunaController
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy

# Scripts
from camtest.commanding.csl_gse import hexapod_puna_homing, hexapod_puna_goto_zero_position, hexapod_puna_goto_retracted_position
from camtest.commanding.csl_gse import check_and_move_absolute, check_and_move_relative_user#, check_and_move_relative_object


from camtest import execute
from camtest import list_setups, load_setup, submit_setup #building_block


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

###############################################################################
#
# CONFIGURE LARGER AVOIDANCE VOLUME
#
###############################################################################

list_setups()

setup = load_setup(9)

print(setup)

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
setup.camera.fpa.avoidance.clearance_z = 5.




###############################################################################
#
# CONNECT TO HEXAPOD
#
###############################################################################

time_step        = 1.

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
        

###############################################################################
#
# CONFIGURE HEXAPOD REFERENCE FRAMES MODEL
#
###############################################################################

# Run csl_model up to the definition of HEX_OBUSR, or : simplified version below

zeros = [0,0,0]

# CSL REFERENCE FRAME MODEL

#model = ReferenceFrameModel()
model = CSLReferenceFrameModel()


# Master
model.add_master_frame()

# HEX_MEC
model.add_frame(name="hexmec", translation=zeros, rotation=zeros, ref="Master")

# HEX_PLT --> HEX_MEC -- no link
model.add_frame(name="hexplt", translation=zeros, rotation=zeros, ref="hexmec")

# HEX_OBJ --> HEX_PLT
model.add_frame(name="hexobj", translation=zeros, rotation=zeros, ref="hexplt")
model.add_link("hexplt","hexobj")

# HEX_USR --> HEX_MEC
model.add_frame(name="hexusr", translation=zeros, rotation=zeros, ref="hexmec")
model.add_link("hexmec","hexusr")

# HEX_OBUSR
transformation = model.get_frame("hexusr").getActiveTransformationTo(model.get_frame("hexobj"))
model.add_frame(name="hexobusr", transformation=transformation, ref="hexusr")
model.add_link("hexobj","hexobusr")


csl_dict =  model.serialize()

setup.csl_model =  csl_dict

"""
submit_setup(setup,"Include basic CSLReferenceFrameModel (hexapod only)")
"""

###############################################################################
#
# VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
#
###############################################################################

is_model_sync(model,hexhw)


###############################################################################
#
# CONFIGURE HEX_USR
#
###############################################################################

# Abs position of L6S2, in mm above the hexmec (== zero position)
L6S2 = 10

usrtrans = [0,0,L6S2]
usrrot   = [0,0,0]
objtrans = [0,0,0]
objrot   = [0,0,0]

model.hexapod_configure_coordinates(usrtrans, usrrot, objtrans, objrot)
hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

is_model_sync(model,hexhw)


###############################################################################
#
# TEST 1 : VERTICAL CHECK, NO TILT
#
###############################################################################

### POSITION AT STARTING POSITION (absolute)

# Move up 2 mm below the avoidance volume

verbose = True

vtrans = [2,2,-7]
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

hex_positions(hexhw)

###############################################################################
#
# TEST 2 : HORIZONTAL CHECK
#
###############################################################################

### POSITION AT STARTING POSITION (absolute)

# Move to 2 mm from the avoidance volume

verbose = True

vtrans = [2,2,-7]
vrot   = [0,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep in x or y --> enter avoidance volume

### Horizontal tolerance = 3mm  => must crash on [2, 2.3]

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
# TEST 3 : VERTICAL CHECK, TILT
#
###############################################################################
#
# CONFIGURE HEX_OBJ WITH TILT IN X
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

usrtrans = [0, 0,L6S2]
usrrot   = [0, 0, 0]
objtrans = [0, 0, 0]
objrot   = [3, 0, 0]

model.hexapod_configure_coordinates(usrtrans, usrrot, objtrans, objrot)
hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### POSITION AT STARTING POSITION (absolute)

# Move up 2 mm below the avoidance volume

verbose = True

vtrans = [2,2,-7]
vrot   = [0,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep UP --> enter avoidance volume

# OBJ SET // to USR ==> should still crash at -5

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
# TEST 4 : VERTICAL CHECK, MOVE UP WHILE TILTED
#
###############################################################################
#
# CONFIGURE HEX_USR WITH TILT IN X
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Largest deviation from the plane given a radius of 100 mm 
# 1 degree  --> 1.746 mm
# 2 degrees --> 3.492 mm
# 3 degrees --> 5.241 mm

usrtrans = [0, 0,L6S2]
usrrot   = [3, 0, 0]
objtrans = [0, 0, 0]
objrot   = [0, 0, 0]

model.hexapod_configure_coordinates(usrtrans, usrrot, objtrans, objrot)
hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### POSITION AT STARTING POSITION (absolute)

# Move to 7 mm below the avoidance volume, keeping hexobj "horizontal" (anti-hexusr tilt)

verbose = True

vtrans = [0,0,-12]
vrot   = [-3,0,0]

execute(check_and_move_absolute, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model,hexhw)

hex_positions(hexhw)

### PROGRESS TOWARDS AVOIDANCE VOLUME (relative)

# Sweep UP --> enter avoidance volume

# OBJ tilted wrt USR ==> should crash at -10.3 (--> -10.2 refused)
#  5.000 mm = definition of avoidance volum2
#  5.241 mm = vertical displacement of edges wrt center due to the tilt between hexusr and hexobj
# 10.2   mm = vertical distance "between the origins" when a point at the edge enters the avoidance volume

vtrans = [0,0,0.1]
vrot   = [0,0,0]

for step in range(100):

    print(f"\nStep {step}")    

    move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

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

## RESET HEXAPOD CONFIG

usrtrans = [0,0,0]
usrrot   = [0,0,0]
objtrans = [0,0,0]
objrot   = [0,0,0]

model.hexapod_configure_coordinates(usrtrans, usrrot, objtrans, objrot)
hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

is_model_sync(model,hexhw)


