import os
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib import cm
from astropy.io import ascii
from astropy.table import Table
import camtest.analysis.convenience as cv

from camtest import load_setup, list_setups

global NaN,orange,gray,lightgray,lightgreen,lightblue
NaN = float('nan')
orange = (1.,0.75,0.)
gray   = (0.5,0.5,0.5)
pink = (1.,0.5,0.75)
brown = (0.7,0.6,0.2)
lightgray=(0.75,0.75,0.75)
lightgreen=(0.5,1,0.5)
lightblue=(0.5,0.5,1.0)
lightpink=(1.,0.75,0.9)
lightorange=(1.,0.9,0.5)
verylightblue=(0.75,0.75,1.0)
verylightgreen=(0.75,1.0,0.75)
verylightgray=(0.9,0.9,0.9)

colors = ['k','r','b','g',orange,'c','m',gray,lightgray,lightgreen,pink]

def ccd_positions(ccd_corners, verbose=True):
    """
    INPUT
    ccd_corners = focal plane coordinates (mm) of the ccd corner pixels
                  These pixels are assumed to be ordered according to
                  the EM FPA EIDP : BL, TL, TR, BR (wrt the CCD ref. frame as defined in the commanding manual)

    verbose : prints info when true

    Example input, (EM FPA), from
    PTO-E2V-FPA-DP-00000001v2_PLATO\ FPA\ EM01\ EIDP_CCD_pixel_corner_coordinates.pdf  Annex M, table starting on pg 3
    # Corner Pixel FOCAL PLANE COORDINATES (mm)
    #               Bottom Left (0,0)         TL               TR                  BR
    cornerfpc= {}
    cornerfpc[4] = [[ 81.854,  0.958], [ 0.342, 0.951], [  0.336, 82.113], [ 81.498, 82.120]]
    cornerfpc[3] = [[  0.991,-81.516], [ 0.987,-0.354], [ 82.150, -0.350], [ 82.153,-81.512]]
    cornerfpc[2] = [[-81.483, -0.991], [-0.321,-0.987], [ -0.317,-82.149], [-81.479,-82.153]]
    cornerfpc[1] = [[ -0.964, 81.465], [-0.963, 0.303], [-82.125,  0.302], [-82.126, 81.464]]

    OUTPUT
    ccd_orientation : as defined in the setup
                      ccd_orientation ~ [180, 270, 0, 90]
    EM :
     origin_offset_x [-0.964, -0.991, -0.991, -0.958]
     origin_offset_y [81.465, 81.483, 81.516, 81.854]
     orientation
     1: 180.00070594341577,
     2: 270.0028237736609,
     3: 0.0026472791094462877,
     4: 90.06635297352653}

    """
    cornerfpc = ccd_corners
    hcorners = ["Y-left  ", "X-top   ", "Y-right ", "X-bottom"]
    ccdsideangles = {}
    ccdxyangles = {}
    ccdxybaselineangles = {1: 180, 2: 270, 3: 0, 4: 90}
    ccd_orientation = {}
    for ccd in [1, 2, 3, 4]:
        if verbose: print()
        angs = [0, 0, 0, 0]
        for i in range(4):
            a = cornerfpc[ccd][i]
            b = cornerfpc[ccd][(i + 1) % 4]
            try:
                ang = np.rad2deg(np.arctan((b[1] - a[1]) / (b[0] - a[0])))
            except:
                print(f"WARNING: {ccd=} Division by {(b[0] - a[0])=}")
                print(f"          --> angle fixed to 90 deg")
                print(f"          PLEASE CHECK CONSISTENCY OF FINAL RESULT")
                ang = 90.
            angs[i] = ang
            if verbose: print(f"{ccd=} {hcorners[i]} ang={np.round(ang, 4):9.4f}")
        ccdsideangles[ccd] = angs
        ccdxyangles[ccd] = [(angs[1] + angs[3]) / 2., (angs[0] + angs[2]) / 2.]

        # Bring "vertical" axes to positive values (for the 90 deg correction between x & y to deliver smth close to 0)
        if ccd in [2, 4]:
            ccdxyangles[ccd][0] = ccdxyangles[ccd][0] if (ccdxyangles[ccd][0] >= 0) else (ccdxyangles[ccd][0] + 180.)
        elif ccd in [1, 3]:
            ccdxyangles[ccd][1] = ccdxyangles[ccd][1] if (ccdxyangles[ccd][1] >= 0) else (ccdxyangles[ccd][1] + 180.)

        if verbose: print(
            f"{ccd=}  X-axis : {np.round(ccdxyangles[ccd][0], 4)}  Y-axis : {np.round(ccdxyangles[ccd][1], 4)}")

        ccd_orientation[ccd] = np.round(((ccdxyangles[ccd][0] + ccdxyangles[ccd][1] - 90.) / 2. + ccdxybaselineangles[ccd]), 4)
        if verbose: print(f"{ccd=} orientation: {np.round(ccd_orientation[ccd], 4)}")

    origin_offset_x = [cornerfpc[1][0][0], cornerfpc[2][0][1], -cornerfpc[3][0][0], -cornerfpc[4][0][1]]
    origin_offset_y = [cornerfpc[1][0][1], -cornerfpc[2][0][0], -cornerfpc[3][0][1], cornerfpc[4][0][0]]

    if verbose:
        print()
        print(f"setup.camera.ccd.{origin_offset_x=}")
        print(f"setup.camera.ccd.{origin_offset_y=}")
        print(f"setup.camera.ccd.orientation={[ccd_orientation[i] for i in range(1,5)]}")

    return origin_offset_x, origin_offset_y, ccd_orientation


###########################################
### FPA EIDP
###########################################

###
### EM
###
# PTO-E2V-FPA-DP-00000001v2_PLATO\ FPA\ EM01\ EIDP_CCD_pixel_corner_coordinates.pdf  Annex M, table starting on pg 3
# Corner Pixel FOCAL PLANE COORDINATES (mm)
#                    BL (0,0)          TL              TR                BR
cornerpixs = [[0, 0], [4509, 0], [4509, 4509], [0, 4509]]
cornerfpc = {}
cornerfpc[4] = [[81.504, 0.958], [0.342, 0.951], [0.336, 82.113], [81.498, 82.120]]
cornerfpc[3] = [[0.991, -81.516], [0.987, -0.354], [82.150, -0.350], [82.153, -81.512]]
cornerfpc[2] = [[-81.483, -0.991], [-0.321, -0.987], [-0.317, -82.149], [-81.479, -82.153]]
cornerfpc[1] = [[-0.964, 81.465], [-0.963, 0.303], [-82.125, 0.302], [-82.126, 81.464]]

###
### ACHEL - PFM
###
# PLATO-KUL-PL-DN_0003_Achel_FPA_PTO-EST-PL-RP-4370_iss1[3].pdf
# Corner Pixel FOCAL PLANE COORDINATES (mm)
#                    BL (0,0)          TL              TR                BR
cornerpixs = [[0, 0], [4509, 0], [4509, 4509], [0, 4509]]
cornerfpc = {}
cornerfpc[4] = [[81.5092, 0.9923], [0.3472, 0.9826], [0.3375, 82.1446], [81.4995, 82.1543]]
cornerfpc[3] = [[0.9892, -81.5027], [0.9714, -0.3407], [82.1334, -0.3229], [82.1512, -81.4849]]
cornerfpc[2] = [[-81.4973, -0.9893], [-0.3353, -0.9757], [-0.3216, -82.1377], [-81.4836, -82.1514]]
cornerfpc[1] = [[-0.9834, 81.4956], [-0.9835, 0.3336], [-82.1454, 0.3336], [-82.1454, 81.4956]]

origin_offset_x, origin_offset_y, ccd_orientation = ccd_positions(ccd_corners=cornerfpc, verbose=True)


###
### BRIGAND - FM01
###
# FPA_brigand PTO-EST-PL-RP-4371_FPA v01 (PLATO CAM FM1 - FPA & TOU Metrology Summary)
# Corner Pixel FOCAL PLANE COORDINATES (mm)


cornerpixs = [[0, 0], [4509, 0], [4509, 4509], [0, 4509]]
cornerfpc = {}
cornerfpc[4] = [[81.5066, 0.9927], [0.3446, 0.9983], [0.3502, 82.1603], [81.5122, 82.1547]]
cornerfpc[3] = [[1.0137, -81.5514], [1.0204, -0.3894], [82.1824, -0.3961], [82.1757, -81.5581]]
cornerfpc[2] = [[-81.5192, -0.9695], [-0.3572, -0.9971], [-0.3848, -82.1591], [-81.5468, -82.1315]]
cornerfpc[1] = [[-1.0079, 81.5502], [-1.0079, 0.3882], [-82.1699, 0.3882], [-82.1699, 81.5502]]

origin_offset_x, origin_offset_y, ccd_orientation = ccd_positions(ccd_corners=cornerfpc, verbose=True)



###
### CHIMAY - FM02
###
# FPA_chimay PTO-EST-PL-RP-4371_FPA v01 (PLATO CAM FM2 - FPA & TOU Metrology Summary)
# Corner Pixel FOCAL PLANE COORDINATES (mm)


cornerpixs = [[0, 0], [4509, 0], [4509, 4509], [0, 4509]]
cornerfpc = {}
cornerfpc[4] = [[81.4984, 0.9831], [0.3364, 0.9737], [0.3270, 82.1357], [81.4890, 82.1451]]
cornerfpc[3] = [[0.9805, -81.4944], [0.9799, -0.3324], [82.1419, -0.3318], [82.1425, -81.4938]]
cornerfpc[2] = [[-81.4954, -0.9883], [-0.3334, -0.9764], [-0.3215, -82.1384], [-81.4835, -82.1503]]
cornerfpc[1] = [[-0.9829, 81.4969], [-0.9829, 0.3349], [-82.1449, 0.3349], [-82.1449, 81.4969]]

origin_offset_x, origin_offset_y, ccd_orientation = ccd_positions(ccd_corners=cornerfpc, verbose=True)


###
### DUVEL - FM03
###
# FPA_duvel PTO-EST-PL-RP-1471_FPA v01 (PLATO CAM FM3 - FPA & TOU Metrology Summary)
# Corner Pixel FOCAL PLANE COORDINATES (mm)


cornerpixs = [[0, 0], [4509, 0], [4509, 4509], [0, 4509]]
cornerfpc = {}
cornerfpc[1] = [[-0.9721, 81.4951], [-0.9721, 0.3331], [-82.1241, 0.3331], [-82.1341, 81.4951]]
cornerfpc[2] = [[-81.4910, -0.9836], [-0.3290, -0.9800], [-0.3253, -82.1420], [-81.4873, -82.1456]]
cornerfpc[3] = [[0.9747, -81.4918], [0.9756, -0.3298], [82.1376, -0.3306], [82.1367, -81.4926]]
cornerfpc[4] = [[81.4873, 0.9684], [0.3253, 0.9768], [0.3337, 82.1388], [81.4957, 82.1304]]

origin_offset_x, origin_offset_y, ccd_orientation = ccd_positions(ccd_corners=cornerfpc, verbose=True)



