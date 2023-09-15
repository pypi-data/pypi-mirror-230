from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from camtest import load_setup
from camtest.analysis import convenience as cv
from camtest.analysis.functions import hartmann_utils
from camtest.analysis.observation import Observation

setup = load_setup()
print(setup.get_id())

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

colors = ['k',pink,'b',orange,'r','g','m',gray,lightgray,lightgreen,'c']

pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
reduceddir = "/Volumes/IZAR/plato/data/reduced/"

# obsids : list of [obsid, site, plot_label]
obsids = []
obsids.append([900, "CSL", "CSL Final"])
obsids.append([2088, "SRON", "SRON EM1 Start"])
obsids.append([2292, "SRON", "SRON EM1 End"])
obsids.append([2441, "SRON", "SRON EM2 Start"])
obsids.append([3344, "SRON", "SRON EM2 End"])
obsids.append([227, "IAS", "IAS EM Start"])
obsids.append([770, "IAS", "IAS EM End"])

# Fit a sinewave --> determine a tilt wrt the OA : TBW
plotname, outstring = hartmann_utils.hartmann_analysis_circle(obsids, datadir=reduceddir, figname="Circle", verbose=True)
plt.savefig(pngdir + plotname)

txtname = f"{plotname.split('.')[0]}.txt"
with open(Path(pngdir) / txtname, "w") as file:
    file.write(outstring)


# = = =

hobsids = {2088:"SRON", 2292:"SRON", 2441:"SRON", 3344:"SRON", 227:"IAS",770:"IAS"}
hdatadir = {"SRON":"/Volumes/IZAR/plato/data/em/sron/obs/", "IAS":"/Volumes/IZAR/plato/data/em/ias/obs/"}

device = "SYN-HK"
keys = ["GSYN_TRP1", "GSYN_TRP8"]

hktabs = {}
for obsid in hobsids.keys():
    obs = Observation(obsid, site=hobsids[obsid], data_dir=hdatadir[hobsids[obsid]])
    hktabs[obsid] = obs.get_hk_per_cube(device=device, keys=keys, outputfile=None, decimals=6, func=np.nanmean)

"""
# Valid alternative:
from camtest.analysis.functions.hk_utils import hk_per_obsid
hk_per_obsid(obsids=[227], device=device, keys=keys, datadir="/Volumes/IZAR/plato/data/em/ias/obs/",outputfile=None, func=np.nanmean, verbose=True)
"""

avgtrp8 = []
avgtrp1 = []
for obsid in hobsids.keys():
    avg = np.nanmean(hktabs[obsid]['GSYN_TRP8'])
    print(f"{obsid} {avg:7.3f}")
    avgtrp8.append(avg)
    avg1 = np.nanmean(hktabs[obsid]['GSYN_TRP1'])
    print(f"{obsid} {avg1:7.3f}")
    avgtrp1.append(avg1)
avgtrp8 = np.array(avgtrp8) # from here
avgtrp1 = np.array(avgtrp1) # from here
avgell = np.array([23.36, 12.96, 28.87, 48.16, -43.5, -44.49]) # from hartmann_analysis_circle (right above)

idx = np.argsort(avgtrp8)
cfit,yfit,model = cv.mypolyfit(np.sort(avgtrp8), avgell[idx], order=1)

plt.figure("HartmannEll")
plt.plot(np.sort(avgtrp8), avgell[idx], 'ko-', lw=2, label="TRP8")
plt.plot(np.sort(avgtrp8), yfit, c=lightgray, ls="--", lw=1, label=r"fit [$24 \mu m/K]$")
#plt.plot(np.sort(avgtrp1), avgell[idx], 'bo-', lw=2, label="TRP1")
plt.legend(fontsize=14)
plt.xlabel("TRP8 [$^{\circ}$C]", size=14)
plt.ylabel("Avg Ellipse Size [$\mu m$]", size=14)
plt.title(r"SRON EM1 & EM2, IAS Start : Displacement vs Post-CSL [$\mu m$]"+"\n"+r"Assuming $\tau=65 \mu m/pix$", size=14)
plt.grid(alpha=0.25)
plt.savefig(pngdir + "em_sron_ias_ambient_avg_ell_size_vs_trp8_pre-post.png")

### Fitting part of the data
sel = [i for i in range(len(avgtrp8[:-2]))]
idx = np.argsort(avgtrp8[sel])
cfit,yfit,model = cv.mypolyfit(np.sort(avgtrp8[sel]), avgell[sel][idx], order=1)
plt.plot(np.sort(avgtrp8[sel]), avgell[sel][idx], 'go-', lw=2, label="TRP8 - SRON")
plt.plot(np.sort(avgtrp8), model(np.sort(avgtrp8)), c=lightblue, ls="--", lw=1, label=f"fit [{cfit[0]:2.0f}"+r" $\mu m/K]$")
plt.legend(fontsize=14)
plt.savefig(pngdir + "em_sron_ias_ambient_avg_ell_size_vs_trp8_pre-post_incl_SRON_only.png")

