import os

import matplotlib.pyplot as plt
import numpy as np

import camtest.analysis.convenience as cv
import camtest.analysis.functions.hk_utils as hku

datadir = "/Volumes/IZAR/plato/data/CSL1/obs/"
pngdir = "/Volumes/IZAR/plato/data/achel/pngs/"

os.path.exists(datadir)

datafiles = os.listdir(datadir)

fontsize = 14


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

colors = ['k','r','b','g',orange,'c','m',gray,lightgray,lightgreen,pink,lightorange]

# ======================================================================================================================
# AVAILABLE CUBES

obsid = 421
sobsid = str(obsid).zfill(5)

try:
    print("PFM - FM")
    obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
    filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir + obsidir)
    ffilenames = [datadir + obsidir + filename for filename in filenames]
except:
    print("EM")
    filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir)
    ffilenames = [datadir + filename for filename in filenames]

cv.print1(ffilenames)


# obsid = 421
# filenames = cv.fileSelect([f'00{obsid}_','cube','fits'],location=datadir)
# cv.print1(filenames)
# ffilenames = [datadir+filename for filename in filenames]

# HK
device = 'SMC'
device = 'FOV'
hk = hku.get_hk(obsid, device=device,datadir=datadir)

t0 = hk["finetime"][0]

# FRAME TIMES
ftime = cv.get_frame_times(ffilenames)
ftime = np.concatenate([np.array(f,dtype=float) for f in ftime])
rftime = ftime - t0

curpos = hk["axis 1 - cur_pos"]
curpos[np.where(curpos>180)] -= 360.

plt.figure("RS")
plt.plot(hk['reltime'], curpos,'k.-',label="curpos")
#plt.plot(hk['reltime'], hk["axis 1 - enc_cnt"]/1.e7,'r.-',label='encoder / 1.e7')
plt.grid(alpha=0.25)
plt.legend(fontsize=fontsize)
plt.xlabel("Rel.Time",fontsize=fontsize)
plt.ylabel("Stage Pos",fontsize=fontsize)
plt.title(f"Big RS - obsid {obsid}",fontsize=fontsize)

ytf = [-180,180]
plt.plot([rftime[0], rftime[0]], ytf, 'g.-',label='Frames')
for tf in rftime[1:]:
    plt.plot([tf,tf],ytf,'g.-')#,label='Frames')
plt.legend(fontsize=fontsize)
#plt.savefig(pngdir+"spr_1156_stage_synchro.png")


pos2 = hk["axis 2 - cur_pos"]
pos3 = hk["axis 3 - cur_pos"]
dp2 = pos2 - pos2[0]
dp3 = pos3 - pos3[0]

dc = curpos-curpos[0]
ytf = [np.min(dc)*0.95,np.max(dc)*1.05]

plt.figure("RSdiff")
plt.plot(hk['reltime'], dc,'k.-',label="curpos ax1")
plt.plot(hk['reltime'], dp2,'b.-',label="curpos ax2")
plt.plot(hk['reltime'], dp3/10.,c='orange',marker='.',ls='-',label="curpos ax3/10.")


plt.grid(alpha=0.25)
plt.legend(fontsize=fontsize)
plt.xlabel("Rel.Time",fontsize=fontsize)
plt.ylabel("Stage Pos",fontsize=fontsize)
plt.title(f"Big RS - obsid {obsid}",fontsize=fontsize)

#ytf = [-180,180]
plt.plot([rftime[0], rftime[0]], ytf, 'g.-',label='Frames')
for tf in rftime[1:]:
    plt.plot([tf,tf],ytf,'g.-')#,label='Frames')
plt.legend(fontsize=fontsize)
plt.savefig(pngdir+"obsid_919_on_long_pulse_do_sync_test.png")
plt.legend(fontsize=10)


########################################################################################################################

def is_in_position(cmd, pos, tolerance=0.0055):
    """
    True when pos is within 'tolerance' of cmd
    """
    result = np.zeros_like(pos, dtype=bool)
    result[np.where(np.abs(pos-cmd)<=tolerance)] = True
    return result



###   SRON   ###

obsid = 2198
sobsid = str(obsid).zfill(5)

obsidir = cv.fileSelect([f'{sobsid}'],location=datadir)[0] + '/'

filenames = cv.fileSelect([f'{sobsid}_','fits'],location=datadir+obsidir)
cv.print1(filenames)
ffilenames = [datadir + obsidir + filename for filename in filenames]

"""
ffilenames = ffilenames[1::2]
cv.print1(ffilenames)
"""

# Select HK source
#device = "N-FEE-HK"
device = "ENSEMBLE"   # (Gimbal)

# Extract the HK in an astropy.table.Table
hk = hku.get_hk(obsid,device=device,datadir=datadir+obsidir)
t0 = hk["finetime"][0]

# EXTRACT FRAME TIMES (e.g. to compare with HK)
ftimes = cv.get_frame_times(ffilenames)

# FRAME TIMES
#ftime = np.concatenate([np.array(f,dtype=float) for f in ftimes])
rftime = ftimes - t0


xpos = hk["GSRON_ENSEMBLE_ACT_POS_X"]
ypos = hk["GSRON_ENSEMBLE_ACT_POS_Y"]
xcur = hk["GSRON_ENSEMBLE_ACT_CUR_X"]
ycur = hk["GSRON_ENSEMBLE_ACT_CUR_Y"]
xcmd = hk["GSRON_ENSEMBLE_CMD_POS_X"]
ycmd = hk["GSRON_ENSEMBLE_CMD_POS_Y"]

tolerance = 0.0055
xok = is_in_position(xcmd, xpos, tolerance=tolerance)
yok = is_in_position(ycmd, ypos, tolerance=tolerance)
#xyok = xok & yok
xyok = np.array(xok & yok, dtype=int)
inpos = np.zeros_like(xpos,dtype=int)
inpos[np.where(np.diff(xyok)>0)] = 1
inpos = np.roll(inpos,1)
gtimes = hk["finetime"][np.where(inpos)] - t0


# GIMBAL STATUS
plt.figure("GimbalStatus")
plt.plot(hk['reltime'],xok,'k.-', label="X in pos")
plt.plot(hk['reltime'],yok*2.,'r.-', label="Y in pos")
plt.plot(hk['reltime'],xyok*3., 'g.-', label="X & Y in pos")
plt.plot(hk['reltime'],xyok*3., 'g.-', label="X & Y in pos")
plt.plot(hk['reltime'],inpos*4., 'b.-', label="Arrival in pos")


plt.grid(alpha=0.25)
plt.legend(fontsize=fontsize)
plt.xlabel("Rel.Time",fontsize=fontsize)
plt.ylabel("Gimbal Status",fontsize=fontsize)
plt.title(f"Gimbal - obsid {obsid}",fontsize=fontsize)
#plt.savefig(pngdir+"obsid_{obsid}_missing_spots_gimbal_status.png")
#plt.savefig(pngdir+f"gimbal_status_obsid_{obsid}.png")


plt.figure("GimbalFrames")
plt.plot(hk['reltime'], xcmd, c=gray, marker=None,ls='-',label="xcmd")
plt.plot(hk['reltime'], ycmd, c=orange,marker=None,ls='-',label="ycmd")
plt.plot(hk['reltime'], xpos,'k.-',label="xpos")
plt.plot(hk['reltime'], ypos,'r.-',label="ypos")

plt.grid(alpha=0.25)
plt.legend(fontsize=fontsize)
plt.xlabel("Rel.Time",fontsize=fontsize)
plt.ylabel("Stage Pos",fontsize=fontsize)
plt.title(f"Gimbal - obsid {obsid}",fontsize=fontsize)

ytf = [-10,10]
plt.plot([rftime[0], rftime[0]], ytf, 'g.-',label='Frames')
for tf in rftime[1:]:
    plt.plot([tf,tf],ytf,'g.-')#,label='Frames')
plt.legend(fontsize=fontsize)


ytf = [-10,10]
plt.plot([gtimes[0], gtimes[0]], ytf, 'b.-',label='Gimbal Arrives In Pos')
for tf in gtimes[1:]:
    plt.plot([tf,tf],ytf,'b.-')#,label='Frames')
plt.legend(fontsize=fontsize)

plt.savefig(pngdir+f"gimbal_frame_times_obsid_{obsid}.png")



"""
Examples of Gimbal Status HK decoding:
https://github.com/IvS-KULeuven/plato-common-egse/blob/develop/src/egse/stages/aerotech/ensemble_controller.py lines 600 and following tells you how to decode status word in  ENSEMBLE HK file
print(f'\t{"Enabled":20s}: {bool(status & 0x00000001)}')
"""

########################################################################################################################


device = 'SYN-HK'
device = "FOV"
hk = hku.get_hk(obsid, device=device,datadir=datadir)
print(hk.columns)

t0 = hk["finetime"][0]

# FRAME TIMES
ftime = cv.get_frame_times(ffilenames)
ftime = np.concatenate([np.array(f,dtype=float) for f in ftime])
rftime = ftime - t0

print(hk.columns)

thact, phiact = np.array(hk["FOV_ACT_THETA"]), np.array(hk["FOV_ACT_PHI"])
thcmd, phicmd = np.array(hk["FOV_CMD_THETA"]), np.array(hk["FOV_CMD_PHI"])
hktime = hk["reltime"]

fontsize = 14

selcmd = np.where(thcmd !=0)
selact = np.where(thact !=0)

plt.plot(hktime[selact], thact[selact], c=gray, ls='-', marker='.', label=r"HK ACT_THETA")
plt.plot(hktime[selcmd], thcmd[selcmd], 'k.-', label=r"HK CMD_THETA")

plt.plot(hktime[selact], phiact[selact], 'r.-', lw=3, label="HK ACT_PHI")
plt.plot(hktime[selcmd], phicmd[selcmd], c=orange, ls='-', marker='.', ms=20, label="HK CMD_PHI")
plt.legend(fontsize=fontsize)
plt.xlabel("Azimuth [det]", size=fontsize)
plt.ylabel(r"$\Delta$ ACT-CMD [deg]", size=fontsize)
plt.title(f"obsid {obsid} FOV-HK  ACT-CMD FoV positions")

"""
# Not so simple : ACT & CMD never exist simultaneously in the HK.
# CMD only exists when commanded [1 sample now and then]
# ACT is sampled regularly, but CMD has no value at that moment in time
plt.figure("FoV")
plt.plot(phicmd, thact-thcmd, 'k.-', label=r"HK $\delta\theta$")
plt.plot(phicmd, phiact-phicmd, 'r.-', label="HK $\delta\phi$")
plt.legend(fontsize=fontsize)
plt.xlabel("Azimuth [det]", size=fontsize)
plt.ylabel(r"$\Delta$ ACT-CMD [deg]", size=fontsize)
plt.title(f"obsid {obsid} FOV-HK  ACT-CMD FoV positions")
