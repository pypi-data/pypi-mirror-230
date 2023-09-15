import os
import time

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib import cm

from camtest import load_setup
import camtest.analysis.convenience as cv
from camtest.analysis.functions import hk_utils as hk
from camtest.analysis import image_utils as iu

from camtest.analysis.observation import download_observation, Observation

datadir = "/Volumes/IZAR/plato/data/em/csl/obs/"
datadir = "/Volumes/IZAR/plato/data/csl2/obs/"
datadir = os.getenv("PLATO_LOCAL_DATA_LOCATION")
print(datadir)

camera = "brigand"
camera = "chimay"
pngdir = f"/Volumes/IZAR/plato/data/{camera}/pngs/"

os.path.exists(datadir)

datafiles = os.listdir(datadir)

fontsize = 14

# ======================================================================================================================
# setup = load_setup(setup_id=35, site_id="CSL1", from_disk=True)
setup = load_setup(setup_id=65)
setup = load_setup(setup_id=38, site_id="CSL2", from_disk=True)
print(setup)

# DOWNLOAD OBSID
obsid = 228

download_observation(obsid, site="CSL2",setup=setup, data_dir=datadir)
download_observation(obsid)#, selection='csv')

# DOWNLOAD LIST OF OBSIDS
for obs in [i for i in range(202,211)]:
for obs in [939,945]:
    #download_observation(obsid)  # , selection='csv')
    download_observation(obs, site="CSL1", setup=setup, data_dir=datadir)
# ======================================================================================================================
# AVAILABLE CUBES
obsid = 966
sobsid = str(obsid).zfill(5)

try:
    print("PFM - FM")
    obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
    filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir + obsidir)
    ffilenames = [datadir + obsidir + filename for filename in filenames]
except:
    print("EM")
    filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir)
    ffilenames = [datadir + filename for filename in filenames]

cv.print1(ffilenames)


"""
# EM CSL
obsid = 900
filenames = cv.fileSelect([f'00{obsid}_','cube','fits'],location=datadir)
cv.print1(filenames)
ffilenames = [datadir+filename for filename in filenames]
"""

# ======================================================================================================================
# STRUCTURAL QUICK LOOK

# Verify the nb of layers in all cubes of the given obsid & the shape of the datacubes
for cn in range(len(ffilenames)):
    hduc = fits.open(ffilenames[cn])
    time.sleep(0.25)
    print(f"{cn:3d} {hduc[2].data.shape}")

# ======================================================================================================================
# DETAILED STRUCTURE -- FITS EXTENSIONS

# Verify the nb of layers in all cubes of the given obsid & the shape of the datacubes
for cn in range(len(ffilenames)):
    hduc = fits.open(ffilenames[cn])
    time.sleep(0.25)
    print(f"CUBE {cn}")
    hduc.info()
# ======================================================================================================================
# DISPLAY ONE SINGLE LAYER

cn = 8
en = 2  # Extension 2 is usually the first IMAGE extension
ln = 1
iu.show_layer(cube_number=cn, layer_number=ln, filenames=ffilenames, extension=en, obsid=obsid, rowrange=None, colrange=None, vsigma=2, cmap=cm.hot)
iu.show_layer(cube_number=cn, layer_number=ln, filenames=ffilenames, extension=en, obsid=None, vmin=5900, vmax=6100, cmap=cm.inferno)
iu.show_layer(cube_number=cn, layer_number=ln, filenames=ffilenames, extension=en, obsid=None, vmin=3450, vmax=4200, cmap=cm.hot)

layer = iu.get_layer(cube_number=cn, layer_number=ln, filenames=ffilenames, extension=en, rowrange=None, colrange=None)
print(layer.shape)

# ======================================================================================================================
# DISPLAY ONE LAYER OF EVERY CUBE

ln = 2
en = 2
for cn in range(len(ffilenames)):
    iu.show_layer(cn,ln,filenames=ffilenames, extension=en, obsid=obsid)

# ======================================================================================================================
# DISPLAY ALL LAYERS OF A SINGLE CUBE

cn = 4
for ln in range(5):
    iu.show_layer(cn,ln,filenames=ffilenames, extension=en,obsid=obsid)


# ======================================================================================================================
# EXTRACT A SINGLE IMAGE

cn = 0
hduc = fits.open(ffilenames[cn])
hduc.info()

hduc[0].header
hduc[2].header

cube = np.array(hduc[cn].data, dtype=float)
sccd = f"CCD_{hduc[cn].header['CCD_ID']}{hduc[2].header['SENSOR_SEL']}"
print(f"{sccd}")

ln=2
cv.stats(cube[ln,:,:])

cv.imshow(np.log10(cube[ln,:,:]))#,vmin=2,vmax=4)

# ======================================================================================================================
# EXTRACT FRAME TIMES (e.g. to compare with HK)
ftimes = cv.get_frame_times(ffilenames)

rtime = np.round(ftimes-ftimes[0], 3)
print(rtime)
print(np.diff(rtime))

# ======================================================================================================================
# EXTRACT HK VALUES DURING THE OBSERVATION

# Select HK source
device = "ENSEMBLE"
device = "PUNA"
device = "SYN-HK"

# A. Directly

# Extract the HK in an astropy.table.Table
hkt = hk.get_hk(obsid,device=device,datadir=datadir+obsidir)

# B. Via an Observation object

if datadir is None:
    obs = Observation(obsid=obsid, data_dir=None)  # if PLATO_LOCAL_DATA_LOCATION is defined; else set datadir to "/.../obs/"
else:
    obs = Observation(obsid=obsid, data_dir=datadir)  # if PLATO_LOCAL_DATA_LOCATION is defined; else set datadir to "/.../obs/"

hkt = obs.get_hk(device=device)

obs.get_hk_names(device=device)

reltime = hkt["finetime"]-hkt["finetime"][0]
plt.plot(reltime, hkt['GSYN_CCD4'], 'ko-')

print(np.round(reltime, 3))

#plt.plot(reltime, hk['GSRON_ENSEMBLE_ACT_CUR_X'])



# ======================================================================================================================
# INSPECT "FULL IMAGES", including pre- & over-scans

# cube_number = identifier of a given fits file in the list
cn = 0
# extension_number = identifier of the extension to be extracted from the fits file
# It can easily be slected from cv.print1(extnames), see below
en = 4
# layer_number = identifier of the desired layer in the cube
ln = 2

# Open the file manually
hduc = fits.open(ffilenames[cn])
hduc.info()


# Get the list of extensions in the target fits file & print them
# SPRE  = Serial PREscan
# SOVER = Serial OVERscan
# POVER = Parallel OVERscan
# WCS-TAB contains the time information
extnames = iu.get_extnames(cn, ffilenames)
cv.print1(extnames)

# Get a given extension
# The extension can be specified by number or by name
ext = iu.get_extension(cn, ffilenames, extension=3)
print(ext.header["EXTNAME"])


# Display the image data of a given CCD (full-CCD size for visualisation of partial readout)
# ccd_number : use if data from several CCDs are present in the selected fits file
#              ccd_number is mandatory if data from several CCDs are present in the selected fits file
# full : includes all available pre- and over-scans
# bckgndsub : includes a background subtraction (base on smoothing functions with median and gauss filters)
# See also iu.get_ccd
ccd_number = 1
img_1 = iu.show_ccd(cn, ln, filenames=ffilenames, ccd_number=ccd_number, vsigma=2, obsid=obsid, full=True, bckgndsub=False)

# Display the image data of all CCDs (full Focal Plane size)
# See also iu.get_allccds
img_4 = iu.show_allccds(cn, ln, filenames=ffilenames, vsigma=0.5, obsid=obsid, full=True, bckgndsub=False, vmin=1320, vmax=1420)
#plt.savefig(pngdir+f"{camera}_{obsid}_layer_{ln}_full.png")

# Visualize any given extension.
# The extension can be specified by number or by name
iu.show_extension(cn, ln, ffilenames, extension=en, obsid=169)

# Get one layer out of an extension, or just a sub-part of it
layer = iu.get_layer(cn, ln, ffilenames, extension=en, rowrange=[100,200], colrange=None)
print(layer.shape)

# Visualize individual rows/columns, or of their average profile
# avg=0/1: display average profile False/True. avg=2: display only the average profile, no individual row or column
iu.show_profile(cn, ln, ffilenames, extension=en, rowcol='row', rowrange=[1,4510], colrange=None, avg=2, figname='Row')
iu.show_profile(cn, ln, ffilenames, extension=en, rowcol='col', rowrange=None, colrange=None, avg=2, rainbow=False, legend=False, figname="Col")







