import os

import matplotlib.pyplot as plt
import numpy as np

import camtest.analysis.convenience as cv
from camtest import list_setups, load_setup
from camtest.analysis.functions.hartmann_utils import analysis_hartmann_cubes
from camtest.analysis.valid_cubes import valid_cubes
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from camtest.commanding.functions.fov_test_geometry import plotCCDs
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles

#datadir = "/Volumes/IZAR/plato/data/em/sron/obs/"
datadir = os.getenv("PLATO_LOCAL_DATA_LOCATION")
#outputdir = "/Volumes/IZAR/plato/data/em/results/"
outputdir = "/Volumes/IZAR/plato/data/achel/pngs/"



os.path.exists(datadir)

datafiles = os.listdir(datadir)

##################################################################
# SETUP
##################################################################
list_setups()
#setup = load_setup(86, site_id="CSL", from_disk=True)
setup = load_setup()
print(setup)

##################################################################
# COMMANDED CCD FOV & COORDINATES
##################################################################

boresight_angle = 3.1
boresight_angle = 12.4
boresight_angle = 16.33

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles_in, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
                                                                 [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
                                                                 reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, cside, ccd_side in zip(angles_in, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {cside:1.0f}   {ccd_side}")
    c += 1


thetas_in = angles_in[:,0]
phis_in = angles_in[:,1]

fpcoords_comm = np.array([ccd_to_focal_plane_coordinates(crow,ccol,ccode) for crow,ccol,ccode in zip(ccdrows,ccdcols,ccdcodes)])
angles_comm   = np.array([focal_plane_coordinates_to_angles(xxfp,yyfp) for xxfp,yyfp in zip(fpcoords_comm[:,0],fpcoords_comm[:,1])])
thetas_comm = angles_comm[:,0]
phis_comm   = angles_comm[:,1]

pars_comm, circle_comm = cv.fitCircle(fpcoords_comm)
cenx_comm,ceny_comm,radius_comm = pars_comm


plotCCDs(figname="FoV",setup=setup)
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro')

##################################################################
# FULL OBSID ANALYSIS
##################################################################



##################################################################
# IDENTIFY THE DATAFILES
##################################################################

obsid = 258
sobsid = str(obsid).zfill(5)

obsidir = cv.fileSelect([f'{sobsid}'],location=datadir)[0] + '/'

filenames = cv.fileSelect([f'{sobsid}_','fits'],location=datadir+obsidir)
cv.print1(filenames)
ffilenames = [datadir + obsidir + filename for filename in filenames]


##################################################################
# CHECK VALIDITY OF ALL CUBES
##################################################################

sel_valid = {}
try:
    sel_valid[obsid] = valid_cubes(obsid)
except:
    print("No predefined list of (in)valid cubes. Reducing all.")
    sel_valid[obsid] = np.arange(len(filenames))

print(f"{len(sel_valid[obsid])} valid cubes for {obsid=} : {sel_valid[obsid]}")

##################################################################
# AUTOMATIC REDUCTION
##################################################################

nlayers = 5

skip_layer_0 = True
layer_selection = None
postfix = None

skip_layer_0 = False
layer_selection = [1,2,3,4]
postfix = "EFOK"

ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=sel_valid[obsid], nlayers=nlayers, angles_in=angles_in,
                               outputdir=outputdir, overwrite=True, verbose=True, skip_layer_0=skip_layer_0,
                               layer_selection=layer_selection, postfix=postfix)


##################################################################
# DISPLAY FOV LOCATIONS VISITED (measured vs commmanded)
##################################################################

fpcoords_meas = ctab["fpcoords_meas"]
pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[sel_valid[obsid],:])  # kick the NaNs out!!
cenx_meas,ceny_meas,radius_meas = pars_meas
distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")


plotCCDs(figname="FoV",setup=setup)
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro', label="Comm")
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1], 'go', label="Meas")
plt.legend(fontsize=14)
plt.title(f"{obsid=}", size=20)

pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
plt.savefig(pngdir+f"em_compare_csl_out_sron_{obsid}_fov_comm_vs_meas_positions.png")



##################################################################
# MULTI-OBSID LOOP -- e.g. cooldown
##################################################################

nlayers = 5

skip_layer_0 = True
layer_selection = None
postfix = None


obsids = [i for i in range(2510,2513)]
obsids = [i for i in range(2513,2517)]
for obsid in obsids:
    print()
    print(obsid)
    print()

    sobsid = str(obsid).zfill(5)
    obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
    filenames = cv.fileSelect([f'{sobsid}_', 'fits'], location=datadir + obsidir)
    cv.print1(filenames)
    ffilenames = [datadir + obsidir + filename for filename in filenames]

    sel_valid = {}
    try:
        sel_valid[obsid] = valid_cubes(obsid)
    except:
        print("No predefined list of (in)valid cubes. Reducing all.")
        sel_valid[obsid] = np.arange(len(filenames))
    print(f"{len(sel_valid[obsid])} valid cubes for {obsid=} : {sel_valid[obsid]}")

    ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=sel_valid[obsid], nlayers=nlayers, angles_in=angles_in,
                               outputdir=outputdir, overwrite=True, verbose=True, skip_layer_0=skip_layer_0,
                               layer_selection=layer_selection, postfix=postfix)


