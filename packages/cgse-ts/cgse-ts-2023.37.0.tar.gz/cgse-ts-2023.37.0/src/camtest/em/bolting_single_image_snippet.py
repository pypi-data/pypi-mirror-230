from camtest.analysis.functions.hartmann_utils import analysis_single_cube
from camtest.commanding.cam_aat_050_ambient_ref_image_bolting import single_ref_image_bolting_em
from camtest import execute

# IMAGE ACQUISITION
execute(single_ref_image_bolting_em)

# IMAGE ANALYSIS  (CHANGE OBSID !)
#datadir = "/Volumes/IZAR/plato/data/em/csl/obs/"
datadir = "/data/CSL/obs/"

obsid = 840
esize = analysis_single_cube(obsid=obsid, datadir=datadir, ref_size=23.82, layer_selection=None)


"""
for obsid in range(834,838):
    esize = analysis_single_cube(obsid=obsid, datadir=datadir, ref_size=23.82)#, layer_selection=[2])
"""

