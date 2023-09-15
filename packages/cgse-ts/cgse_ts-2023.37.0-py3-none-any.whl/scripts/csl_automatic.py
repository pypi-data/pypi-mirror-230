"""
from egse.reload import reload_module, reload_function

import camtest.analysis.functions.hartmann_utils

analysis_single_cube = reload.reload_function(analysis_single_cube)

fovu.coords_circle = reload_function(fovu.coords_circle)

fovu = reload_module(fovu)

camtest.analysis.functions.hartmann_utils = reload_module(camtest.analysis.functions.hartmann_utils)
"""

#######################################
### SCRIPTS CSL GUI
#######################################




### SINGLE POSITION ###

# Commanding
from camtest.commanding.cam_aat_050_single_no_pointing import single_no_pointing
execute(single_no_pointing)



# Reduction & Analysis
from camtest.analysis import convenience as cv
from camtest.analysis.functions.hartmann_utils import analysis_single_cube

datadir = '/Volumes/IZAR/plato/data/em/csl/obs/'
obsid = 840 # single
sobsid = str(obsid).zfill(5)

esize = analysis_single_cube(obsid=obsid, datadir=datadir, ref_size=23.82, layer_selection=None)

### CIRCLE ###

# Commanding
# ----------
from camtest.commanding.cam_aat_050_ambient_circle import cam_aat_050_ambient_circle
execute(cam_aat_050_ambient_circle, num_cycles=5, exposure_time=0.2, elevation=8.3, n_pos=20, n_rows=1500, reverse_order=False, description="Ambient. 1 atm. Reference circle at 8.3 deg of elevation")

# Reduction
# ---------
import numpy as np
import camtest.analysis.functions.fov_utils as fovu
from camtest.analysis.functions.hartmann_utils import hartmann_reduction

datadir = "/Volumes/IZAR/plato/data/em/ias/obs/"
outputdir = "/Volumes/IZAR/plato/data/reduced/"

n_pos = 20
theta = 8.3

angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides = \
    fovu.coords_circle(n_pos=n_pos, theta=theta, distorted=True, reverse_order=False,verbose=True)

obsid = 227
nlayers = 5
layer_selection = None
layer_selection = np.array([1,2,3,4],dtype=int)
cube_selection = None

ctab = hartmann_reduction(obsid=obsid, nlayers=nlayers, layer_selection=layer_selection, cube_selection=cube_selection,
                          fov_angles=angles_in, datadir=datadir, outputdir=outputdir, verbose=True)


# Analysis
# ---------
import os
import numpy as np
import matplotlib.pyplot as plt
import camtest.analysis.convenience as cv
from camtest.analysis.functions import hartmann_utils

#print(os.getenv("PLATO_LOCAL_DATA_LOCATION"))

pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
reduceddir = "/Volumes/IZAR/plato/data/reduced/"

# obsids : list of [obsid, site, plot_label]
obsids = []
obsids.append([900, "CSL", "CSL Final"])
obsids.append([2088, "SRON", "SRON EM1 Start"])
obsids.append([2292, "SRON", "SRON EM1 End"])
obsids.append([2441, "SRON", "SRON EM2 Start"])
obsids.append([3344, "SRON", "SRON EM2 End"])
obsids.append([227, "IAS", "IAS EM Start"])

# Fit a sinewave --> determine a tilt wrt the OA : TBW
plotname = hartmann_utils.hartmann_analysis_circle(obsids, datadir=reduceddir, figname="Circle", verbose=True)
plt.savefig(pngdir + plotname)



### HARTMANN ###

# Commanding
from camtest.commanding.cam_aat_050_ambient_hartmann_verification \
       import cam_aat_050_ambient_hartmann_verification

# use_angles : False: [x,y] positions from LDO. True : computed FoV angles [theta,phi]
use_angles = False
exposure_time = 0.2
execute(cam_aat_050_ambient_hartmann_verification, \
    num_cycles=5, exposure_time=exposure_time,n_rows=1000, \
    table_name='reference_full_40', use_angles=use_angles, description="Ambient Hartmann Verif 40 positions")


# Reduction -- Hartmann
import numpy as np
import camtest.analysis.functions.fov_utils as fovu
from camtest.analysis.functions.hartmann_utils import hartmann_reduction

use_angles, distorted_input = False, True # Hartmann (LDO x,y positions)
use_angles, distorted_input = True, False # Flexible (computed thetas & phis)

[angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides] =\
    fovu.coords_from_table(table_name="reference_full_40", use_angles=use_angles, distorted_input=distorted_input,
                           distorted_output=True, sort_fov_pos_in_azimuth=False, reverse_order=False, verbose=True)

datadir = "/Volumes/IZAR/plato/data/em/sron/obs/"
outputdir = "/Volumes/IZAR/plato/data/reduced/"
obsid = 3348
nlayers = 5
layer_selection = np.array([1,2,3,4],dtype=int)
cube_selection = None

ctab = hartmann_reduction(obsid=obsid, nlayers=nlayers, layer_selection=layer_selection, cube_selection=cube_selection,
                          fov_angles=angles_in, datadir=datadir, outputdir=outputdir, verbose=True)


# Analysis

import matplotlib.pyplot as plt
from camtest.analysis.functions import hartmann_utils

pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
reduceddir = "/Volumes/IZAR/plato/data/reduced/"

# obsids : list of [obsid, site, plot_label]
obsids = []
obsids.append([642, "CSL", "CSL Pre-Bolting"])
obsids.append([842, "CSL", "CSL Post-Bolting"])
# obsids.append([2442, "SRON", "SRON EM2 Start"])
# obsids.append([3320, "SRON", "SRON EM2 Warmup"])
# obsids.append([3348, "SRON", "SRON EM2 Warmup"])

maxsize = 100
taus = [66, 65, 60, 50]
plotname = hartmann_utils.hartmann_analysis_full40(obsids, taus=taus, datadir=reduceddir, maxsize=maxsize, figname=None, verbose=True)
plt.savefig(pngdir + plotname)




### INGESTION OF A NEW CSLReferenceFrameModel
from camtest import load_setup
setup = load_setup(setup_id=97, site_id="CSL", from_disk=True)
print(setup.get_id())


from camtest.commanding.functions.csl_functions import csl_model_from_file, prepare_hexapod

## 1. Model creation
#filename = "006_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"
filename = "PLATO-CSL-PL-RP-00xx_CSL_RFModel_CamName_Beer_ROT_Template.xlsx"
location = "/Users/pierre/plato/plato-cgse-conf/data/CSL/conf/"

model, setup = csl_model_from_file(filename=filename, location=location, setup=setup, verbose=True)

## 2. Submit new setup
setup_description = f"CSL Reference Frame Model {filename}"
setup = submit_setup(setup, f"CSLReferenceFrameModel {setup_description}")
setup = load_setup()

## 3. Configure Hexapod
hexhw = prepare_hexapod(model=model, setup=None)

