#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 16:24:50 2020

@author: pierre
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 15:40:20 2020

@author: pierre
"""

import datetime

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import numpy as np

import camtest.analysis.convenience as cv
from camtest.analysis import simfits

##################### DATA DIRECTORY ##########################################

simname = stem = 'tn016'

fitsdir   = "/Volumes/MAGNET/plato/simout/"+simname+"/fits/" 



###############################################################################
#############                      DATA ACCESS 
###############################################################################


ccd_side = 'E'
simfile = fitsdir + stem + '_' + ccd_side + ".fits"

hdul = pyfits.open(simfile)


# Under development:
# observation = get_observation(obsid, location=os.getenv("PLATO_DATA_STORAGE_LOCATION"))
# hdul        = observation["SCIENCE"]
# hexapod_hk  = observation["HEX"]



###############################################################################
#############              BASIC INSPECTION 
###############################################################################


# PRIMARY HEADER = META DATA

header = hdul[0].header
print(header)
print()


# headert0 is the creation time of the fits file 
# frame time in further extensions are relative to it ==> !! when dealing with acquisition times

headert0 = hdul[0].header["DATE-OBS"]

t0 = datetime.datetime.strptime(headert0, "%Y-%m-%d %H:%M:%S").timestamp()

print(f"Header time : {headert0}")
print(f"Converted   : {t0}")


###############################################################################
############            FITS - TABLE OF CONTENT 
###############################################################################

# EXTENSIONS = SIMULATIONS

# A. TABLE OF CONTENT

# Every Image comes with 4 extensions
# WINDOW1   SPRESCANE1   SPRESCANF1   POVERSCAN1

hdul.info()

# Identify the extensions by type
list_image,list_prescane,list_prescanf,list_overscan = simfits.info(hdul)

print(list_image)

# Assemble relative timing between the frames.
reltime = simfits.reltime(hdul, t0=None)

print(f"Relative timing of the subsequent images: \n{reltime}")



###############################################################################
#############           BASIC VISUALISATION 
###############################################################################


n = 73

simfits.show(hdul,field_type='image',n=n,clim=(998,1002))

simfits.show(hdul,'prescane',n,select=None,clim=(998,1002))

simfits.show(hdul,'overscan',n,select=None,clim=(998,1002))
simfits.show(hdul,'overscan',n,select=[0,25,500,600],clim=(998,1002))



###############################################################################
###########             BIAS (reverse clocking)
###############################################################################

mean_biases = {}

for ccd_side in ["E","F"]:
  print(f"ccd_side {ccd_side}")
  simfile = fitsdir + stem + '_' + ccd_side + "_bias.fits"

  hdul = pyfits.open(simfile)
  #hdul.info()

  list_image,list_prescane,list_prescanf,list_overscan = simfits.info(hdul)
  
  list_image = list_image[:10]

  # Average bias value / image
  rbiases = np.zeros_like(list_image,dtype=float)
  for i,im_id in enumerate(list_image):
    data = hdul[im_id].data
    rbiases[i] = cv.robustf(data, np.mean, sigma=2.)
    print(f"{i:2d}, {np.mean(data):9.4f}, {rbiases[i]:9.4f}")

  cv.stats(rbiases)

  mean_biases[ccd_side] = np.mean(rbiases)

print(mean_biases)



###############################################################################
###########              DARK 
###############################################################################


ccd_side = 'E'
simfile = fitsdir + stem + '_' + ccd_side + ".fits"
print(simfile)

hdul = pyfits.open(simfile)
hdul.info()

list_image,list_prescane,list_prescanf,list_overscan = simfits.info(hdul)

nimages = len(list_image)

mean_raw = np.zeros_like(simfits.get(hdul,n=1,field_type="image"),dtype=float)
mean_sub = np.zeros_like(simfits.get(hdul,n=1,field_type="image"),dtype=float)

for i in range(nimages):
    data = simfits.get(hdul,n=i,field_type="image")
    scan = simfits.get(hdul,n=i,field_type="prescan"+str(ccd_side).lower())
    sub  = data - np.mean(scan)
    
    mean_raw = mean_raw + data
    mean_sub = mean_sub + sub
    print(f"{i:2d} Raw {np.mean(data):9.4f}   Bias {np.mean(scan):9.4f}   Sub {np.mean(data) - np.mean(scan):9.4f}")

mean_raw = mean_raw / nimages
mean_sub = mean_sub / nimages

cv.stats(mean_raw)
cv.stats(mean_sub)

texp = 20.985  # sec  (25 - 4510 * (110e-6 + 2295*340e-9))
gain = 20      # e- / adu

dark_raw = (mean_raw - mean_biases[ccd_side]) / texp * gain
dark_sub = mean_sub / texp * gain

cv.stats(dark_raw)
cv.stats(dark_sub)

cv.stats(dark_raw-dark_sub)


###############################################################################
#############           FINAL VISUALISATION 
###############################################################################

plt.figure("Dark bulk",figsize=(6,12))
plt.imshow(dark_raw,interpolation="nearest",origin="lower",cmap='jet',clim=(1,2))
plt.xlabel("Column")
plt.ylabel("Row")
plt.title("Dark Current [e-/sec]")
plt.colorbar()

# CCD - Coordinates : ccd_side = 'E' --> "Right" half of the CCD
ccd_xE = np.arange(dark_raw.shape[1]) - hdul[1].header["CRPIX1"]

dark_profile_raw = np.mean(dark_raw,axis=0)

plt.figure("Dark profile",figsize=(6,12))
plt.plot(ccd_xE,dark_profile_raw,'k-')
plt.xlabel("Column")
plt.ylabel("Dark Current [e-/sec]")
plt.title(f"Dark Profile -- CCD side {ccd_side}")



