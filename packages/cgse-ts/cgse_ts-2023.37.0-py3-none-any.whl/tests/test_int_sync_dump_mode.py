import sys

import time

from egse.dpu import DPUInterface
from egse.dpu.dpu_cs import is_dpu_cs_active
from egse.fee import n_fee_mode
from egse.setup import load_setup

setup = load_setup()

dpu: DPUInterface = setup.camera.dpu.device

if not is_dpu_cs_active():
    print("DPU Control Server is not active or can not be found.")
    sys.exit()

mode: n_fee_mode =  dpu.n_fee_get_mode()
sync_sel = dpu.n_fee_get_sync_mode()
print(f"mode = {n_fee_mode(mode).name}, {'internal' if sync_sel else 'external'} sync")

if mode != n_fee_mode.ON_MODE:
    print("N-FEE shall be in ON mode")
    sys.exit()

if sync_sel:
    print("N-FEE shall be in external sync")
    sys.exit()

response = dpu.n_fee_set_standby_mode()
print(f"{response = }")

while dpu.n_fee_get_mode() != n_fee_mode.STAND_BY_MODE:
    time.sleep(0.5)

mode: n_fee_mode =  dpu.n_fee_get_mode()
sync_sel = dpu.n_fee_get_sync_mode()
print(f"mode = {n_fee_mode(mode).name}, {'internal' if sync_sel else 'external'} sync")

response = dpu.n_fee_set_dump_mode_int_sync({})
print(f"{response = }")

while not dpu.n_fee_is_dump_mode():
    time.sleep(0.5)

mode: n_fee_mode =  dpu.n_fee_get_mode()
sync_sel = dpu.n_fee_get_sync_mode()
print(f"mode = {n_fee_mode(mode).name}, {'internal' if sync_sel else 'external'} sync")

response = dpu.n_fee_set_external_sync({})
print(f"{response = }")

response = dpu.n_fee_set_standby_mode()
print(f"{response = }")

while dpu.n_fee_get_mode() != n_fee_mode.STAND_BY_MODE:
    time.sleep(0.5)

mode: n_fee_mode =  dpu.n_fee_get_mode()
sync_sel = dpu.n_fee_get_sync_mode()
print(f"mode = {n_fee_mode(mode).name}, {'internal' if sync_sel else 'external'} sync")

response = dpu.n_fee_set_on_mode()
print(f"{response = }")

while dpu.n_fee_get_mode() != n_fee_mode.ON_MODE:
    time.sleep(0.5)

mode: n_fee_mode =  dpu.n_fee_get_mode()
sync_sel = dpu.n_fee_get_sync_mode()
print(f"mode = {n_fee_mode(mode).name}, {'internal' if sync_sel else 'external'} sync")
