"""
PLATO-TEST-SCRIPTS/CAMTESTS/COMMANDING

Commanding building blocks for the DPU, FEEs, CCDs, ambient and TVAC.

Versions:
    * check the git commit messages or the git history for this module
"""
import logging
import time
from typing import Callable
from typing import List
from typing import Tuple

from deepdiff import DeepDiff
from rich.console import Console
from rich.table import Table

from camtest.commanding import aeu
from camtest.core.exec import building_block
from egse.decorators import deprecate
from egse.dpu import DPUInterface, DPUProxy
from egse.dpu import DPUMonitoring
from egse.exceptions import Abort
from egse.fee import convert_ccd_order_list
from egse.fee import fee_sync_mode
from egse.fee import n_fee_mode
from egse.reg import RegisterMap
from egse.setup import SetupError
from egse.state import GlobalState

MODULE_LOGGER = logging.getLogger(__name__)


@building_block
def n_cam_partial_int_sync(num_cycles=None, row_start=None, row_end=None,
                           rows_final_dump=None, ccd_order=None, ccd_side=None,
                           exposure_time=None):
    """
    Acquire the specified number of full images at ambient. The N-FEE will be configured to use its
    internal clock. The cycle time will be calculated from the given exposure time, the number
    of rows to readout/transmit, and the number of rows to dump.

    After the number of cycles has been reached, the N-FEE is configured back into
    internal sync dump mode.

    Args:
        num_cycles: Number images to acquire. If zero, images will continue to be acquired until
            the FEE is set to STANDBY or DUMP mode again.
        row_start: First row to read out
        row_end: Last row to read out (inclusive)
        rows_final_dump: number of rows for the clearout after the readout
        ccd_order: list of four integers containing the CCD numbers 1, 2, 3, 4
        ccd_side: 'E', 'F', or 'BOTH'
        exposure_time: required exposure time [s].
    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    # Command the DPU to put the FEE in full-image mode and acquire the
    # requested number of images.  Afterwards, the FEE is set to STANDBY or DUMP
    # mode again.

    # set_fee_full_image_mode is a generic name for
    # set_n_fee_full_image_mode & set_f_fee_full_image_mode
    # These 2 have a different signature --> we pass a dictionary

    n_fee_parameters = {
        "num_cycles": num_cycles,
        "dump_mode_int": True,  # make sure internal sync dump mode is called at the end
        "row_start": row_start,
        "row_end": row_end,
        "rows_final_dump": rows_final_dump,
        "ccd_order": ccd_order,
        "ccd_side": ccd_side,
        "cycle_time": n_cam_texp_to_tsync(exposure_time, row_start, row_end, rows_final_dump)
    }

    MODULE_LOGGER.info(f"The cycle time will be configured to {n_fee_parameters['cycle_time']}s.")

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    MODULE_LOGGER.debug(f"arguments to dpu.n_fee_set_full_image_mode_int_sync: {dpu_pars=}")
    dpu.n_fee_set_full_image_mode_int_sync(dpu_pars)

    # When a finite number of images were requested (num_cycles > 0), check if the acquisition
    # is over every "time_request_granularity" seconds, otherwise, just return.

    if num_cycles:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)


@building_block
def n_cam_acquire_and_dump(num_cycles=None, row_start=None, row_end=None,
                      rows_final_dump=None, ccd_order=None, ccd_side=None):
    """
    Acquire images during the specified number of cycles (25 sec), with the N-FEE in
    full-image mode (incl. partial readout). The N-FEE will use the external sync signal
    from the AEU.

    The Dump Gate bit is set to True in the NFEE register.

    After the number of cycles has been reached, the N-FEE is configured back into dump mode.

    Args:
        num_cycles: Number images to acquire. If zero, images will continue to be acquired until
            the FEE is set to STANDBY or DUMP mode again.
        row_start : First row to read out.
        row_end   : Last row to read out (inclusive).
        rows_final_dump: number of rows for the clearout after the readout
        ccd_order : list of 4 integers, e.g. [1,2,3,4]
        ccd_side: 'E', 'F', or 'BOTH'
    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    # Here we don't have to set the exposure time!

    # Command the DPU to put the FEE in full-image mode and acquire the
    # requested number of images.  Afterwards, the FEE is set to STANDBY or DUMP
    # mode again.

    n_fee_parameters = {
        "num_cycles":  num_cycles,
        "row_start":  row_start,
        "row_end":  row_end,
        "rows_final_dump":  rows_final_dump,
        "ccd_order":  ccd_order,
        "ccd_side":  ccd_side,
    }

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    dpu.n_fee_set_full_image_mode(dpu_pars)

    # Set Dump Gate to High
    dpu.n_fee_set_register_value('reg_5_config', 'DG_en', 1)

    # When a finite number of images were requested (n>0), check if the acquisition
    # is over every "time_request_granularity" seconds, otherwise, just return immediately.

    if num_cycles:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)



@building_block
def n_cam_partial_ccd(num_cycles=None, row_start=None, row_end=None,
                      rows_final_dump=None, ccd_order=None, ccd_side=None):
    """
    Acquire images during the specified number of cycles (25 sec), with the N-FEE in
    full-image mode (incl. partial readout). The N-FEE will use the external sync signal
    from the AEU.

    After the number of cycles has been reached, the N-FEE is configured back into dump mode.

    Args:
        num_cycles: Number images to acquire. If zero, images will continue to be acquired until
            the FEE is set to STANDBY or DUMP mode again.
        row_start : First row to read out.
        row_end   : Last row to read out (inclusive).
        rows_final_dump: number of rows for the clearout after the readout
        ccd_order : list of 4 integers, e.g. [1,2,3,4]
        ccd_side: 'E', 'F', or 'BOTH'
    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    # Here we don't have to set the exposure time!

    # Command the DPU to put the FEE in full-image mode and acquire the
    # requested number of images.  Afterwards, the FEE is set to STANDBY or DUMP
    # mode again.

    n_fee_parameters = {
        "num_cycles":  num_cycles,
        "row_start":  row_start,
        "row_end":  row_end,
        "rows_final_dump":  rows_final_dump,
        "ccd_order":  ccd_order,
        "ccd_side":  ccd_side,
    }

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    dpu.n_fee_set_full_image_mode(dpu_pars)

    # When a finite number of images were requested (n>0), check if the acquisition
    # is over every "time_request_granularity" seconds, otherwise, just return immediately.

    if num_cycles:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)


@building_block
def n_cam_partial_cycle_config(num_cycles=None,
                               row_start=None, row_end=None, rows_final_dump=None,
                               ccd_order=None, ccd_side=None, cycle_time=None):
    """
    Same as n_cam_partial_ccd, but allowing to configure the cycle duration from 25 to 50 sec,
    by steps of 6.25 sec.
    """

    # Set the requested AEU Sync Period
    aeu.n_cam_sync_enable(image_cycle_time=cycle_time)

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=row_start,
        row_end=row_end,
        rows_final_dump=rows_final_dump,
        ccd_order=ccd_order,
        ccd_side=ccd_side
    )

    n_cam_partial_ccd(**n_fee_parameters)

    # Reset the requested AEU Sync Period to its default
    # FIXME: This should probably only be called when num_cycles > 0
    aeu.n_cam_sync_enable()


@building_block
def n_cam_full_ccd(num_cycles=None, ccd_order=None, ccd_side=None, rows_overscan=None):
    """
    Acquire images during the specified number of cycles (25 sec), with the N-FEE in full-image
    mode (incl. partial readout).

    Args:
        num_cycles: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to STANDBY or
            DUMP mode again.
        ccd_order: list of 4 integers, e.g. [1,2,3,4]
        ccd_side: 'E', 'F', or 'BOTH'
        rows_overscan: number of rows to acquire in the parallel overscan
    """

    row_start = 0
    row_end = 4509 + rows_overscan
    rows_final_dump = 0

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=row_start,
        row_end=row_end,
        rows_final_dump=rows_final_dump,
        ccd_order=ccd_order,
        ccd_side=ccd_side
    )

    n_cam_partial_ccd(**n_fee_parameters)


@building_block
def n_cam_full_standard(num_cycles=None, ccd_side=None):
    """
    Acquire images during the specified number of cycles (25 sec), with the N-FEE in
    full-image mode, i.e. 4510 CCD rows + 30 parallel overscan rows.

    Args:
        num_cycles: Number images-cycles to acquire. One cycle = 1 long sync pulse period = 25 sec
            If zero, images will continue to be acquired until the FEE is set to STANDBY or
            DUMP mode again.
        ccd_side: 'E', 'F', or 'BOTH'
    """

    row_start = 0
    row_end = 4509 + 30
    rows_final_dump = 0
    ccd_order = [1, 2, 3, 4]

    n_cam_partial_ccd(num_cycles=num_cycles, row_start=row_start, row_end=row_end,
                      rows_final_dump=rows_final_dump, ccd_order=ccd_order, ccd_side=ccd_side)


@building_block
def n_cam_window(num_cycles=None, ccd_order=None, ccd_side=None):
    """
    Acquire images during the specified number of cycles (25 sec), with the N-FEE in full-image mode (incl. partial readout).

    Args:
        num_cycles: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to STANDBY or DUMP mode again.
        ccd_order = list of 4 integers, e.g. [1,2,3,4]
        ccd_side: 'E', 'F', or 'BOTH' (BOTH is standard in FEE "windowing mode")
    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    # Here we don't have to set the exposure time!

    # Command the DPU to put the FEE in full-image mode and acquire the
    # requested number of images.  Afterwards, the FEE is set to STANDBY or DUMP
    # mode again.

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["ccd_order"] = ccd_order
    n_fee_parameters["ccd_side"] = ccd_side     # TODO This still needs to be converted!

    dpu.n_fee_set_windowing_mode(n_fee_parameters)

    # When a finite number of images were requested (n>0), check if the acquisition
    # is over every "time_request_granularity" seconds,

    if num_cycles != 0:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)


@building_block
def n_cam_window_upload(window_list=None, window_size=None, ccd_id=None):
    """
        Upload the windowing parameters to the N-FEE

        Args:
            window_list: array of window_coordinates. Dimensions [n,2]
            window_size: window_size [in pixels]
            ccd_id     : CCD identifier on which this window-list is applicable (in [1,2,3,4])

        xmin,xmax,ymin,ymax for window i = window_list[i,0], window_list[i,0]+window_size, window_list[i,1], window_list[i,1]+window_size

    """

    dpu = GlobalState.setup.camera.dpu.device

    n_fee_parameters = dict()
    n_fee_parameters["window_list"] = window_list
    n_fee_parameters["window_size"] = window_size
    n_fee_parameters["ccd_id"]      = ccd_id

    dpu.n_fee_upload_windows(n_fee_parameters)


@building_block
def n_cam_reverse_clocking(
        num_cycles=None, clock_dir_serial=None, ccd_order=None, ccd_side=None):
    """
    Reverse clocking is described in PLATO-MSSL-PL-TN-0015 (v1.0).
    It exists in two flavors, depending the operation of the readout register:
    1: serial REV
    2: serial FWD
    Both modes provide a reliable measure of the readout noise,
    but only the second one guarantees a reliable measure of the offset

    In both cases, the parallel clocks are REV.

    No "images" are acquired in reverse clocking → a handful of "frames" are usually sufficient

    Args:
        num_cycles: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to DUMP mode again.
        clock_dir_serial: "FWD" for representative digital offset, else "REV"
        ccd_order: list of 4 integers, e.g. [1,2,3,4]
        ccd_side: GlobalState.setup.camera.fee.ccd_sides.enum..E (or F, ALT or BOTH)

    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        clock_dir_serial=clock_dir_serial,
        clock_dir_parallel="REV",
        ccd_order=ccd_order,
        ccd_side=ccd_side,
    )

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    dpu.n_fee_set_reverse_clocking(dpu_pars)

    # When a finite number of images were requested (n>0), check if the acquisition
    # is over every "time_request_granularity" seconds,

    if num_cycles:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)


def load_and_inspect_register_map():
    def tf(x): return "True" if x else "False"

    dpu_dev = GlobalState.setup.camera.dpu.device

    reg_map = dpu_dev.n_fee_sync_register_map()

    vgd_19 = reg_map[('reg_19_config', 'ccd_vgd_config')]
    vgd_20 = reg_map[('reg_20_config', 'ccd_vgd_config')]
    vgd = (vgd_20 << 4) + vgd_19

    MODULE_LOGGER.info(
        f"Register map:\n"
        f"N-FEE mode = {n_fee_mode(reg_map['ccd_mode_config']).name}\n"
        f"CI width   = {reg_map['charge_injection_width']}\n"
        f"CI gap     = {reg_map['charge_injection_gap']}\n"
        f"CI enabled = {tf(reg_map['charge_injection_en'])}\n"
        f"V-GD       = 0x{vgd:X} -> {vgd / 1000 * 5.983:.2f}\n"
        f"IG Low     = {reg_map['ccd_ig_lo_config']}\n"
        f"IG High    = {reg_map['ccd_ig_hi_config']}\n"
        f"digitise   = {tf(reg_map['digitise_en'])}\n"
        f"DG         = {tf(reg_map['DG_en'])}\n"
    )


@building_block
def n_cam_charge_injection_full(
        num_cycles=None, row_start=None, row_end=None, rows_final_dump=None,
        ccd_order=None, ccd_side=None, ci_width=None, ci_gap=None, vgd=None):
    """
    Charge injection in N-FEE full image mode.

    Args:
        num_cycles: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to DUMP mode again.
        row_start : First row to read out.
        row_end   : First row not to read out.
        rows_final_dump: number of rows for the clearout after the readout
        ccd_order : list of 4 integers, e.g. [1,2,3,4]
        ccd_side  sensor_sel.E (or F, ALT or BOTH)
        ci_width  : width of each charge-injection region, in number of rows
        ci_gap    : nb of rows between the charge-injection regions
        vgd       : V_GD voltage, driving charge-injection level
                    V_GD ~ 14 : FWC
                    V_GD = 15 ~ 70% FWC
                    V_GD = 16 ~ 50% FWC
                    V_GD = 17 ~ 30% FWC
    """

    sensor_sel = GlobalState.setup.camera.fee.sensor_sel.enum

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=row_start,
        row_end=row_end,
        rows_final_dump=rows_final_dump,
        ccd_order=ccd_order,
        ccd_side=ccd_side,
        ci_width=ci_width,
        ci_gap=ci_gap,
        vgd=vgd,
    )

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)

    dpu_dev: DPUInterface = GlobalState.setup.camera.dpu.device

    # Go to -> STANDBY -> ON mode

    MODULE_LOGGER.info("Commanding N-FEE to STANDBY mode")
    dpu_dev.n_fee_set_standby_mode()
    wait_for_long_pulse()

    MODULE_LOGGER.info("Commanding N-FEE to ON mode")
    dpu_dev.n_fee_set_on_mode()
    wait_for_long_pulse()

    # The VGD config parameter shall be set when the N-FEE is in ON mode

    MODULE_LOGGER.info("Set V_GD and IG_HI register parameter")
    dpu_dev.n_fee_set_vgd({"ccd_vgd_config": dpu_pars['ccd_vgd_config']})  # preferably 15.0
    dpu_dev.n_fee_set_register_value('reg_20_config', 'ccd_ig_hi_config', 0xFFF)  # value from MSSL

    # Go to -> STANDBY mode

    MODULE_LOGGER.info("Commanding N-FEE to STANDBY mode")
    dpu_dev.n_fee_set_standby_mode()
    wait_for_long_pulse()

    # Now we can configure the N-FEE into charge injection mode

    MODULE_LOGGER.info("Configure N-FEE for charge injection")
    dpu_dev.n_fee_set_register_value('reg_0_config', 'v_start', dpu_pars['v_start'])
    dpu_dev.n_fee_set_register_value('reg_0_config', 'v_end', dpu_pars['v_end'])
    dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_width', dpu_pars['charge_injection_width'])
    dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_gap', dpu_pars['charge_injection_gap'])
    dpu_dev.n_fee_set_register_value('reg_2_config', 'ccd_readout_order', dpu_pars['ccd_readout_order'])
    dpu_dev.n_fee_set_register_value('reg_3_config', 'n_final_dump', dpu_pars['n_final_dump'])
    dpu_dev.n_fee_set_register_value('reg_3_config', 'charge_injection_en', 1)
    dpu_dev.n_fee_set_register_value('reg_5_config', 'sync_sel', 0)  # external sync
    dpu_dev.n_fee_set_register_value('reg_5_config', 'sensor_sel', sensor_sel.E_SIDE.value)
    dpu_dev.n_fee_set_register_value('reg_5_config', 'digitise_en', 1)
    dpu_dev.n_fee_set_register_value('reg_5_config', 'DG_en', 0)

    load_and_inspect_register_map()

    # Go to -> FULL_IMAGE mode

    MODULE_LOGGER.info("Set N-FEE in FULL_IMAGE mode.")
    MODULE_LOGGER.info("Image data for E-side")
    dpu_dev.n_fee_set_register_value('reg_21_config', 'ccd_mode_config', n_fee_mode.FULL_IMAGE_MODE)
    wait_for_long_pulse()

    wait_cycles(num_cycles)

    # Change to the F-side

    MODULE_LOGGER.info("Image data for F-side")
    dpu_dev.n_fee_set_register_value('reg_5_config', 'sensor_sel', sensor_sel.F_SIDE.value)

    wait_cycles(num_cycles)

    # Go back to -> STANDBY -> ON mode and reset the config

    MODULE_LOGGER.info("Commanding N-FEE to STANDBY mode")
    dpu_dev.n_fee_set_standby_mode()
    wait_for_long_pulse()

    MODULE_LOGGER.info("Commanding N-FEE to ON mode")
    dpu_dev.n_fee_set_on_mode()
    wait_for_long_pulse()

    MODULE_LOGGER.info("Reset the  N-FEE")
    dpu_dev.n_fee_reset()
    wait_for_long_pulse()

    reg_map = dpu_dev.n_fee_sync_register_map()
    MODULE_LOGGER.debug(reg_map)

    MODULE_LOGGER.info("Commanding N-FEE to STANDBY mode")
    dpu_dev.n_fee_set_standby_mode()
    wait_for_long_pulse()

    MODULE_LOGGER.info("Commanding N-FEE to DUMP mode")
    n_cam_to_dump_mode()

    # The following should have been done by the N-FEE reset above

    # dpu_dev.n_fee_set_vgd({"ccd_vgd_config": 19.90})
    # dpu_dev.n_fee_set_register_value('reg_20_config', 'ccd_ig_hi_config', 0)
    # dpu_dev.n_fee_set_register_value('reg_0_config', 'v_start', 0)
    # dpu_dev.n_fee_set_register_value('reg_0_config', 'v_end', 4509)
    # dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_width', 0)
    # dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_gap', 0)
    # dpu_dev.n_fee_set_register_value('reg_3_config', 'n_final_dump', 0)
    # dpu_dev.n_fee_set_register_value('reg_3_config', 'charge_injection_en', 0)
    # dpu_dev.n_fee_set_register_value('reg_5_config', 'sync_sel', 0)  # external sync
    # dpu_dev.n_fee_set_register_value('reg_5_config', 'sensor_sel', sensor_sel.BOTH_SIDES)
    # dpu_dev.n_fee_set_register_value('reg_5_config', 'digitise_en', 1)
    # dpu_dev.n_fee_set_register_value('reg_5_config', 'DG_en', 0)
    #
    # reg_map = dpu_dev.n_fee_sync_register_map()
    # MODULE_LOGGER.info(reg_map)


def n_cam_charge_injection_window(num_cycles=None, ccd_order=None, ccd_side=None, ci_width=None, ci_gap=None, vgd=None):
    """
    Charge injection in FEE windowing mode

    Args:
        num_cycles: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to STANDBY or DUMP mode again.
        ccd_order : list of 4 integers, e.g. [1,2,3,4]
        ccd_side  : sensor_sel.BOTH (or E, F, or ALT -- BOTH is standard in FEE "windowing mode")
        ci_width  : width of each charge-injection region, in number of rows
        ci_gap    : nb of rows between the charge-injection regions
        vgd       : V_GD voltage, driving charge-injection level
                    V_GD ~ 14 : FWC
                    V_GD = 15 ~ 70% FWC
                    V_GD = 16 ~ 50% FWC
                    V_GD = 17 ~ 30% FWC

    """

    setup = GlobalState.setup

    dpu = setup.camera.dpu.device

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["ccd_order"] = ccd_order
    n_fee_parameters["ccd_side"] = ccd_side     # TODO This still has to be converted!
    n_fee_parameters["ci_width"] = ci_width
    n_fee_parameters["ci_gap"] = ci_gap
    n_fee_parameters["vgd"] = vgd

    dpu.n_fee_set_charge_injection_windowing(n_fee_parameters)

    # When a finite number of images were requested (n>0), check if the acquisition
    # is over every "time_request_granularity" seconds,

    if num_cycles != 0:

        wait_until_num_cycles_is_zero()

        while not (n_cam_is_standby_mode() or n_cam_is_dump_mode()):
            time.sleep(setup.camera.fee.time_request_granularity)


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_to_standby_mode')
@building_block
def n_fee_to_standby_mode():
    return n_cam_to_standby_mode()


@building_block
def n_cam_to_standby_mode():
    """Set the N-FEE to STANDBY mode."""

    dpu = GlobalState.setup.camera.dpu.device
    dpu.n_fee_set_standby_mode()


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_is_standby_mode')
def n_fee_is_standby_mode() -> bool:
    return n_cam_is_standby_mode()


def n_cam_is_standby_mode():
    """
    Check if the N-FEE is in STANDBY mode.

    Returns:
        Boolean: True is N-FEE in standby mode, False otherwise.
    """

    dpu = GlobalState.setup.camera.dpu.device
    return dpu.n_fee_get_mode() == n_fee_mode.STAND_BY_MODE


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_to_on_mode')
@building_block
def n_fee_to_on_mode():
    return n_cam_to_on_mode()


@building_block
def n_cam_to_on_mode():
    """Set the N-FEE to ON mode."""

    dpu = GlobalState.setup.camera.dpu.device
    dpu.n_fee_set_on_mode()


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_is_on_mode')
def n_fee_is_on_mode() -> bool:
    return n_cam_is_on_mode()


def n_cam_is_on_mode():
    """
    Check if the N-FEE is in ON mode.

    Returns:
        Boolean: True is N-FEE in ON mode, False otherwise.
    """

    dpu = GlobalState.setup.camera.dpu.device
    return dpu.n_fee_get_mode() == n_fee_mode.ON_MODE


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_to_dump_mode')
@building_block
def n_fee_to_dump_mode():
    return n_cam_to_dump_mode()


@building_block
def n_cam_to_dump_mode():
    """
    Set the n_fee to DUMP mode in external sync. This mode is hard code for consistency. The arguments are:
    row_start = row_end = 0, rows_final_dump = 4510, ccd_order = [1,2,3,4], and ccd_side = 'BOTH'.

    DUMP mode means cycling over the 4 CCDs, with the dump_gate high during readout, i.e. a
    normal readout process, without digitization.
    """

    dpu: DPUInterface = GlobalState.setup.camera.dpu.device

    n_fee_parameters = dict(
        row_start=0,
        row_end=0,
        rows_final_dump=4510,
        ccd_side='BOTH',
        ccd_order=[1, 2, 3, 4],
    )

    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    dpu.n_fee_set_dump_mode(dpu_pars)


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_to_dump_mode_int_sync')
@building_block
def n_fee_to_dump_mode_int_sync():
    return n_cam_to_dump_mode_int_sync()


@building_block
def n_cam_to_dump_mode_int_sync():
    """
    Set the n_fee to DUMP mode and internal sync. This mode is hard code for consistency. The arguments are:
    row_start = row_end = 0, rows_final_dump = 4510, ccd_order = [1,2,3,4], ccd_side = 'BOTH', and cycle_time = 0.6.

    DUMP mode means cycling over the 4 CCDs, with the dump_gate high during readout, i.e.
    a normal readout process, without digitization.

    Note that the cycle time does NOT include the 400ms of the synchronisation pulse.
    """

    dpu = GlobalState.setup.camera.dpu.device

    n_fee_parameters = dict(
        row_start=0,
        row_end=0,
        rows_final_dump=4510,
        ccd_order=[1, 2, 3, 4],
        ccd_side='BOTH',
        cycle_time=0.6,
    )
    dpu_pars = _convert_n_fee_parameters(n_fee_parameters)
    dpu.n_fee_set_dump_mode_int_sync(dpu_pars)


@deprecate(reason='of naming consistency with other camtest commanding',
           alternative='n_cam_is_dump_mode')
def n_fee_is_dump_mode() -> bool:
    return n_cam_is_dump_mode()


def n_cam_is_dump_mode() -> bool:
    """
    Check if the N-FEE is in ON mode.

    Returns:
        Boolean: True is N-FEE in DUMP mode, False otherwise.
    """

    dpu: DPUInterface = GlobalState.setup.camera.dpu.device
    return bool(dpu.n_fee_is_dump_mode())


def n_cam_is_int_sync() -> bool:
    """
    Check if the N-FEE is in internal sync mode.

    Returns:
        Boolean: True is N-FEE in internal sync mode, False otherwise.
    """

    dpu: DPUInterface = GlobalState.setup.camera.dpu.device
    return dpu.n_fee_get_sync_mode() == fee_sync_mode.INTERNAL


def n_cam_is_ext_sync() -> bool:
    """
    Check if the N-FEE is in external sync mode.

    Returns:
        Boolean: True is N-FEE in external sync mode, False otherwise.
    """

    dpu: DPUInterface = GlobalState.setup.camera.dpu.device
    return dpu.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL


@building_block
def set_slicing(num_cycles=None):
    """ Set the slicing parameter for the FITS generation.

    Args:
        - num_cycles: Maximum number of cycles to include in a single FITS cube.
    """

    dpu = GlobalState.setup.camera.dpu.device
    dpu.set_slicing(num_cycles=num_cycles)


def get_slicing() -> int:
    """ Return the slicing parameter for hte FITS generation.

    Returns: Maximum number of cycles to include in a single FITS cube.
    """

    dpu = GlobalState.setup.camera.dpu.device
    return dpu.get_slicing()


@building_block
def n_fee_set_clear_error_flags():
    """ Command the N-FEE to clear all error flags for non RMAP/SpW related functions immediately

    The `clear_error_flag` bit in the register map is set to 1, meaning that all error flags that are generated by
    the N-FEE FPGA for non RMAP-SpW related functions are cleared immediately.  This bit is cleared automatically,
    so that any future error flags can be latched again.  If the error conditions persist and no corrective measures
    are taken, then error flags would be set again."""

    dpu: DPUInterface = GlobalState.setup.camera.dpu.device
    dpu.n_fee_set_clear_error_flags()


@building_block
def n_fee_set_fpga_defaults():
    """ Set the FPGA default values in the N-FEE register map.

    A table is printed out, showing the values that have changed.
    """

    with GlobalState.setup.camera.dpu.device as dpu:
        register_map_before: RegisterMap = dpu.n_fee_sync_register_map()
        dpu.n_fee_set_fpga_defaults()
        register_map_after: RegisterMap = dpu.n_fee_sync_register_map()

    # Print the difference (in a table) between before and after

    difference = DeepDiff(register_map_before.as_dict(), register_map_after.as_dict())

    dataset = []

    for names, values in difference["values_changed"].items():
        split_names = names[5:-1].split('][')
        item = (split_names[0].strip("'"), split_names[1].strip("'"),
                str(values["old_value"]), str(values["new_value"]))
        dataset.append(item)

    # Sort by register entry and inside each, by sub-register entry (alphabetically)

    dataset.sort(key=lambda a: a[1])
    dataset.sort(key=lambda a: int(a[0].split("_")[1]))

    table = Table(title="N-FEE FPGA defaults")
    table.add_column("Register")
    table.add_column("Sub-register")
    table.add_column("Old value", justify="right")
    table.add_column("New value", justify="right")

    for item in dataset:
        table.add_row(*item)

    console = Console(width=120)
    console.print(table)

    # Check whether the N-FEE FPGA defaults were changed correctly

    default_values = GlobalState.setup.camera.fee.fpga_defaults
    fpga_changed_correctly = True

    for reg_name in default_values:
        hex_string = str(default_values[reg_name])
        byte_string = int(hex_string, 16).to_bytes(length=4, byteorder='big', signed=False)

        new_entry = register_map_after.get_register_data(reg_name)

        if byte_string != new_entry:
            fpga_changed_correctly = False
            print(f"N-FEE defaults incorrect for {reg_name}: is {new_entry} but should have been {byte_string}")

    if fpga_changed_correctly:
        print("The changes in N-FEE FPGA parameters were applied correctly.")


def n_cam_readout_times(row_start=None, row_end=None, rows_final_dump=None):
    """ Computes the durations of the different readout phases.

    Args:
        row_start: starting row for the readout (zero-based)
        row_end: ending row for the readout (zero-based)
        rows_final_dump: number of rows for the clearout after the readout

    Returns:
        A tuple with the following timing values.

        * time_initial_dump: dump all rows "below" row_start
        * time_actual_readout: duration of the actual readout, i.e. full frame or region of
            interest in case of partial readout
        * time_final_dump: dump 'rows_final_dump' rows after the actual readout
    """

    setup = GlobalState.setup

    # CALIBRATION VALUES

    # Transfer time 1 row in parallel direction
    time_row_shift = setup.camera.fee.time_row_parallel  # 110.e-6

    # Transfer time 1 row during clearout
    time_row_clearout = setup.camera.fee.time_row_clearout  # 90.e-6

    # At 3 MHz = 333 ns, rounded to 20 ns (50 MHz master clock) = 340 ns
    time_pixel_readout = setup.camera.fee.time_pixel_readout  # 340.e-9

    # Nb of rows in the parallel overscan
    #n_parallel_overscan = setup.camera.fee.n_parallel_overscan

    # Nb of pixels in the serial prescan
    n_serial_prescan = setup.camera.fee.n_serial_prescan

    # Nb of pixels in the serial overscan
    n_serial_overscan = setup.camera.fee.n_serial_overscan

    # Mb of columns to read in every row (col 0 to col col_end)
    col_end = setup.camera.fee.col_end

    # REGION OF INTEREST

    # Number of pixels in every (half) row
    # col_end = 2254
    n_half_cols = col_end + n_serial_prescan
    #if col_end == GlobalState.setup.camera.fee.col_end:
    n_half_cols += n_serial_overscan

    # Time to shift and read a single row
    time_half_col = time_row_shift + n_half_cols * time_pixel_readout

    # readout time of the region of interest
    n_rows_partial = row_end - row_start
    time_actual_readout = n_rows_partial * time_half_col

    # PARALLEL OVERSCAN
    # In partial readout, the parallel overscan is indirectly defined through row_end --> no special handling here
    #time_actual_readout += n_parallel_overscan * time_half_col

    # INITIAL AND FINAL dump

    # Time necessary for initial dump of lines 'under' row_start
    time_initial_dump = row_start * time_row_clearout

    # Time necessary for the final dump
    time_final_dump = rows_final_dump * time_row_clearout

    return time_initial_dump, time_actual_readout, time_final_dump


def n_cam_tsync_to_texp(sync_time=None, row_start=None, row_end=None,
                       rows_final_dump=None):
    """
    Calculate the exposure time from the sync time of the FEE & the full-image mode parameters

    Args:
        sync_time: Internal sync time of the FEE time.
        row_start: starting row for the readout (zero-based)
        row_end: ending row for the readout (zero-based)
        col_end: number of pixels in the serial readout (pre-scan + readout + serial overscan)
        rows_final_dump: number of rows for the clearout after the readout

    Returns:
        The exposure time.
    """


    time_initial_dump, time_actual_readout, time_final_dump = \
        n_cam_readout_times(row_start, row_end, rows_final_dump)

    # exposure time is "what's left of the 'sync-pulse-period' after all the 'duties' (transfers and readout)
    # have been done

    exp_time = sync_time - time_initial_dump - time_actual_readout - time_final_dump

    return exp_time


def n_cam_texp_to_tsync(exposure_time=None, row_start=None, row_end=None,
                       rows_final_dump=None):
    """
    Calculate the sync time of the FEE from the exposure time.

    Args:
        row_start: starting row for the readout (zero-based)
        row_end: ending row for the readout (zero-based)
        rows_final_dump: number of rows for the clearout after the readout
        exposure_time: Exposure time [seconds] : float

    Returns:
        the period for the internal sync pulse in seconds.
    """

    exposure_time = float(exposure_time)

    time_initial_dump, time_actual_readout, time_final_dump = \
        n_cam_readout_times(row_start, row_end, rows_final_dump)

    # INTERNAL SYNC PULSE PERIOD

    # The sync period contains the exposure time and all the 'readout duties' (transfers and readout)
    sync_time = exposure_time + time_initial_dump + time_actual_readout + time_final_dump

    return sync_time


def _convert_n_fee_parameters(n_fee_parameters: dict) -> dict:
    """
    Internal function to map the camtest.commanding parameters of a building_block to the expected
    parameter set for dpu commanding. The function translates the keys, converts the values for
    certain keys, and removes unknown key:value pairs.

    TODO:
        * remove unknown key:value pairs
        * accept other values for ccd_side, i.e. 'ALT', String of 4 or 8 characters e.g. 'EFEF',
          Tuple[4 or 8 sides]
        * How do I convert clock_dir_serial ? Is this converted into just one register value or
          are there several that need to be set depending on 'FWD' or 'REV'?

    Args:
        n_fee_parameters (dict): dictionary of parameters as passed into a camtest.commanding
            building_block.

    Returns:
        a new dictionary with converted key:values pairs.
    """

    def conv_ccd_side(value):
        sensor_sel = GlobalState.setup.camera.fee.sensor_sel.enum

        if isinstance(value, (tuple, list)) or value.upper() == 'ALT':
            # a ccd_sides key will be created separately in the special cases
            return sensor_sel.RESERVED.value
        elif value.upper() == 'BOTH':
            return sensor_sel.BOTH_SIDES.value
        elif value.upper() == 'F':
            return sensor_sel.F_SIDE.value
        elif value.upper() == 'E':
            return sensor_sel.E_SIDE.value
        elif isinstance(value, str) and len(value) in (4, 8):
            # a ccd_sides key will be created separately in the special cases
            return sensor_sel.RESERVED.value
        else:
            raise Abort(f"Incorrect ccd_side parameter content: ccd_side={value}")

    def conv_ccd_order(value: List):
        if isinstance(value, (list, tuple)):
            order = convert_ccd_order_list(value)
        elif isinstance(value, int):
            order = value
        else:
            raise ValueError("The CCD readout order should be specified as a list or an integer")
        return order

    def conv_cycle_time(value: float):
        return int(value * 1000)

    def conv_rev_clock(value: str):
        return 1 if value == "REV" else 0

    conv_key = {
        "row_start": "v_start",
        "row_end": "v_end",
        "ccd_side": "sensor_sel",
        "ccd_order": "ccd_readout_order",
        "rows_final_dump": "n_final_dump",
        "cycle_time": "int_sync_period",
        "ci_width": "charge_injection_width",
        "ci_gap": "charge_injection_gap",
        "clock_dir_serial": "reg_clk_dir",
        "clock_dir_parallel": "img_clk_dir",
        "vgd": "ccd_vgd_config",
    }

    conv_value = {
        "row_start": int,
        "row_end": int,
        "rows_final_dump": int,
        "ccd_side": conv_ccd_side,
        "ccd_order": conv_ccd_order,
        "cycle_time": conv_cycle_time,
        "clock_dir_serial": conv_rev_clock,
        "clock_dir_parallel": conv_rev_clock,
        "vgd": float,
    }

    def new_key(key):
        return conv_key.get(key, key)

    def new_value(key, value):
        try:
            return conv_value[key](value)
        except KeyError:
            return value

    dpu_pars = {}

    for k, v in n_fee_parameters.items():
        dpu_pars[new_key(k)] = new_value(k, v)

        # Handle special cases

        if k == "ccd_side":
            if v == 'ALT':
                dpu_pars["ccd_sides"] = ('E', 'E', 'E', 'E', 'F', 'F', 'F', 'F')
            elif v in ('E', 'F', 'BOTH'):
                pass  # this is handled in the conv_ccd_side() function
            elif isinstance(v, (tuple, list)):
                if len(v) not in (4, 8):
                    raise Abort(
                        f"The ccd_side parameter shall contain 4 or 8 characters, not {len(v)}. "
                        f"The given input is incorrect: {v}.")
                dpu_pars["ccd_sides"] = tuple(v)
            elif isinstance(v, str):
                if len(v) not in (4, 8):
                    raise Abort(
                        f"The ccd_side parameter shall contain 4 or 8 characters, not {len(v)}. "
                        f"The given input is incorrect: {v}.")
                dpu_pars["ccd_sides"] = tuple(x for x in v)

    try:
        dpu_pars.setdefault("ccd_readout_order", GlobalState.setup.camera.fee.ccd_numbering.DEFAULT_CCD_READOUT_ORDER)
    except AttributeError:
        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.DEFAULT_CCD_READOUT_ORDER")
    return dpu_pars


def wait_cycles(num_cycles: int):
    """Wait until num_cycles have passed, then return."""
    with DPUMonitoring() as moni:
        return moni.wait_num_cycles(num_cycles)


def wait_until_num_cycles_is_zero():
    """Wait until the num_cycles maintained by the DPU Processor is zero, then return."""
    with DPUMonitoring() as moni:
        moni.wait_until_synced_num_cycles_is_zero()


def wait_for_timecode() -> Tuple[int, str]:
    """Wait until a timecode is received from the DPU Processor."""
    with DPUMonitoring() as moni:
        return moni.wait_for_timecode()


def wait_for_long_pulse():
    """Wait until the start of the next readout cycle."""
    with DPUMonitoring() as moni:
        return moni.on_long_pulse_do(lambda: True)


def on_frame_number_do(frame_number: int, func: Callable, *args, **kwargs):
    """
    This function allows to synchronise the execution of the given function to the given
    frame number that is sent out by the N-FEE. Time synchronisation is accurate within 100ms.

    Args:
        frame_number: the frame number on which the function execution shall be synchronised - [0, 1, 2, 3]
        func (Callable): the function to synchronise to the timecode
        *args: any arguments to pass to the function
        **kwargs: any keyword arguments to pass to the function

    Returns:
        The return value of the called function.

    Raises:
        A TimeoutError when no sync data was received from the monitoring socket after 30s.
    """
    with DPUMonitoring() as moni:
        return moni.on_frame_number_do(frame_number, func, *args, **kwargs)


def on_long_pulse_do(func: Callable, *args, **kwargs):
    """
    This function allows to synchronise the execution the given function to the timecode
    that is send out by the N-FEE. Time synchronisation is accurate within 100ms.

    Args:
        func (Callable): the function to synchronise to the timecode
        *args: any arguments to pass to the function
        **kwargs: any keyword arguments to pass to the function

    Returns:
        The return value of the called function.

    Raises:
        A TimeoutError when no sync data was received from the monitoring socket after 30s.
    """
    with DPUMonitoring() as moni:
        return moni.on_long_pulse_do(func, *args, **kwargs)


if __name__ == "__main__":
    import rich

    n_fee_pars = dict(
        num_cycles=0,
        row_start=0,
        row_end=9,
        rows_final_dump=0,
        ccd_order=[1, 1, 1, 1],
        ccd_side='E',
    )

    rich.print(_convert_n_fee_parameters(n_fee_pars))

    try:
        n_fee_pars["ci_width"] = 50
        n_fee_pars["ci_gap"] = 100
        rich.print(_convert_n_fee_parameters(n_fee_pars))
    except Abort as exc:
        print(exc)

    try:
        n_fee_pars["clock_dir_serial"] = "REV"
        n_fee_pars["clock_dir_parallel"] = "REV"
        rich.print(_convert_n_fee_parameters(n_fee_pars))
    except Abort as exc:
        print(exc)

    n_fee_pars["ccd_side"] = 'BOTH'
    n_fee_pars["ccd_order"] = [1, 2, 3, 4]

    rich.print(_convert_n_fee_parameters(n_fee_pars))

    n_fee_pars["ccd_side"] = 'ALT'
    n_fee_pars["ccd_order"] = [1, 3, 1, 3]

    rich.print(_convert_n_fee_parameters(n_fee_pars))

    n_fee_pars["ccd_side"] = ('E', 'F', 'E', 'F')
    n_fee_pars["ccd_order"] = [1, 1, 1, 1]

    rich.print(_convert_n_fee_parameters(n_fee_pars))

    n_fee_pars["ccd_side"] = 'FFEE'
    rich.print(_convert_n_fee_parameters(n_fee_pars))

    n_fee_pars["ccd_side"] = 'EEEEFFFF'
    rich.print(_convert_n_fee_parameters(n_fee_pars))

    try:
        n_fee_pars["ccd_side"] = 'EFEFEF'
        rich.print(_convert_n_fee_parameters(n_fee_pars))
    except Abort as exc:
        print(exc)

    try:
        n_fee_pars["ccd_side"] = ('E', 'F')
        rich.print(_convert_n_fee_parameters(n_fee_pars))
    except Abort as exc:
        print(exc)

    n_fee_pars = dict(
         num_cycles=20,
         row_start=0,
         row_end=4539,
         rows_final_dump=0,
         ccd_order=[1, 2, 3, 4],
         ccd_side='BOTH',
         ci_width=4509,
         ci_gap=0,
         vgd=15)

    try:
        rich.print(_convert_n_fee_parameters(n_fee_pars))
    except Abort as exc:
        print(exc)
