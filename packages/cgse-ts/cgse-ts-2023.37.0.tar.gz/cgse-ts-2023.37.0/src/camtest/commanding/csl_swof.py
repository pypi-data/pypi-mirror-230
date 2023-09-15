"""
CSL SWITCH OFF PROCEDURE

SWITCH OFF  AEU, DPU, OGSE LAMP,  TM ACQUISITION, FITS GENERATION & VARIOUS GUIs

"""

from camtest import execute
################
# AEU SWOFF
################
from camtest.commanding import aeu, ogse

execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)


################
# OGSE SWOFF
################

execute(ogse.ogse_swoff)


################
# SWOFF DPU, FITS-GEN & TM ACQUISITION
################

# In the terminals on the server where these have been launched: Ctrl-C will stop the following
# Stop    DPU CS
# Stop    FITS generator
# Stop    python -m egse.fee.n_fee_hk -platform offscreen


