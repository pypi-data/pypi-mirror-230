from typing import Tuple

from rich import pretty
from rich import print

from camtest import camtest_logger
from camtest import end_observation
from camtest import start_observation
from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.fee import n_fee_mode
from egse.setup import load_setup

pretty.install()


def wait_for_timecode() -> Tuple[int, str]:
    """Wait until a timecode is received from the DPU Processor."""
    with DPUMonitoring() as moni:
        return moni.wait_for_timecode()


def wait_for_long_pulse():
    """Wait until the start of the next readout cycle."""
    with DPUMonitoring() as moni:
        moni.on_long_pulse_do(lambda: True)


def wait_num_cycles(num_cycles: int):
    """Wait until num_cycles have passed, then return."""
    with DPUMonitoring() as moni:
        moni.wait_num_cycles(num_cycles)


def wait_for_num_cycles_is_zero():
    with DPUMonitoring() as moni:
        moni.wait_until_synced_num_cycles_is_zero()


def true_or_false(value):
    return "True" if value else "False"


def load_and_inspect_register_map():
    tf = true_or_false  # shortcut

    reg_map = dpu_dev.n_fee_sync_register_map()

    vgd_19 = reg_map[('reg_19_config', 'ccd_vgd_config')]
    vgd_20 = reg_map[('reg_20_config', 'ccd_vgd_config')]
    vgd = (vgd_20 << 4) + vgd_19

    camtest_logger.info(
        f"Register map:\n"
        f"N-FEE mode = {n_fee_mode(reg_map['ccd_mode_config']).name}\n"
        f"CI width   = {reg_map['charge_injection_width']}\n"
        f"CI gap     = {reg_map['charge_injection_gap']}\n"
        f"CI enabled = {tf(reg_map['charge_injection_en'])}\n"
        f"V-GD       = 0x{vgd:X} -> {vgd/1000*5.983:.2f}\n"
        f"digitise   = {tf(reg_map['digitise_en'])}\n"
        f"DG         = {tf(reg_map['DG_en'])}\n"
    )


def load_and_print_full_register_map():
    reg_map = dpu_dev.n_fee_sync_register_map()
    camtest_logger.info(reg_map)


setup = load_setup()
print(f"Setup ID: {setup.get_id()}")

dpu_dev: DPUProxy = setup.camera.dpu.device
print(f"DPU Proxy: {dpu_dev.is_cs_connected() if dpu_dev else False}")

start_observation(f"Test Charge Injection: direct DPU commanding")
camtest_logger.info("Starting Test Charge Injection")

load_and_inspect_register_map()

camtest_logger.info("Commanding N-FEE to STANDBY mode")
dpu_dev.n_fee_set_standby_mode()
wait_for_long_pulse()
camtest_logger.info(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

camtest_logger.info("Commanding N-FEE to ON mode")
dpu_dev.n_fee_set_on_mode()
wait_for_long_pulse()
camtest_logger.info(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

camtest_logger.info("Set V_GD register parameter")
dpu_dev.n_fee_set_vgd({"ccd_vgd_config": 15.0})

load_and_inspect_register_map()

camtest_logger.info("Commanding N-FEE to STANDBY mode")
dpu_dev.n_fee_set_standby_mode()
wait_for_long_pulse()
camtest_logger.info(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

load_and_inspect_register_map()

camtest_logger.info("Set the V_GD and other pars for charge injection.")
dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_width', 100)
dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_gap', 200)
dpu_dev.n_fee_set_register_value('reg_3_config', 'charge_injection_en', 1)
dpu_dev.n_fee_set_register_value('reg_5_config', 'digitise_en', 1)
dpu_dev.n_fee_set_register_value('reg_5_config', 'DG_en', 0)

load_and_inspect_register_map()

camtest_logger.info("Set N-0FEE in FULL_IMAGE mode.")
dpu_dev.n_fee_set_register_value('reg_21_config', 'ccd_mode_config', n_fee_mode.FULL_IMAGE_MODE)
wait_for_long_pulse()
print(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

wait_num_cycles(5)

camtest_logger.info("Commanding N-FEE to STANDBY mode")
dpu_dev.n_fee_set_standby_mode()
wait_for_long_pulse()
print(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

camtest_logger.info("Commanding N-FEE to ON mode")
dpu_dev.n_fee_set_on_mode()
wait_for_long_pulse()
print(f"N-FEE mode = {n_fee_mode(dpu_dev.n_fee_get_mode()).name}")

camtest_logger.info("Reset V_GD and other pars to their default value.")
dpu_dev.n_fee_set_vgd({"ccd_vgd_config": 19.90})
dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_width', 0)
dpu_dev.n_fee_set_register_value('reg_1_config', 'charge_injection_gap', 0)
dpu_dev.n_fee_set_register_value('reg_3_config', 'charge_injection_en', 0)
dpu_dev.n_fee_set_register_value('reg_5_config', 'digitise_en', 1)
dpu_dev.n_fee_set_register_value('reg_5_config', 'DG_en', 0)
load_and_inspect_register_map()

end_observation()
