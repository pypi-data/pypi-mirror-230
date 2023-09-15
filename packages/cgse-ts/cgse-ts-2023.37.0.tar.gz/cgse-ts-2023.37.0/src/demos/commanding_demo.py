#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 15:48:14 2020

@author: pierre
"""

###############################################################################
#     COMMANDING  DEMO  TEST-PREPARATION WORKSHOP   2020 07 06
###############################################################################

"""
# Prerequisites

Mandatory:
    
    Set the environment variable PLATO_DATA_STORAGE_LOCATION 
    to a write-able directory on your computer. 
    Go there and create 2 subdirectories "obs" & "daily"

    Start StorageManager:
    <common-egse_env> $ python -m egse.storage.storage_cs

    Start the ConfigurationManager
    <common-egse_env> $  python -m egse.confman.confman_cs

Optional: 
    
    launch hexapod Control Server (simulator)
    <common-egse_env> $ python -m egse.hexapod.symetrie.puna_cs --sim

"""

from camtest import *
from camtest.commanding import *

######################## CALLING A COMMANDING SCRIPT ##########################

print ('generate_command_sequence' in dir())
print ('cam_tvlpt_030' in dir())


list_setups()

list_setups(site_id="CSL")

list_setups(site_id="CSL", position=4)

load_setup(8)

print(GlobalState.setup.pretty_str())


GlobalState.setup.camera.dpu.device.get_n_fee_mode()


# Dry run & visualisation of the sequence of events
generate_command_sequence(cam_tvlpt_030, num_bias=10, num_dark=100)

# Also allowed:
parameter_dict = {'num_bias':10, 'num_dark':100}
generate_command_sequence(cam_tvlpt_030, **parameter_dict)


# NOT:
# generate_command_sequence(cam_tvlpt_030(num_bias=10, num_dark=100))


# Creation of an obsid and actual execution
execute(cam_tvlpt_030, num_bias=10, num_dark=100)


"""
Check the data in $PLATO_DATA_STORAGE_LOCATION
"""






######################## MANUAL COMMANDING ####################################

################# TEST HOUSES : THIS IS FOR YOU ###############################

####### REGULAR PCOT MEMBER : THIS IS (FORBIDDEN). FORGET IT. NICHT GUT #######


# Simulator
hexapod = GlobalState.setup.gse.hexapod.device 

print(hexapod)


# Proxy
from egse.hexapod.symetrie.puna import PunaProxy

hexapod = PunaProxy()

print(hexapod)


####  launch the hexapod Controller GUI -- After you have instanciated the hexapod proxy!
# <common-egse_env> $ python -m egse.hexapod.symetrie.puna_ui --type proxy


hexapod.homing()

translation = [2,4,6]
rotation    = [-1,1,2]
hexapod.move_absolute(*translation, *rotation)




















