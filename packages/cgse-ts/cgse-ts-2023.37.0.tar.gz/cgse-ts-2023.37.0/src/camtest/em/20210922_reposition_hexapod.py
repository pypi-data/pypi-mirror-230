"""
This script will bring the Hexapod (FPA) back to the Hartmann plane.
We will use small steps when we move closer to L6.

The following steps are taken:

* lower the FPA to bring the L6 lens outside of the detector mask
* move hexapod to zero position
* run the prealignment script to regenerate the model EM 005 (model and hexapod shall be in sync afterwards)
* correct rotations
* correct x-y translations (not z)
* bring the hexapod to the Hartmann plane in small steps
* correct the latest x-y translations
* perform a test measurement at the Hartmann plane
* save the model in a new Setup and submit the Setup

"""
import rich

from camtest import execute
from camtest.analysis.convenience import printm
from camtest.commanding import dpu
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.commanding.csl_gse import hex_positions
from camtest.commanding.csl_gse import hexapod_puna_goto_zero_position
from camtest.commanding.csl_gse import is_model_sync
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.hexapod.symetrie.puna import PunaProxy
from egse.setup import load_setup
from egse.setup import submit_setup

hexhw = PunaProxy()

# We are now in retracted position

# Now move the hexapod to its zero position --------------------------------------------------------

move_ok = execute(hexapod_puna_goto_zero_position, wait=True)


##### WAIT UNTIL THE HEXAPOD IS AT ZERO POSITION #####


####################################################################################################
#                                                                                                  #
# At this point the hexapod is at zero position. Now we have to regenerate the proper model such   #
# that both the model and the hexapod are at zero position and in sync. The script to run is:      #
#                                                                                                  #
#    camtest/em/csl_alignment_fpa_prealignment_as_run_20210921.py                                  #
#                                                                                                  #
# After this script has run (up to line 500), we can continue here...                              #
#                                                                                                  #
####################################################################################################


setup = load_setup()  # --> shall return the newly created Setup that was saved in the previous script
print(setup)

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

is_model_sync(model, hexhw)  # --> shall return True!

verbose = True


# CORRECT ROTATIONS --------------------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 0.8914  0.4805 18.0496]
#  [ 0.175  -0.1543  0.2363]]

vtrans = [0, 0, 0]
vrot   = rot

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# CORRECTING X-Y TRANSLATION -----------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])

vtrans = [trans[0], trans[1], 0]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# START MOVING UP IN SMALL STEPS -------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 1.00000e-04 -2.00000e-04  1.80445e+01]
#  [-0.00000e+00 -0.00000e+00 -0.00000e+00]]

vtrans = [0, 0, 7]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# MOVING UP ----------------------------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 2.40000e-03  1.05000e-02  1.10445e+01]
#  [-0.00000e+00 -0.00000e+00 -0.00000e+00]]

vtrans = [0, 0, 5.0445]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# MOVING UP ----------------------------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 4.00e-03  1.82e-02  6.00e+00]
#  [-0.00e+00 -0.00e+00 -0.00e+00]]

vtrans = [0, 0, 3]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# MOVING UP ----------------------------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 0.005   0.0228  3.    ]
#  [-0.     -0.     -0.    ]]

vtrans = [0, 0, 2]
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)

# MOVING UP ----------------------------------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 0.0057  0.0258  1.    ]
#  [-0.     -0.     -0.    ]]

vtrans = trans
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

hex_positions(hexhw)


# CORRECT the latest X-Y translations --------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 0.0003  0.0015 -0.    ]
#  [-0.     -0.     -0.    ]]

vtrans = trans
vrot   = [0, 0, 0]

move_ok = execute(check_and_move_relative_user,
                  cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])
# [[ 0. -0. -0.]
#  [-0. -0. -0.]]


# Test the positioning at the Hartmann flat plane -------------------------------------------------------

execute(csl_point_source_to_fov,
        theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False)  # obsid =

n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid =


# Serialize and save the model in a new Setup ------------------------------------------------------

csl_dict = model.serialize()
setup.csl_model.model = csl_dict
rich.print(setup)
setup = submit_setup(
    setup, "CSLReferenceFrameModel EM 006 20210922 - bringing FPA at Hartmann flat plane"
)
rich.print(setup)

setup = load_setup()
