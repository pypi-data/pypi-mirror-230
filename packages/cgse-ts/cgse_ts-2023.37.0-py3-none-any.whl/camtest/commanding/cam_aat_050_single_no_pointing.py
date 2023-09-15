from camtest import building_block
from camtest.commanding import dpu

@building_block
def single_no_pointing():
    n_fee_parameters = dict(
        num_cycles=3,
        row_start=4000,
        row_end=4509,
        rows_final_dump=4510,
        ccd_order=[3,3,3,3],
        ccd_side="F",
        exposure_time=0.2
    )

    dpu.n_cam_partial_int_sync(**n_fee_parameters)

