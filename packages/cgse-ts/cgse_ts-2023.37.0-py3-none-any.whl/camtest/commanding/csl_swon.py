"""
CSL SWITCH ON PROCEDURE

SWON AEU, DPU, OGSE, LOAD THE SETUP, START TM ACQUISITION, FITS GENERATION & VARIOUS GUIs


Throughout the procedure:
. a line starting with $ indicates a command to be passed on a terminal (client or server)
. python commands (= uncommented statements) are directly executable from this script
"""



###########################
# HARWARE POWER ON
###########################

# Physical power on of the various hardware components
# All or part of this can be skipped wrt the components already ON

# Power on the EGSE Server  (in the rack)
# Power on the EGSE Desktop (computer)
# Power on the AEU Camera Test EGSE (in the rack)
# Power on the DAQ (Test house Temeperature Data Acquisition System, in the rack)
# Power on the mechanism controllers (in the rack):
#     Huber stages
#     Hexapod
# Power on the OGSE controller (in the rack)
# Power on the Spacewire interface (in the rack)


###########################
# LOGIN on the EGSE Desktop
###########################

# Login to the "client":
#   usr : plato-data
#   pwd : stm-data

# Login to the "server" (open a terminal and connect to it)
# $ ssh plato-data@egseserver (pwd: stm-data)

# NB: the background color differs between terminals open on the client and on the server



###########################
# Process Manager
###########################

# Launch the Process Manager
# Either via the DEDICATED ICON on the left of the screen (send the mouse to the top left corner to see it)
# OR, on the client:
# $pm_ui

# CHECK: You must now see three green buttons
# Storage
# Configuration Manager
# Process Manager


##############################
# LOAD THE SETUP ON THE CLIENT
##############################

# In the ProcessManager GUI
# Launch the Configuration Manager GUI : clic on GUI next to the Configuration manager
# In the Configuration Manager GUI : clic on the magnifier on top to display the list of available setup
# In the list, clic on a setup
# Clic on the truck-loading icon, top left of the GUI

# CHECK : in the Configuration Manager GUI, check that the Setup ID corresponds to the setup just loaded


###############################
# SWITCH ON THE CONTROL SERVERS
###############################
# In the Process Manager GUI :
# clic on all "START" icons:

# Symetrie Puna
# Huber SMC9300
# AEU cRIO
# OGSE
# DAQ

# NB:the DPU does not have the corresponding icon

# CHECK : all buttons should progressively turn green (except the DPU)



###############################
# PYTHON IMPORTS
###############################

from camtest import load_setup, start_observation, end_observation, execute
from camtest.commanding import aeu, dpu, ogse


#######################################
# LOAD THE SETUP IN THIS PYTHON SESSION
#######################################

setup = load_setup()
print(setup)

# CHECK : the setup ID at the bottom should correspond to the setup ID loaded from the Configuration Manager GU (see above)


#######################################
# SWITCH ON THE AEU
#######################################

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_000_

aeu.n_cam_swon()

aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()


#######################################
# DPU CONTROL SERVER AND GUIs
#######################################

# DPU CONTROL SERVER: on the server
# $dpu_cs start

# DPU GUI: on the client
# $dpu_ui


###############################
# FITS FILE GENERATION
###############################

# On the server
# $fitsgen start


###############################
# TELEMETRY ACQUISITION
###############################

# On the server
# $python -m egse.fee.n_fee_hk -platform offscreen

###############################
# FOV GUI (GSE mechanisms)
###############################
# $fov_gui


###############################
# FEE TO AMBIENT - DUMP
###############################


# STANDBY mode external sync
execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode (up to 30 seconds)

print(dpu.n_cam_is_standby_mode())


# DUMP mode internal sync
execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())



###############################
# OGSE
###############################


start_observation("Switch on procedure: OGSE")  # obsid =

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

print(ogse.attenuator_is_moving())
print(ogse.attenuator_is_ready())

end_observation()



