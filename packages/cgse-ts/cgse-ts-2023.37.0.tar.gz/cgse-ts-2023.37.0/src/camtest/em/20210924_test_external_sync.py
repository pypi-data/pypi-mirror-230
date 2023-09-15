from camtest import load_setup, start_observation, end_observation, execute
from camtest.commanding import aeu, dpu, ogse

setup = load_setup()
print(setup)  # Setup 73


# SYSTEM SWITCH ON ---------------------------------------------------------------------------------

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode external sync")  # obsid = 613

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

# On the server: dpu_cs start
# On the server: fitsgen start
# On the server: python -m egse.fee.n_fee_hk -platform offscreen

# On the client: dpu_ui

dpu.n_cam_to_standby_mode()

# Wait until in standby mode

dpu.n_cam_is_standby_mode()

dpu.n_cam_to_dump_mode()

dpu.n_cam_is_dump_mode()

end_observation()

start_observation("Switch on procedure: OGSE")  # obsid = 614

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()

end_observation()

start_observation("Test external sync mode")    # obsid 615

n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=499,
    rows_final_dump=4510,
    ccd_order=[1, 2, 3, 4],
    ccd_side="F"
)

dpu.n_cam_partial_ccd(**n_fee_parameters)

end_observation()

execute(dpu.n_cam_to_standby_mode)  # 616

execute(aeu.n_cam_sync_disable)     # 617
execute(aeu.n_cam_swoff)    # 618

execute(ogse.ogse_swoff)   # 619
