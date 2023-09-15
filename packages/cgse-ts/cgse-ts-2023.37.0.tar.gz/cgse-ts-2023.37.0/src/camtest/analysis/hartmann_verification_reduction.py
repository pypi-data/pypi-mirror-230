import os
import numpy as np
import matplotlib.pyplot as plt
import camtest.analysis.convenience as cv
from camtest import list_setups, load_setup
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth, fov_geometry_from_table
from camtest.commanding.functions.fov_test_geometry import plotCCDs
from camtest.analysis.functions.hartmann_utils import analysis_hartmann_cubes
from camtest.analysis.valid_cubes import valid_cubes
from astropy.io import ascii
from astropy.table import Column

datadir = "/Volumes/IZAR/plato/data/em/sron/obs/"
outputdir = "/Volumes/IZAR/plato/data/em/results/"

os.path.exists(datadir)

datafiles = os.listdir(datadir)

##################################################################
# SETUP
##################################################################
list_setups()
setup = load_setup()
print(setup)

##################################################################
# COMMANDED CCD FOV & COORDINATES
##################################################################

distorted_input = True
distorted = True

verbose = True
reverse_azimuth_order = False

table_name='reference_full_40'

use_angles=False
sort_fov_pos_in_azimuth = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, table_name=table_name, use_angles=use_angles, verbose=verbose)

if sort_fov_pos_in_azimuth:
    angles_in, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,[ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],reverse=reverse_azimuth_order)
else:
    angles_in, ccdrows, ccdcols, ccdcodes, ccdsides = anglesorig, ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles_in, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1

thetas_in = angles_in[:,0]
phis_in = angles_in[:,1]

fpcoords_comm = np.array([ccd_to_focal_plane_coordinates(crow,ccol,ccode) for crow,ccol,ccode in zip(ccdrows,ccdcols,ccdcodes)])
angles_comm   = np.array([focal_plane_coordinates_to_angles(xxfp,yyfp) for xxfp,yyfp in zip(fpcoords_comm[:,0],fpcoords_comm[:,1])])
thetas_comm = angles_comm[:,0]
phis_comm   = angles_comm[:,1]


#pars_comm, circle_comm = cv.fitCircle(fpcoords_comm)
#cenx_comm,ceny_comm,radius_comm = pars_comm


plotCCDs(figname="FoV",setup=setup)
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro-')

##################################################################
# FULL OBSID ANALYSIS
##################################################################


##################################################################
# IDENTIFY THE DATAFILES
##################################################################

obsid = 2442
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
    sel_valid[obsid] = np.arange(len(ffilenames))

print(f"{len(sel_valid[obsid])} valid cubes for {obsid=} : {sel_valid[obsid]}")

##################################################################
# AUTOMATIC REDUCTION
##################################################################

nlayers = 5

skip_layer_0 = True
layer_selection = None
postfix = None

ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=sel_valid[obsid], nlayers=nlayers, angles_in=angles_in,
                               outputdir=outputdir, overwrite=True, verbose=True, skip_layer_0=skip_layer_0,
                               layer_selection=layer_selection, postfix=postfix)


##################################################################
# Selected fields --> ASCII
##################################################################
# _in   = original fov angles, without distortion
# _comm = original fov angles, including distortion --> what to expect from commanding
# _meas = computed from measured sources' pixel coordinates

for ii, cc, mm in zip(ctab["theta_in"], ctab["theta_comm"], ctab["theta_meas"]):
    print(ii, cc, mm)
for ii, cc, mm in zip(ctab["phi_in"], ctab["phi_comm"], ctab["phi_meas"]):
    print(ii, cc, mm)

cns = Column(np.arange(72))

csel = ctab.copy()
csel.add_column(cns, name="pos", index=0)

for c in ctab.colnames:
    if len(ctab[c].shape) > 1:
        print(c, ctab[c].shape, "remove")
        csel.remove_column(c)
    else:
        print(c, ctab[c].shape)

print(csel.colnames)

ascii.write(csel, output=outputdir+f"obsid_{setup.site_id}_{setup.get_id()}_{str(obsid).zfill(5)}.txt", format="fixed_width", overwrite=True)


##################################################################
# DISPLAY FOV LOCATIONS VISITED (measured vs commmanded)
##################################################################

fpcoords_meas = ctab["fpcoords_meas"]
# pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[sel_valid[obsid],:])  # kick the NaNs out!!
# cenx_meas,ceny_meas,radius_meas = pars_meas
# distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
# print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")


plotCCDs(figname="FoV",setup=setup)
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro', label="Comm")
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1], 'go', label="Meas")
plt.legend(fontsize=14)
plt.title(f"{obsid=}", size=20)

pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
plt.savefig(pngdir+f"em_sron_{obsid}_fov_comm_vs_meas_positions.png")
plt.savefig(pngdir+f"em_compare_csl_out_sron_in_csl900_sron_{obsid}_fov_comm_vs_meas_positions.png")


