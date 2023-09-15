from camtest import load_setup, start_observation, end_observation, execute
from camtest.analysis.convenience import printm
from camtest.commanding import aeu, dpu, ogse
from camtest.commanding.csl_gse import is_model_sync
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.hexapod.symetrie.puna import PunaProxy

# Load the Setup from the configuration manager

setup = load_setup()    # setup 86
print(setup)

# Extract the model from the Setup

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

# Get the connection to the PUNA Hexapod

hexhw = PunaProxy()

# Check if the model and the hexapod are in sync

is_model_sync(model, hexhw)  # --> shall return True!

# Another way to check if the FPA is at bolting position

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("bolt"))
printm([trans, rot])


start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_00086_00???

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()

# On the server: dpu_cs start
# On the server: fitsgen start
# On the server: python -m egse.fee.n_fee_hk -platform offscreen

# On the client: dpu_ui

execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode

print(dpu.n_cam_is_standby_mode())

execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())

start_observation("Switch on procedure: OGSE")  # obsid = CSL_00086_00???

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())

end_observation()


n_fee_parameters = dict(
    num_cycles=5,
    row_start=1750,
    row_end=3250,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid = CSL_00086_00691
