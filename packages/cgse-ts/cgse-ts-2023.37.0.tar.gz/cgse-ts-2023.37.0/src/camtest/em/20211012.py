from camtest import start_observation, end_observation, execute
from camtest.commanding import ogse, aeu, dpu
from camtest.commanding.csl_gse import csl_point_source_to_fov
from egse.setup import load_setup

setup = load_setup()


# AEU + OGSE switch-on

start_observation("Switch on procedure: AEU + OGSE")  # obsid =

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())


end_observation()

# On the client: dpu_ui

execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode

print(dpu.n_cam_is_standby_mode())

execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())

# Test position - test image to confirm everything is alright

execute(csl_point_source_to_fov, theta=8.3, phi=-5, wait=False)  # obsid = 853

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3500,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid = 854

csl_dict = model.serialize()
setup.csl_model.model = csl_dict
setup.csl_model.laser_tracker_data = "006_csl_refFrames_CSL-PL-RP-0019_EM_AlignmentReport.xls"
print(setup)
setup = submit_setup(
    setup, "CSLReferenceFrameModel EM 006 20211012 - bolted"
)
print(setup)    # 87

setup = load_setup()


# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: AEU and OGSE")

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()

ogse.ogse_swoff()

end_observation()




start_observation("Switch on procedure: AEU")

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()
