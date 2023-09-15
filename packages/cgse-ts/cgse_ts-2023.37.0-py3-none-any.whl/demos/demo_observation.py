"""

Demo on class Observation

PREREQUISITE :
    . possess a local copy of the data from an observation (image data cubes in fits and HK files in csv format)
    . the data must be in a subdirectory whose full path ends this structure:  /full/.../path/obs/<obsid>_<site>_<setup>
        (_<setup> is optional)

INPUT to constructor of the Observation:
    . obsid = integer
    . data_dir = either None, or /full/.../path from the example above
               if None, it is assumed that the environment variable PLATO_LOCAL_DATA_LOCATION = /full/.../path/

Version 1.0 20211217

P. Royer
"""

import os
import numpy as np
from camtest.analysis.observation import Observation
from camtest import load_setup
import camtest.analysis.convenience as cv

setup = load_setup()

# Optional, but ideal: set this env. variable (and make sure your IDE recognises it, via the preferences)
print(os.getenv("PLATO_LOCAL_DATA_LOCATION"))


##############################################################
###                 OBSERVATION OBECTS
##############################################################

# The Observation class offers a number of functionalities to easily explore and access the content of an obsid
# It requires that the data from the observation pre-exists on your disc (if not: see get_observation below).
# See below to see how to link your local data dir with the Observation class


########################
# DEFINE THE OBSERVATION
########################


obsid = 2442


# IF PLATO_LOCAL_DATA_LOCATION is defined:

obs = Observation(obsid)

# ELSE

data_dir = "/full/.../path/"    # Points to the directory containing 1 directory / obsid ("obs")

obs = Observation(obsid=obsid, data_dir=data_dir)




#########################
# Explore the Observation
#########################

# Where it was found on disk
print("Full obsid", obs.obsid_full)

print("Obsid-specific dir :", obs.obsid_dir)
print("Input data_dir", obs.data_dir)
print("Full path to the obsid: ", obs.path)

print("Setup used for the obsid    ", obs.get_setup_id())
print("Setup loaded in your session", int(setup.get_id()))

# Print the building block that executed to launch this obsid and its parameters
obs.get_execution()


# List of corresponding csv filenames
csvs = obs.get_filenames_csv(full_path=False)

cv.print1(csvs)

# List of filenames for the image data cubes.
# Note we use full_path=True this time
fcubes = obs.get_filenames_cubes(full_path=True)

cv.print1(fcubes)


# Extract one cube [astropy.io.fits entity]
cube_number = 36
hduc = obs.get_cube_hdu(cube_number=cube_number)
print(hduc.info())
cube = hduc[2].data

print(cube.shape)

print(f"CCD coord of LL image corner: [{-hduc[2].header['CRPIX2']}, {-hduc[2].header['CRPIX1']}]")

# Explore the shape of all image data-cubes for a given extension
# By extension number
obs.print_cube_shapes(2)
# By extension name
obs.print_cube_shapes(extension="IMAGE_3_E")

# Extract the times at which each and every frame was acquired
ftimes = obs.get_frame_times()

print(ftimes)



##########################################
# Explore the HK acquired during the obsid
##########################################

# Get the list of devices for which HK exists during this obsid
cv.print1(obs.get_hk_devices())

device = "SYN-HK"

# Get the list of HK entries for the selected device

cv.print1(obs.get_hk_names(device=device))


# Retrieve the HK table for a given device
hk = obs.get_hk(device=device)


# Retrieve the HK table for a given device, interpolated at the frame-acquisition times
keys = ["GSYN_TRP1", "GSYN_TRP8"]

hk_frame = obs.get_hk_per_frame(device=device, keys=keys, outputfile=None, decimals=6)

print(hk_frame.colnames)

# Retrieve the HK table for a given device, averaged over the duration of every cube
hk_cube = obs.get_hk_per_cube(device=device, keys=keys, outputfile=None, decimals=6, func=np.nanmean)

print(hk_cube.colnames)




##############################################################
###                 DOWNLOAD OBSERVATION
##############################################################

# This is a helper function, allowing to easily download an obsid from the data-repository @ KUL
# It implicitly demands to have a rsync access to that data-repository

obsid = 2164
setup = 43      # The necessity for this parameter will be removed in the future

# Download obsid : cubes and HK -- highly recommended (wrt the subsequent use of Observation)
# ASSUMING env. variable PLATO_LOCAL_DATA_LOCATION is defined:
download_observation(obsid, setup)

# Download obsid : HK only
download_observation(obsid, setup, selection="csv")

# Download obsid : cubes only
download_observation(obsid, setup, selection="cubes")


# IF PLATO_LOCAL_DATA_LOCATION is not defined, add "data_dir" to every call. For instance:
data_dir = "/full/.../path/"        # points to the directory with one directory / obsid ("obs")
download_observation(obsid, setup, data_dir=data_dir)











