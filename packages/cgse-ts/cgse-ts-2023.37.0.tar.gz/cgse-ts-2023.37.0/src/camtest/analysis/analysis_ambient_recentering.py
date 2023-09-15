#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 09:50:45 2019

@author: pierre
"""

# Source Extractor in Python
# https://sep.readthedocs.io/en/v1.0.x/tutorial.html

# skimage : pip install scikit-image

# NB: comparison of diff. thresholding approaches : sfil.try_all_threshold(image)


import os
import time

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from astropy.io import fits
from astropy.table import Table
from matplotlib import cm
from scipy.interpolate import interp1d
from skimage import morphology

import camtest.analysis.convenience as cv
from camtest import list_setups, load_setup
from camtest.analysis.functions.hartmann_utils import get_hartmann_ellipse, plotHartmann, analysis_hartmann_cubes, \
    rxry_to_flat
from camtest.analysis.image_utils import backgroundSubtraction
from camtest.analysis.image_utils import cleanSignificant, significantPixels
from camtest.analysis.observation import Observation, download_observation
from camtest.analysis.valid_cubes import valid_cubes
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from camtest.commanding.functions.fov_test_geometry import plotCCDs
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles
from egse.setup import load_setup
from egse.state import GlobalState


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

fsize = 14

#pngdir = "/Users/pierre/plato/pr/pngs/em/"
pngdir = "/Volumes/IZAR/plato/data/em/pngs/"
datadir = "/Volumes/IZAR/plato/data/em/csl/obs/"
outputdir = resultdir = "/Volumes/IZAR/plato/data/em/csl/results/"
outputdir = resultdir = "/Volumes/IZAR/plato/data/em/results/"
outputdir = resultdir = "/Volumes/IZAR/plato/data/reduced/"

os.path.exists(datadir)

datafiles = os.listdir(datadir)

##################################################################
list_setups()
setup = load_setup(setup_id=12, site_id="CSL", from_disk=True)
print(setup.get_id())


##################################################################
# LOAD LDO ANALYSIS RESULTS
##################################################################
# EM
ldodatadir = "/Volumes/IZAR/plato/data/em/ldo_hartmann/ambient/"
ldofilename = "coords_ellipses_v03_meas_xyz_ellipses_pr.txt"
# Achel
camera = "achel"
ldodatadir = "/Volumes/IZAR/plato/data/achel/ldo/data/"
ldofilename = f"{camera}_coords_ellipses_meas_xyz_ellipses_pr.txt"

ldos = ascii.read(ldodatadir + ldofilename,format='fixed_width')
print(ldos.colnames)

# = = = = = = = =

ldodiff = ldos['prellsize']-ldos['radius']/2.

# Extract the data , sorted in phi, and then select one theta
sortsel = ldos['argsort']
thetasortldo, phisortldo = ldos['theta'][sortsel],ldos['phi'][sortsel]
ldodiffsort = ldodiff[sortsel]
ldoradiussort = ldos['radius'][sortsel] / 2.
ldoprellsizesort = ldos['prellsize'][sortsel]

sel16 = np.where(thetasortldo > 16.)
ldophi16 = phisortldo[sel16]
ldodiff16 = ldodiffsort[sel16]
ldoprellsizesort16 = ldoprellsizesort[sel16]
ldoradiussort16 = ldoradiussort[sel16]

sel12 = np.where((thetasortldo>11) & (thetasortldo < 14.))
ldophi12 = phisortldo[sel12]
ldodiff12 = ldodiffsort[sel12]
ldoprellsizesort12 = ldoprellsizesort[sel12]
ldoradiussort12 = ldoradiussort[sel12]

sel8 = np.where((thetasortldo>6) & (thetasortldo < 9))
ldophi8 = phisortldo[sel8]
ldodiff8 = ldodiffsort[sel8]
ldoprellsizesort8 = ldoprellsizesort[sel8]
ldoradiussort8 = ldoradiussort[sel8]

sel3 = np.where(thetasortldo<6)
ldophi3 = phisortldo[sel3]
ldodiff3 = ldodiffsort[sel3]
ldoprellsizesort3 = ldoprellsizesort[sel3]
ldoradiussort3 = ldoradiussort[sel3]

ldosize   = ldoprellsizesort
ldosize16 = ldoprellsizesort16
ldosize12 = ldoprellsizesort12
ldosize8  = ldoprellsizesort8
ldosize3  = ldoprellsizesort3

##################################################################
list_setups()
setup = GlobalState.setup
print(setup)

##################################################################
# Intended CCD coordinates
##################################################################

boresight_angle = 3.1
boresight_angle = 12.4
boresight_angle = 16.33
boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles_in, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
                                                                 [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
                                                                 reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, cside, ccd_side in zip(angles_in, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {cside:1.0f}   {ccd_side}")
    c += 1


thetas_in = angles_in[:,0]
phis_in = angles_in[:,1]

fpcoords_comm = np.array([ccd_to_focal_plane_coordinates(crow,ccol,ccode) for crow,ccol,ccode in zip(ccdrows,ccdcols,ccdcodes)])
angles_comm   = np.array([focal_plane_coordinates_to_angles(xxfp,yyfp) for xxfp,yyfp in zip(fpcoords_comm[:,0],fpcoords_comm[:,1])])
thetas_comm = angles_comm[:,0]
phis_comm   = angles_comm[:,1]

pars_comm, circle_comm = cv.fitCircle(fpcoords_comm)
cenx_comm,ceny_comm,radius_comm = pars_comm


plotCCDs(figname="FoV",setup=setup)
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro')

##################################################################
# PRELIMINARY DATA INSPECTION
##################################################################
# OBSID 467 no probl
# OBSID 468 nothing of cube 0
# OBSID 469 : source seen moving in all layers of cube 0
# OBSID 485 : cube 0 empty. 5 layers in cube 1
# OBSID 497, 498 : cube 0 empty


obsid = 553
filenames = cv.fileSelect([f'00{obsid}_','fits'],location=datadir)
cv.print1(filenames)


# Verify the nb of layers in all cubes of the given obsid & the shape of the datacubes
for cn in range(len(filenames)):
    filename = datadir+filenames[cn]
    hduc = fits.open(filename)
    time.sleep(1)
    print(cn, hduc[2].data.shape)

# BASIC VISUAL INSPECTION

showLayer(0,2,filenames=filenames,obsid=obsid)

ln = 0
for cn in range(len(filenames)):
    showLayer(cn,ln,filenames=filenames,obsid=obsid)

cn = 1
for ln in range(4):
    showLayer(cn,ln,filenames=filenames,obsid=obsid)


##################################################################
# FULL OBSID ANALYSIS  ---   IN DETAIL
##################################################################

selall = np.arange(20)
selno0 = np.arange(20)[1:]
sel424 = [i for i in range(20)]
sel424.pop(10)
sel424.pop(5)
sel_valid = {406:selno0, 424:sel424, 427:selall, 430:np.arange(18),
             467:selall, 468:selno0, 469:sel424, 485:selno0, 486:selno0,
             497:selno0, 498:selno0}

obsid = 498
filenames = cv.fileSelect([f'00{obsid}_','cube','fits'],location=datadir)
cv.print1(filenames)

ncubes = len(filenames)

# Extension number of the image cube
extnc = 2
nlayers = 4

allepars = np.zeros([ncubes,nlayers,5],dtype=float)
alleparssci = np.zeros_like(allepars)

ccdids = np.zeros(ncubes,dtype=int)
ccdsides = np.zeros(ncubes,dtype=str)
rowstarts = np.zeros(ncubes,dtype=int)
allbackgrounds = []
allells, allellssci = [],[]

nan2d = np.array([[np.nan for i in range(5)] for j in range(4)])
#for cn in [0,1]:
for cn in range(ncubes):

    filename = datadir+filenames[cn]

    hduc = fits.open(filename)

    ccdids[cn]     =  hduc[2].header["CCD_ID"]
    ccdsides[cn]   =  hduc[2].header["SENSOR_SEL"][0]
    rowstarts[cn]  =  hduc[0].header["V_START"]
    if  hduc[0].header["V_START"] != -hduc[2].header["CRPIX2"]:
        print(f"WARNING {cn=} {hduc[0].header['V_START']=} {-hduc[2].header['CRPIX2']=}")
    #rowstarts[cn] = -hduc[0].header["CRPIX2"]
    #colstarts[cn] = -hduc[2].header["CRPIX1"]

    cube = np.array(hduc[extnc].data,dtype=float)

    print()
    print(f"Cube {cn:2d} : {filename}   {cube.shape}  CCD {ccdids[cn]}{ccdsides[cn]}  rowstart {rowstarts[cn]}")

    if cube.shape[0]==5:
        print()
        print("WARNING ON CUBE SHAPE {cn} {cube.shape}")
        print()
        cube = cube[1:,:,:]

    if cn not in sel_valid[obsid]:
        allepars[cn, :, :] = nan2d
        alleparssci[cn, :, :] = nan2d
        allbackgrounds.append(None)
        allells.append(None)
        allellssci.append(None)
        print()
        print(f"{obsid} - SKIPPING LAYER {cn}")
        print()
        continue

    #get_hartmann_ellipse(cube, median_size=[1, 15, 15], gauss_sigma=[0, 11, 11], centroiding=True, cleaning=True, backgnd_sub=True, threshold='yen', mad_sigma=3, mad_width=15, verbose=True)
    epars, eparssci, ells, ellssci, significant, signiclean, labels, background = get_hartmann_ellipse(cube.copy())

    allepars[cn,:,:] = epars
    alleparssci[cn,:,:] = eparssci
    allbackgrounds.append(background)
    allells.append(ells)
    allellssci.append(ellssci)

cx,cy,ella,ellb,alpha = np.nanmean(allepars[:,:,0],axis=1),np.nanmean(allepars[:,:,1],axis=1),np.nanmean(allepars[:,:,2],axis=1),np.nanmean(allepars[:,:,3],axis=1),np.nanmean(allepars[:,:,4],axis=1)
cxsci,cysci,ellasci,ellbsci,alphasci = np.nanmean(alleparssci[:,:,0],axis=1),np.nanmean(alleparssci[:,:,1],axis=1),np.nanmean(alleparssci[:,:,2],axis=1),np.nanmean(alleparssci[:,:,3],axis=1),np.nanmean(alleparssci[:,:,4],axis=1)

ellsize, ellsizesci = np.sqrt(ella*ella + ellb*ellb), np.sqrt(ellasci*ellasci + ellbsci*ellbsci)


#np.allclose(np.nanmean(allepars[:,:,0],axis=1)[sel_valid[obsid]], np.nanmean(allepars[sel_valid[obsid],:,0],axis=1))

print(np.allclose(cx,cxsci,equal_nan=True))#,atol=1.e-4)
print(np.allclose(cy,cysci,equal_nan=True))#,atol=1.e-4)
print(np.allclose(ellsize,ellsizesci,equal_nan=True,atol=1.e-1))
print(np.round(ellsize-ellsizesci,4))

hcolstart = {'E':0,'F':2255}
colstarts = np.array([hcolstart[i] for i in ccdsides])

cencol = cx + colstarts
cenrow = cy + rowstarts


# FP coords as measured  AND   COORDINATES OF THE CENTER OF ROTATION
fpcoords_meas = np.array([ccd_to_focal_plane_coordinates(crow,ccol,ccode) for crow,ccol,ccode in zip(cenrow,cencol,ccdids)])
pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[sel_valid[obsid],:])  # kick the NaNs out!!
cenx_meas,ceny_meas,radius_meas = pars_meas
distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")
# obsid 406 (8.3 deg)   : -0.755 -0.361 0.836
# obsid 424 (3.1 deg)   : -0.7499 -0.3489 0.8271
# obsid 427 (12.4 deg)  : -0.8285 -0.3770 0.9102
# obsid 430 (16.33 deg) : -0.8932 -0.3981 0.9779
# theta_correction
# obsid 467 (8.3 deg)   :  0.0203 0.0369 0.0421
# obsid 468 (12.4 deg)  :  0.0108 0.0475 0.0487
# obsid 469 (3.1 deg)   :  0.0474 0.0253 0.0537
# obsid 485 (8.3 deg)   :  0.0243 0.0372 0.0444
# obsid 486 (8.3 deg)   : -0.7989 -0.3025 0.8543 (no theta corr)
# obsid 497 (8.3 deg)   :  0.0238 0.0366 0.0437
# obsid 498 (8.3 deg)   : -0.7989 -0.3025 0.8542 (no theta corr)
# Post - realignment
# obsid 553 (8.3 deg)   : 0.6786 0.7682 1.0250 (theta_corr)

thetaphis_meas = np.array([focal_plane_coordinates_to_angles(x,y) for (x,y) in zip(fpcoords_meas[:,0],fpcoords_meas[:,1])])
thetas_meas, phis_meas = thetaphis_meas[:,0],thetaphis_meas[:,1]
c = 0
for i,j in zip(thetas_meas,phis_meas):
    print(f"{c:2d}   {i:.3f}  {j:8.3f}  {-171+18*c:4d}")
    c+=1


# Systematic in delta_phi ?
delta_phis = phis_meas - phis_comm
cv.stats(delta_phis[sel_valid[obsid]])

delta_thetas = thetas_meas - thetas_comm
cv.stats(delta_thetas[sel_valid[obsid]])



# obsid 430
# selphi = [i for i in range(20)]
# selphi.pop(11)
# selphi.pop(0)
# delta_phis = phis_meas - angles[selphi,1]
# c = 0
# for i,j in zip(phis_meas,angles[selphi,1]):
#     print(f"{c:2d}   {i:.3f}  {j:8.3f}")
#     c+=1

#
# EXPORT THE RESULTS
#


csltab = Table()
csltab["epars"] = allepars
csltab["eparssci"] = alleparssci
csltab["ccdid"] = ccdids
csltab['ccdside'] = ccdsides
csltab['rowstart'] = rowstarts
csltab['cenx'] = cx
csltab['ceny'] = cy
csltab['cencol'] = cencol
csltab['cenrow'] = cenrow
csltab['ella'] = ella
csltab['ellb'] = ellb
csltab['ellsize'] = ellsize
csltab['ellsizesci'] = ellsizesci
csltab["fpcoords_comm"] = fpcoords_comm
csltab["fpcoords_meas"] = fpcoords_meas
csltab["theta_meas"] = thetas_meas
csltab["phi_meas"] = phis_meas
csltab["theta_comm"] = thetas_comm
csltab["phi_comm"] = phis_comm
csltab["theta_in"] = thetas_in
csltab["phi_in"] = phis_in
csltab["delta_phi"] = delta_phis
csltab["delta_theta"] = delta_thetas

csltab.colnames

csltab.write(outputdir+f"obsid_{obsid}_ellipse_table.fits",overwrite=False)

# obsid 430
# csltab["fpcoords_comm"] = fpcoords_comm[selphi]
# csltab["theta_comm"] = angles[selphi,0]
# csltab["phi_comm"] = angles[selphi,1]
# csltab["delta_phis"] = delta_phis
# csltab.write(pngdir+f"obsid_{obsid}_ellipse_table.fits",overwrite=True)


##################################################################
# FULL OBSID ANALYSIS  ---   IN ONE GO
##################################################################


obsid = 2292

filenames = cv.fileSelect([f'00{obsid}_','fits'],location=datadir)
cv.print1(filenames)
ffilenames = [datadir+filename for filename in filenames]


sel_valid = {}
try:
    sel_valid[obsid] = valid_cubes(obsid)
except:
    print("No predefined list of (in)valid cubes. Reducing all.")
    sel_valid[obsid] = np.arange(len(filenames))

skip_layer_0 = False
ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=sel_valid[obsid], nlayers=4, angles_in=angles_in, outputdir=outputdir, overwrite=True, verbose=True, skip_layer_0=skip_layer_0)


#ctab  = Table(csltab[1].data)
fpcoords_meas = csltab["fpcoords_meas"]
pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[sel_valid[obsid],:])  # kick the NaNs out!!
cenx_meas,ceny_meas,radius_meas = pars_meas
distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")








##################################################################
# LAYER SELECTION  ---  REPRODUCIBILITY ANALYSIS
##################################################################


obsid = 813

filenames = cv.fileSelect([f'00{obsid}_','fits'],location=datadir)
cv.print1(filenames)
ffilenames = [datadir+filename for filename in filenames]


sel_valid = {}
try:
    sel_valid[obsid] = valid_cubes(obsid)
except:
    print("No predefined list of (in)valid cubes. Reducing all.")
    sel_valid[obsid] = np.arange(len(filenames))

skip_layer_0 = False
for c in range(5):
    sel_layer=np.arange(3)+1+c*3
    post_fix = f"_sel{c}"
    print(sel_layer, "--", post_fix)
    ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=sel_valid[obsid], nlayers=4,
                                   angles_in=angles_in, outputdir=outputdir, overwrite=True,
                                   verbose=True, skip_layer_0=skip_layer_0, layer_selection=sel_layer,
                                   postfix=post_fix)


#ctab  = Table(csltab[1].data)
fpcoords_meas = csltab["fpcoords_meas"]
pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[sel_valid[obsid],:])  # kick the NaNs out!!
cenx_meas,ceny_meas,radius_meas = pars_meas
distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")



#
# DIAGNOSTIC PLOTS
#

#cslellsize,cslellsizesci = csltab['ellsize'],csltab['ellsizesci']


# print("Ext  --  cube.shape")
# for cn in range(ncubes):
#     filename = datadir+filenames[cn]
#     hduc = fits.open(filename)
#     cube = np.array(hduc[extnc].data,dtype=float)
#     print(f"{cn:2d} - {cube.shape}")


plotCCDs(figname="FoV",setup=setup)
plt.plot(ldos['x_meas'],ldos['y_meas'],c=verylightblue,ls="",marker='o',ms=5,label='LDO_meas')
plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'g+', ms=10)
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1], 'ro')
plt.plot([cenx_comm],[ceny_comm],'g+',ms=10,label='CSL_comm')
plt.plot([cenx_meas],[ceny_meas],'ro',label=f'CSL_meas {obsid}:8.3')
#plt.legend(loc=(0.78,0.86))
plt.legend(loc=(0.715,0.86))
plt.ylabel("Y [mm]")
plt.savefig(pngdir+"em_ldo_csl_recentering_FoV_prior_to_fixing_ccd_to_fp_coordinates_incl_LDO_2obsids_zoom_center.png")

plt.figure('FoV')
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1],c=orange,ls="",marker='o',ms=5)
plt.plot([cenx_meas],[ceny_meas],c=orange,ls="",marker='o',ms=5,label=f'CSL_meas {obsid}:3.1')
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1],c=lightgreen,ls="",marker='o',ms=5)
plt.plot([cenx_meas],[ceny_meas],c=lightgreen,ls="",marker='o',ms=5,label=f'CSL_meas {obsid}:12.4')
plt.plot(fpcoords_meas[:,0], fpcoords_meas[:,1],c=lightgray,ls="",marker='o',ms=5)
plt.plot([cenx_meas],[ceny_meas],c=lightgray,ls="",marker='o',ms=5,label=f'CSL_meas {obsid}:16.33')
plt.legend()
#plt.savefig(pngdir+"em_ldo_csl_recentering_FoV_prior_to_fixing_ccd_to_fp_coordinates_incl_LDO_4obsids.png")






"""
plt.figure("InPhiRadiiLDO_COMP")
plt.plot(ldophi16,ldosize16,c='k',marker='o',ls='-',label=f"16 deg PR")
plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"12 deg PR")
plt.plot(ldophi8,ldosize8,c=lightgray,marker='o',ls='-',label=f" 8 deg PR")
plt.plot(ldophi3,ldosize3,c=lightblue,marker='o',ls='-',label=f" 3 deg PR")
plt.plot(ldophi16,ldoradiussort16,c='k',marker='o',ls='--',label=f"16 deg DV")
plt.plot(ldophi12,ldoradiussort12,c=gray,marker='o',ls='--',label=f"12 deg DV")
plt.plot(ldophi8,ldoradiussort8,c=lightgray,marker='o',ls='--',label=f"8 deg DV")
plt.plot(ldophi3,ldoradiussort3,c=lightblue,marker='o',ls='--',label=f"3 deg DV")
plt.grid(alpha=0.25)
plt.plot(cslphis[1:],cslellsizesci[1:],c=lightgreen,marker='o',ls='-',label="8 deg CSL PR")
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth. Obsid {obsid}",size=fsize)
#plt.savefig(ldopngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_absolute_incl_csl_all.png")
"""
plt.figure("InPhiRadii")
plt.plot(ldophi16,ldosize16,c='k',marker='o',ls='-',label=f"LDO 16 deg")
plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"LDO 12 deg")
plt.plot(ldophi8,ldosize8,c=lightgray,marker='o',ls='-',label=f"LDO 8 deg")
plt.plot(ldophi3,ldosize3,c=lightblue,marker='o',ls='-',label=f"LDO 3 deg")
plt.plot(phis_meas[sel_valid[obsid]],ellsizesci[sel_valid[obsid]],c=lightgray,marker='o',ls='--',label=r"CSL 8 deg [$\theta$ corr]")
plt.plot(phis_meas[sel_valid[obsid]],ellsizesci[sel_valid[obsid]],c=gray,marker='o',ls='--',label=r"CSL 12 deg [$\theta$ corr]")
plt.plot(ctab8['phi_meas'][sel_valid[obsid]],ctab8['ellsizesci'][sel_valid[obsid]],c=lightgray,marker='o',ls=':',label=r"CSL 8 deg [no $\theta$ corr]")

plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth. Obsid {obsid}",size=fsize)
#plt.savefig(ldopngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_absolute_incl_csl_all.png")


phi8180 = np.array(phi8.copy())
phi8180[np.where(phi8180<0.)] += 360.
phi8180 -= 180.
ssel180 = np.argsort(phi8180)
prellsizesort8180 = prellsizesort8.copy()[ssel180]
phi8180 = phi8180[ssel180]

plt.figure("InPhi180deg")
plt.plot(phi8,prellsizesort8,c=gray,marker='o',ls='-',label=f"LDO 8 deg")
plt.plot(phi8180,prellsizesort8180,c=lightgray,marker='o',ls='-',label=f"LDO 8 deg - azimuth+180")
plt.plot(cslphis[1:],cslellsizesci[1:],c=lightgreen,marker='o',ls='-',label="CSL 8 deg")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth. Obsid {obsid}\nAzimuth LDO + 180 deg",size=fsize)
#plt.savefig(pngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_absolute_incl_csl_zoom_ldo_azimuth_180.png")


# Difference between fitting methods <= 0.015 pixels : negligible
# plt.figure("CSLdiff")
# plt.plot(cslellsizesci-cslellsize,'k.-')

cslav8 = np.mean(cslellsizesci[1:])
ldoav8 = np.mean(prellsizesort8180)
print(f"CSL {cslav8:.3f} LDO {ldoav8:.3f}  Diff {cslav8-ldoav8:.3f}")

x, y = cslphis[1:], cslellsizesci[1:]
f = interp1d(x,y,kind='linear')
csl_at_ldophis = f(phi8)
csl_at_ldophis180 = f(phi8180)

plt.figure("InPhiRadii")
plt.plot(phi8,csl_at_ldophis,'go--',label="8 deg CSL interp.")
#plt.plot(phi8180,csl_at_ldophis180,'bo--',label="8 deg CSL interp. 180")
plt.grid(alpha=0.25)
plt.legend()

cv.stats(csl_at_ldophis-prellsizesort8)
cv.stats(csl_at_ldophis180-prellsizesort8180)

plt.figure("CSLLDO")
plt.plot(phi8,csl_at_ldophis-prellsizesort8,c=lightgreen,marker='o',ls='-',label="8 deg CSL(interp.) - LDO")
plt.plot(phi8180,csl_at_ldophis180-prellsizesort8180,c=lightgray,marker='o',ls='-',label="8 deg CSL(interp.) - LDO+180deg")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("(CSL-LDO) $\delta\Sigma$ [pix]",size=fsize)
plt.title(f"$\delta Ellipse\ size\ (\delta\Sigma)$ vs azimuth ($\phi$). Obsid {obsid}",size=fsize)
#plt.savefig(pngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_difference_csl-ldo_incl_azimuth_180_altcolor.png")



fsize=14
plt.figure("theta_vs_phi")
plt.plot(phis_meas, thetas_meas, c=gray, marker='o',ls='-',label=f"8 deg {obsid=}")
plt.plot(phis_meas, thetas_meas, c=lightblue, marker='o',ls='-',label=f"3.1 deg {obsid=}")
plt.plot(phis_meas, thetas_meas, c=lightgray, marker='o',ls='-',label=f"12.4 deg {obsid=}")
plt.plot(phis_meas, thetas_meas, c='k', marker='o',ls='-',label=f"16.3 deg {obsid=}")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Boresight Angle  $[^\circ]$",size=fsize)
plt.title(f"Measured FoV positions [no recentering]",size=fsize)
plt.savefig(pngdir+f"em_ldo_theta_vs_phi_meas_csl_4obsids.png")

plt.figure("delta_phis")
plt.plot(phis_meas[validcubesel], delta_phis, c=gray, marker='o',ls='-',label=f"8 deg {obsid=}")
plt.plot(phis_meas[sel_valid[obsid]], delta_phis[sel_valid[obsid]], c=lightblue, marker='o',ls='-',label=f"3 deg {obsid=}")
plt.plot(phis_meas[sel_valid[obsid]], delta_phis[sel_valid[obsid]], c=lightgray, marker='o',ls='-',label=f"12 deg {obsid=}")
plt.plot(phis_meas, delta_phis, c='k', marker='o',ls='-',label=f"16 deg {obsid=}")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Delta Azimuth  $\delta\phi\ [^\circ]$",size=fsize)
plt.title(f"Measured FoV positions [no recentering]",size=fsize)
plt.xlim(-180,180.)
plt.ylim(-10,0.)
plt.savefig(pngdir+f"em_ldo_delta_phi_meas_csl_4obsids.png")



#
# Unified results
#

hobsids = {3:424, 8:406, 12:427, 16:430}
csl3 = fits.open(outputdir+f"obsid_{hobsids[3]}_ellipse_table.fits")
csl8 = fits.open(outputdir+f"obsid_{hobsids[8]}_ellipse_table.fits")
csl12 = fits.open(outputdir+f"obsid_{hobsids[12]}_ellipse_table.fits")
csl16 = fits.open(outputdir+f"obsid_{hobsids[16]}_ellipse_table.fits")

ctab3  = Table(csl3[1].data)
ctab8  = Table(csl8[1].data)
ctab12 = Table(csl12[1].data)
ctab16 = Table(csl16[1].data)

# Theta corr setup 71
hobsidst = {3:469, 8:467, 12:468, 16:470} # Incl theta_correction setup 71
#csl3t = fits.open(outputdir+f"obsid_{hobsidst[3]}_ellipse_table.fits")
csl8t = fits.open(outputdir+f"obsid_{hobsidst[8]}_ellipse_table.fits")
csl12t = fits.open(outputdir+f"obsid_{hobsidst[12]}_ellipse_table.fits")
#csl16t = fits.open(outputdir+f"obsid_{hobsidst[16]}_ellipse_table.fits")
#ctab3t  = Table(csl3t[1].data)
ctab8t  = Table(csl8t[1].data)
ctab12t = Table(csl12t[1].data)
#ctab16t = Table(csl16t[1].data)




plt.figure("InPhiRadii")
plt.plot(ldophi16,ldosize16,c=lightgray,marker='o',ls='-',label=f"LDO 16 deg")
plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"LDO 12 deg")
plt.plot(ldophi8,ldosize8,c=lightblue,marker='o',ls='-',label=f"LDO 8 deg")
plt.plot(ldophi3,ldosize3,c='k',marker='o',ls='-',label=f"LDO 3 deg")
plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],ctab16['ellsizesci'][sel_valid[hobsids[16]]],c=lightgray,marker='o',ls='--',label="CSL 16 deg")
plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],ctab12['ellsizesci'][sel_valid[hobsids[12]]],c=gray,marker='o',ls='--',label="CSL 12 deg")
plt.plot(ctab8['phi_meas'][sel_valid[hobsids[8]]],ctab8['ellsizesci'][sel_valid[hobsids[8]]],c=lightblue,marker='o',ls='--',label="CSL 8 deg")
plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],ctab3['ellsizesci'][sel_valid[hobsids[3]]],c='k',marker='o',ls='--',label="CSL 3 deg")
#plt.plot(ctab16t['phi_meas'][sel_valid[hobsidst[16]]],ctab16t['ellsizesci'][sel_valid[hobsidst[16]]],c=lightgray,marker='o',ls='--',label=r"CSL 16 w/ $\theta$ corr")
plt.plot(ctab12t['phi_meas'][sel_valid[hobsidst[12]]],ctab12t['ellsizesci'][sel_valid[hobsidst[12]]],c=gray,marker='o',ls=':',label=r"CSL 12 w/ $\theta$ corr")
plt.plot(ctab8t['phi_meas'][sel_valid[hobsidst[8]]],ctab8t['ellsizesci'][sel_valid[hobsidst[8]]],c=lightblue,marker='o',ls=':',label=r"CSL 8 w/ $\theta$ corr")
#plt.plot(ctab3t['phi_meas'][sel_valid[hobsidst[3]]],ctab3t['ellsizesci'][sel_valid[hobsidst[3]]],c='k',marker='o',ls='--',label=r"CSL 3 w/ $\theta$ corr")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth",size=fsize)
plt.ylim(26,38)
plt.savefig(pngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_absolute_incl_csl_with_thetacorr_812.png")




# 8 = original measurement at 8.3 deg
# 8t = incl. theta_corr  (there was a hex_goto_zero in between)
# 8r & 8tr = repeat of the above
# 8h & 8ht repeat of the above, after yet another hex_goto_zero & back to hartmann plane
csl8 = fits.open(outputdir+f"obsid_406_ellipse_table.fits")
csl8t = fits.open(outputdir+f"obsid_467_ellipse_table.fits")
csl8r = fits.open(outputdir+f"obsid_486_ellipse_table.fits")
csl8tr = fits.open(outputdir+f"obsid_485_ellipse_table.fits")
csl8h = fits.open(outputdir+f"obsid_497_ellipse_table.fits")
csl8th = fits.open(outputdir+f"obsid_498_ellipse_table.fits")
ctab8  = Table(csl8[1].data)
ctab8t  = Table(csl8t[1].data)
ctab8r  = Table(csl8r[1].data)
ctab8tr  = Table(csl8tr[1].data)
ctab8h  = Table(csl8h[1].data)
ctab8th  = Table(csl8th[1].data)


# Theta_correction investigation
plt.figure("EllipseThetaCorr2")
plt.plot(ldophi8,ldosize8,c='k',marker='o',ls='-',label=f"LDO")
plt.plot(  ctab8['phi_meas'][sel_valid[406]],  ctab8['ellsizesci'][sel_valid[406]],c=lightblue,marker='o',ls='--',label="CSL orig")
plt.plot( ctab8t['phi_meas'][sel_valid[467]], ctab8t['ellsizesci'][sel_valid[467]],c=lightgreen,marker='o',ls=':',label=r"CSL w/ $\theta$ corr")
plt.plot( ctab8r['phi_meas'][sel_valid[485]], ctab8r['ellsizesci'][sel_valid[485]],c=lightgray,marker='o',ls='--',label="CSL repeat")
plt.plot(ctab8tr['phi_meas'][sel_valid[486]],ctab8tr['ellsizesci'][sel_valid[486]],c=gray,marker='o',ls=':',label=r"CSL repeat w/ $\theta$ corr")
plt.plot( ctab8h['phi_meas'][sel_valid[497]], ctab8h['ellsizesci'][sel_valid[497]],c=orange,marker='o',ls='--',label="CSL hex repos")
plt.plot(ctab8th['phi_meas'][sel_valid[498]],ctab8th['ellsizesci'][sel_valid[498]],c=pink,marker='o',ls=':',label=r"CSL hex repos w/ $\theta$ corr")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth - 8 deg",size=fsize)
plt.savefig(pngdir+"em_ldo_compare_ellipse_size_8deg_reproducibility_6obsids_w_ldo_12.png")

plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"LDO")

#plt.plot(ldophi16,ldosize16,c=lightgray,marker='o',ls='-',label=f"LDO 16 deg")
#plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"LDO 12 deg")
#plt.plot(ldophi3,ldosize3,c='k',marker='o',ls='-',label=f"LDO 3 deg")
#plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],ctab16['ellsizesci'][sel_valid[hobsids[16]]],c=lightgray,marker='o',ls='--',label="CSL 16 deg")
#plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],ctab12['ellsizesci'][sel_valid[hobsids[12]]],c=gray,marker='o',ls='--',label="CSL 12 deg")
#plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],ctab3['ellsizesci'][sel_valid[hobsids[3]]],c='k',marker='o',ls='--',label="CSL 3 deg")
#plt.plot(ctab16t['phi_meas'][sel_valid[hobsidst[16]]],ctab16t['ellsizesci'][sel_valid[hobsidst[16]]],c=lightgray,marker='o',ls='--',label=r"CSL 16 w/ $\theta$ corr")
#plt.plot(ctab12t['phi_meas'][sel_valid[hobsidst[12]]],ctab12t['ellsizesci'][sel_valid[hobsidst[12]]],c=gray,marker='o',ls=':',label=r"CSL 12 w/ $\theta$ corr")
#plt.plot(ctab3t['phi_meas'][sel_valid[hobsidst[3]]],ctab3t['ellsizesci'][sel_valid[hobsidst[3]]],c='k',marker='o',ls='--',label=r"CSL 3 w/ $\theta$ corr")






plt.figure("dtheta")
plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],ctab16['theta_meas'][sel_valid[hobsids[16]]]-16.33,c=lightgray,marker='o',ls='--',label="CSL 16 deg")
plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],ctab12['theta_meas'][sel_valid[hobsids[12]]]-12.4,c=gray,marker='o',ls='--',label="CSL 12 deg")
plt.plot(ctab8['phi_meas'][sel_valid[hobsids[8]]],ctab8['theta_meas'][sel_valid[hobsids[8]]]-8.3,c=lightblue,marker='o',ls='--',label="CSL 8 deg")
plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],ctab3['theta_meas'][sel_valid[hobsids[3]]]-3.1,c='k',marker='o',ls='--',label="CSL 3 deg")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $\phi\ [^\circ]$",size=fsize)
plt.ylabel(r"Boresight error $\delta\theta\ [^\circ]$",size=fsize)
plt.title(f"Boresight error vs azimuth",size=fsize)
plt.savefig(pngdir+"em_ldo_boresight_error_vs_azimuth_4obsids.png")

delta_thetas16 = ctab16['theta_meas'][sel_valid[hobsids[16]]]-16.33
delta_thetas12 = ctab12['theta_meas'][sel_valid[hobsids[12]]]-12.4
delta_thetas8  = ctab8['theta_meas'][sel_valid[hobsids[8]]]-8.3
delta_thetas3  = ctab3['theta_meas'][sel_valid[hobsids[3]]]-3.1
cv.stats(delta_thetas3*60.)
cv.stats(delta_thetas8*60.)
cv.stats(delta_thetas12*60.)
cv.stats(delta_thetas16*60.)

delta_thetas3_0  = delta_thetas3 - np.mean(delta_thetas3)
delta_thetas8_0  = delta_thetas8 - np.mean(delta_thetas8)
delta_thetas12_0 = delta_thetas12 - np.mean(delta_thetas12)
delta_thetas16_0 = delta_thetas16 - np.mean(delta_thetas16)
phis_meas3  = ctab3['phi_meas'][sel_valid[hobsids[3]]]
phis_meas8  = ctab8['phi_meas'][sel_valid[hobsids[8]]]
phis_meas12 = ctab12['phi_meas'][sel_valid[hobsids[12]]]
phis_meas16 = ctab16['phi_meas'][sel_valid[hobsids[16]]]

# def fit_sin temporarily in playAmbientAnalysis
phis_meas_4obs = np.concatenate([phis_meas3,phis_meas8,phis_meas12,phis_meas16])
delta_thetas_0_4obs = np.concatenate([delta_thetas3_0,delta_thetas8_0,delta_thetas12_0,delta_thetas16_0])
selsortcorr = np.argsort(phis_meas_4obs)

from scipy.optimize import curve_fit
def sine_func(x, freq, amplitude, phase, offset):
    return np.sin(x * freq + phase) * amplitude + offset

# p0=[guess_freq, guess_amplitude,
#     guess_phase, guess_offset]
p0 = [1./360., 0.4, 0.5, 0.]
fit = curve_fit(sine_func, phis_meas_4obs[selsortcorr], delta_thetas_0_4obs[selsortcorr], p0=p0)
delta_theta_correction_phi   = np.arange(-180,189,9.)
delta_theta_correction_theta = sine_func(delta_theta_correction_phi, *fit[0])

### EXPORT CORRECTION TABLE  (the correction shall be added to the commanded value, the minus sign is included here)
#
print(np.round(fit[0],4))
#
# theta_correction_table = Table()
# theta_correction_table['phi'] = delta_theta_correction_phi
# theta_correction_table['theta'] = - np.round(delta_theta_correction_theta, 4)
# ascii.write(theta_correction_table,pngdir+'boresight_vs_azimuth_correcction_em_001.txt',overwrite=False,format='fixed_width')
###


for i,j in zip([3,8,12,16], [delta_thetas3,delta_thetas8,delta_thetas12,delta_thetas16]):
    print(f"{i} {(np.max(j)-np.min(j))/2.:.3f}")

plt.figure("meandtheta")
plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],delta_thetas16 - np.mean(delta_thetas16),c=lightgray,marker='o',ls='--',label="CSL 16 deg")
plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],delta_thetas12 - np.mean(delta_thetas12),c=gray,marker='o',ls='--',label="CSL 12 deg")
plt.plot(ctab8['phi_meas'][sel_valid[hobsids[8]]],delta_thetas8 - np.mean(delta_thetas8),c=lightblue,marker='o',ls='--',label="CSL 8 deg")
plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],delta_thetas3 - np.mean(delta_thetas3),c='k',marker='o',ls='--',label="CSL 3 deg")
plt.plot(delta_theta_correction_phi, delta_theta_correction_theta, 'ro-', label='- correction')
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $\phi\ [^\circ]$",size=fsize)
plt.ylabel(r"Boresight error $\delta\theta\ - mean(\delta\theta)\ [^\circ]$",size=fsize)
plt.title(f"Offset boresight error vs azimuth",size=fsize)
plt.savefig(pngdir+"em_ldo_boresight_error_offsetted_vs_azimuth_4obsids_incl_correction.png")





plt.figure("theta")
#plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],ctab16['theta_meas'][sel_valid[hobsids[16]]],c=lightgray,marker='o',ls='--',label="CSL 16 deg")
plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],ctab12['theta_meas'][sel_valid[hobsids[12]]],c=gray,marker='o',ls='--',label="CSL 12 deg")
plt.plot(ctab8['phi_meas'][sel_valid[hobsids[8]]],ctab8['theta_meas'][sel_valid[hobsids[8]]],c=lightblue,marker='o',ls='--',label="CSL 8 deg")
#plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],ctab3['theta_meas'][sel_valid[hobsids[3]]]-3.1,c='k',marker='o',ls='--',label="CSL 3 deg")

plt.plot(ctab12t['phi_meas'][sel_valid[hobsids[12]]],ctab12t['theta_meas'][sel_valid[hobsids[12]]],c=gray,marker='o',ls='-',label=r"CSL 12 deg w/ $\theta$ corr")
plt.plot(ctab8t['phi_meas'][sel_valid[hobsids[8]]],ctab8t['theta_meas'][sel_valid[hobsids[8]]],c=lightblue,marker='o',ls='-',label=r"CSL 8 deg w/ $\theta$ corr")

plt.plot(ctab12t['phi_meas'][sel_valid[hobsids[12]]],ctab12t['theta_comm'][sel_valid[hobsids[12]]],c=gray,marker='o',ls=':',label="CSL 12 deg [comm]")
plt.plot(ctab8t['phi_meas'][sel_valid[hobsids[8]]],ctab8t['theta_comm'][sel_valid[hobsids[8]]],c=lightblue,marker='o',ls=':',label="CSL 8 deg [comm]")

plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $\phi\ [^\circ]$",size=fsize)
plt.ylabel(r"Boresight_meas $\theta\ [^\circ]$",size=fsize)
plt.title(f"Boresight_meas vs azimuth",size=fsize)
plt.savefig(pngdir+f"em_ldo_boresight_error_vs_azimuth_8deg_with_without_theta_correction.png")





























##################################################################
# CUBE-BASED ANALYSIS
##################################################################
# OBSID 406 : no data in first FoV position
# OBSID 424 : no data in FoV positions 5,10  (the source is on the egde of the CCD, outside)
# OBSID 427 : no issue

# obsid = 842
# filenames = cv.fileSelect([f'00{obsid}_','fits'],location=datadir)
# cv.print1(filenames)
# ffilenames = [datadir+filename for filename in filenames]

obsid = 2113
obsid = 770
sobsid = str(obsid).zfill(5)

obsidir = cv.fileSelect([f'{sobsid}'],location=datadir)[0] + '/'

filenames = cv.fileSelect([f'{sobsid}_','fits'],location=datadir+obsidir)
cv.print1(filenames)
ffilenames = [datadir + obsidir + filename for filename in filenames]
cv.print1(ffilenames)


"""
# Verify the nb of layers in all cubes of the given obsid
for cn in range(len(filenames)):
    filename = datadir+filenames[cn]
    hduc = fits.open(filename)
    time.sleep(1)
    print(cn, hduc[2].data.shape)
"""

# BASIC VISUAL INSPECTION


cv.showLayer(10,1,filenames=ffilenames,obsid=obsid)

for cn in range(len(filenames)):
    cv.showLayer(cn,0,filenames=filenames,obsid=obsid)


cn = 11
filename = ffilenames[cn]
hduc = fits.open(filename)
time.sleep(0.5)
hduc.info()
extnc = 2
cube = np.array(hduc[extnc].data,dtype=float)
layer=3
cv.imshow(cube[layer,:,:,],vsigma=2,cmap=cm.inferno)

# hduc[0].header
# hduc[2].header
#
# #tabs = ff.get_absolute_time(filename)
# extnames = ff.get_ext_names(filename)

"""
sccd = f"CCD_{hduc[2].header['CCD_ID']}{hduc[2].header['SENSOR_SEL']}"
cv.imshow(cube[layer,:,:,],vmin=38000,vmax=56000)
plt.colorbar()
plt.title(f"{obsid=} cube={cn} {layer=} {sccd}",size=20)
plt.savefig(pngdir+f"em_obsid_{obsid}_cube_{cn}_layer_{layer}_{sccd}_zoom.png")

diff = cube[1,:,:,]-cube[0,:,:,]
cv.imshow(diff,vsigma=2,cmap=cm.inferno)

sf = ndi.generic_filter(diff, np.std, size=15)

cv.imshow(sf,vsigma=2,cmap=cm.inferno)

"""

epars, eparssci, ells, ellssci, significant, signiclean, labels, bgnd = get_hartmann_ellipse(cube.copy())

bgndsub = cube[1:,:,:] - bgnd

layer=3
cv.imshow(bgndsub[layer,:,:,],vsigma=2,cmap=cm.inferno)

rowmin,rowmax, colmin,colmax = 470,530,850,900
cv.imshow(bgndsub[layer,rowmin:rowmax, colmin:colmax],vsigma=2,cmap=cm.inferno)
cv.imshow(significant[layer,rowmin:rowmax, colmin:colmax],vsigma=2,cmap=cm.inferno)
testimage = significant[layer,rowmin:rowmax, colmin:colmax]


### ELLIPSE EXTRACTION FROM DATA-CUBE
#####################################

ts = time.process_time()
epars, eparssci, ells, ellssci, significant, signiclean, labels, bgnd = get_hartmann_ellipse(cube.copy())
te = time.process_time()
print(te, ts, te-ts)


### ELLIPSE VISUALISATION
#############################
site = 'ias'
saveplot = 1
bgndsub = cube[1:,:,:] - bgnd
nlayers = bgndsub.shape[0]
for layer in range(nlayers):
    # with IMAGE
    # plotHartmann(cube[layer, :, :], significant[layer, :, :], signiclean[layer, :, :], labels[layer, :, :],
    #              fitmethod='pers', pltborder=6, vsigma=1, cmap=cm.inferno,
    #              title=f"{obsid=}[{cn}]: \ncube {layer=}")
    # if saveplot: plt.savefig(pngdir+f"em_{site}_{obsid}_ext_{cn}_layer_{layer}_hartmann_plot.png")
    # with BACKGROUND subtraction
    plotHartmann(bgndsub[layer, :, :], significant[layer, :, :], signiclean[layer, :, :], labels[layer, :, :],
                 fitmethod='pers', pltborder=6, vsigma=1, cmap=cm.inferno,
                 title=f"{obsid=}[{cn}]: \ncube {layer=}")
    if saveplot: plt.savefig(pngdir+f"em_{site}_{obsid}_ext_{cn}_layer_{layer}_hartmann_plot_bgnd_cleaningFalse.png")
    plt.close()


### ELLIPSE SIZE AND LOCATION
#############################

# Compare both Ellipse fitting routines:
ellsize = np.sqrt(pow(epars[:,2],2) + pow(epars[:,3],2))
ellsizesci = np.sqrt(pow(eparssci[:,2],2) + pow(eparssci[:,3],2))
print(ellsize-ellsizesci)
print(f"Fitting methods give the same ellipse size: {np.allclose(ellsize-ellsizesci,0.,atol=1.e-4)}")

cv.stats(ellsize)

size=14
plt.figure('ellsize')
plt.plot(ellsize)
plt.grid(alpha=0.25)
plt.xlabel('Layer',size=size)
plt.ylabel('Pixels',size=size)
plt.title(f"Ellipse Size : {np.mean(ellsize):.3f} $\pm$ {np.std(ellsize):.3f}",size=size)
plt.savefig(pngdir+f"em_{obsid}_ext_{extn}_ellipse_size.png")


































##################################################################
# BELOW = DRAFT VERSION: STEP BY STEP ANALYSIS OF SIMULATED IMAGES
##################################################################

dataDir = "/Volumes/IZAR/plato/simout/testprep/hartmann8_45/"
pngDir  = "/Users/pierre/plato/pr/pngs/testprep/"
fitsDir = dataDir+"fits/"

fitsfiles = os.listdir(fitsDir)
cv.print1(fitsfiles)


#############################################################
# Analysis Single Image
#############################################################

## OPEN FITS FILE
## ------------

fits_filename = fitsDir+fitsfiles[0]

hdu = fits.open(fits_filename)

hdu.info()

image = np.array(hdu["IMAGE_4",0].data,dtype=float)
header = hdu["IMAGE_4",0].header

rowpix1, colpix1 = -header["CRPIX2"], -header["CRPIX1"]
rowpixn, colpixn = header["NAXIS2"], header["NAXIS1"]

raw = image.copy()
plt.figure("raw")
plt.imshow(raw,interpolation="nearest",cmap=cm.gray,clim=(8000,15000))
plt.xlim(1360,1420)
plt.ylim(170,230)

## BIAS REMOVAL
## ------------

bias_filename = "biasfilename.fits"
bhdu = fits.open(bias_filename)
bhdu.info()

bias =
image = image - bias

## FF Correction
## -------------
ff_filename = "flatfilename.fits"
fhdu = fits.open(ff_filename)
fhdu.info()

flatfull =
flatsub = flatfull[colpix1:colpix1+colpixn,rowpix1:rowpix1+rowpixn]
image = image / flatsub

## BACKGROUND SUBTRACTION
## ----------------------

#  FLAT BACKGROUND:
backgroundMethod = 'edge'
median_size,gauss_sigma = None,None

# SMOOTH VARYING BACKGROUND
backgroundMethod = 'sep'
median_size,gauss_sigma = None,None

# LOCAL BACKGROUND
backgroundMethod = 'filter'
median_size,gauss_sigma = [21,21],11

image, background = backgroundSubtraction(image,method=backgroundMethod,width=10,verbose=True, median_size=median_size, gauss_sigma=gauss_sigma)

plt.figure('backgndsub')
plt.imshow(image, interpolation='nearest',origin='lower',cmap=cm.hot,clim=(0,5000))
plt.xlim(1360,1420)
plt.ylim(170,230)

#censigma, boxsigma = psfBox(image, method='sigma', sigma=sigma, cosmicRemoval=filtering, kernel=None, verbose=1)


#####################
## SIGNIFICANT PIXELS
#####################

##  A. Rough Selection

sigma = 5

# Global Yen Thresholding
imyen = significantPixels(image,method='yen')

# Global sigma clipping
#imglo = significantPixels(image,method='global',sigma=sigma)

# Local m.a.d. clipping -- !! Long Computation Time
#imloc = significantPixels(image,method='local',sigma=sigma)

## B. Filtering out the isolated pixels

significant = imyen

signiclean = cleanSignificant(significant,method='union')



#####################
## LABEL THE HARTMANN SPOTS
#####################

labels = morphology.label(signiclean, background=0)
nlabelsorig = nlabels = np.max(labels)


ilabels = [i for i in range(1, nlabels + 1)]
slabels = [len(np.where(labels == n)[0]) for n in ilabels]
print(f"Nb & sizes of the original labels : {nlabels} -- {slabels}")

sel = np.where(labels != 0)

pltborder = 6
xmin,xmax = np.min(sel[1])-pltborder,np.max(sel[1])+pltborder
ymin,ymax = np.min(sel[0])-pltborder,np.max(sel[0])+pltborder

print(f"In the image: [{xmin:7.2f},{xmax:7.2f}]   --   On the CCD: [{xmin+colpix1:7.2f},{xmax+colpix1:7.2f}]")
print(f"              [{ymin:7.2f},{ymax:7.2f}]                    [{ymin+rowpix1:7.2f},{ymax+rowpix1:7.2f}]")


plt.figure("labels")
plt.imshow(labels, cmap=plt.cm.nipy_spectral,interpolation='nearest',origin='lower',clim=(0.,np.max(labels)))
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)

"""
plt.figure('signiclean')
plt.imshow(signiclean, interpolation='nearest',origin='lower',cmap=cm.hot,clim=(0,1))

plt.figure('significant')
plt.imshow(significant, interpolation='nearest',origin='lower',cmap=cm.hot,clim=(0,1))

plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
"""

#####################
## FIT AN ELLIPSE TO THE HARTMANN PATTERN
#####################


# A. COLLECT ALL LABELLED POINTS INTO A DATASET
sel = np.where(labels != 0)
ellipsin = np.vstack(sel).T

# B. FIT AN ELLIPSE TO THAT SET OF COORDINATES
ellpars, ellipse = cv.fitEllipse(ellipsin)
ellparsci, ellipsesci = fitEllipseScikit(ellipsin)


#####################
## PLOT RESULT
#####################


plotHartmann(image,significant,signiclean,labels)
plt.savefig(pngDir+f"hartmann_pattern_4_panels.png")




#####################
## CHANGE TO FOCAL PLANE COORDINATES
#####################
# So far we have the coordinates in pixel on one CCD
# We want to fit a circle to various detection spread over all 4 CCDs
# --> we need one common reference frame. Logically we must therefore use the focal plane coordinates

# Assuming we visit 20 position in total, over 1 circle
nfovpos = 20

# Radius of the circle
boresight_angle = 6.85

# CCD coordinates where the images SHOULD land
# ccdrows, ccdcols, ccdcodes, ccdsides, angles = circle_fov_geometry(n=nfovpos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=False)


# CCD coordinats where the images DID land
ccdrows, ccdcols, ccdcodes = np.zeros(nfovpos), np.zeros(nfovpos), np.zeros(nfovpos)

ccdrows[0],ccdcols[0],ccdcodes[0] = ellpars[0]+rowpix1, ellpars[1]+colpix1,header["CCD_ID"]

# Focal Plane Coordinates
xfps,yfps = np.zeros(nfovpos), np.zeros(nfovpos)
xfps[0],yfps[0] = ccd_to_focal_plane_coordinates(ccdrows[0],ccdcols[0],ccdcodes[0])



for ccdn in [1,2,3,4]:

    xfps[ccdn],yfps[ccdn] = ccd_to_focal_plane_coordinates(ccdrows[0],ccdcols[0],ccdn)

    print(f"{ccdn} - [{xfps[ccdn]},{yfps[ccdn]}]")



######################  ANALYSIS STARTING FROM FITS   ############################################

## LDO
ldos = ascii.read(ldodatadir + "coords_ellipses_v03_meas_xyz_ellipses_pr.txt",format='fixed_width')
print(ldos.colnames)

lpd = ldos.to_pandas()

lpds = lpd.sort_values('phi_meas')
lpds.set_index(np.arange(40), inplace=True)
lpds.index

lsel3 = (lpds.theta_meas<4)
lsel8 = (lpds.theta_meas>6) & (lpds.theta_meas<10)
lsel12 = (lpds.theta_meas>10) & (lpds.theta_meas<14)
lsel16 = (lpds.theta_meas>14)

## CSL

obsid  = 553
filenames = cv.fileSelect([f'{obsid}_','fits'],location=resultdir)
print(filenames)

csltab = fits.open(resultdir+filenames[0])
ctab  = Table(csltab[1].data)
print(ctab.colnames)

### TO PANDAS DATAFRAME
coltopandas = ctab.colnames
# Pandas can't accomodate multi-column fields
coltopandas.remove('epars')
coltopandas.remove('eparssci')
coltopandas.remove('fpcoords_meas')
coltopandas.remove('fpcoords_comm')

cpd = ctab[coltopandas].to_pandas()

csl8th = fits.open(outputdir+f"obsid_498_ellipse_table.fits")
ctab8th  = Table(csl8th[1].data)



# cslc = fits.open(outputdir+f"obsid_CSL_00078_00553_ellipse_table.fits")
# ctabc  = Table(cslc[1].data)

# At hartmann
# csln = fits.open(outputdir+f"obsid_CSL_00080_00560_ellipse_table.fits")
# ctabn  = Table(csln[1].data)
#
# cslp = fits.open(outputdir+f"obsid_CSL_00080_00562_ellipse_table.fits")
# ctabp  = Table(cslp[1].data)
#
# # // MEC
# cslm = fits.open(outputdir+f"obsid_CSL_00080_00565_ellipse_table.fits")
# ctabm  = Table(cslm[1].data)
#
# # // BIP
# cslb = fits.open(outputdir+f"obsid_CSL_00080_00569_ellipse_table.fits")
# ctabb  = Table(cslb[1].data)
#
# # flat at hartmann level
# cslf = fits.open(outputdir+f"obsid_CSL_00080_00597_ellipse_table.fits")
# ctabf  = Table(cslf[1].data)
#
# # flat at LDO level
# cslfl = fits.open(outputdir+f"obsid_CSL_00080_00600_ellipse_table.fits")
# ctabfl  = Table(cslfl[1].data)
#
# # At LDO level, with LDO tilt
# csllt = fits.open(outputdir+f"obsid_CSL_00080_00606_ellipse_table.fits")
# ctablt  = Table(csllt[1].data)

# At hartmann
cslh = fits.open(outputdir+f"obsid_CSL_00084_00636_ellipse_table.fits")
ctabh  = Table(cslh[1].data)

# At Bolt
cslb = fits.open(outputdir+f"obsid_CSL_00084_00641_ellipse_table.fits")
ctabb  = Table(cslb[1].data)

# At Hartmann // BIP
cslhb = fits.open(outputdir+f"obsid_CSL_00084_00645_ellipse_table.fits")
ctahb  = Table(cslhb[1].data)

# At Hartmann // MEC
cslhm = fits.open(outputdir+f"obsid_CSL_00084_00647_ellipse_table.fits")
ctahm  = Table(cslhm[1].data)

# At Hartmann // LOS
cslhl = fits.open(outputdir+f"obsid_CSL_00084_00649_ellipse_table.fits")
ctahl  = Table(cslhl[1].data)

# Reproducibility Test
cslr0 = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel0.fits")
ctar0  = Table(cslr0[1].data)
cslr1 = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel1.fits")
ctar1  = Table(cslr1[1].data)
cslr2 = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel2.fits")
ctar2  = Table(cslr2[1].data)
cslr3 = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel3.fits")
ctar3  = Table(cslr3[1].data)
cslr4 = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel4.fits")
ctar4  = Table(cslr4[1].data)


# After Bolting #1
cslb1 = fits.open(outputdir+f"obsid_CSL_00086_00811_ellipse_table.fits")
ctabb1  = Table(cslb1[1].data)

# After Bolting #2
cslb1 = fits.open(outputdir+f"obsid_CSL_00086_00841_ellipse_table.fits")
ctabb1  = Table(cslb1[1].data)

# After FSS Installation
cslfss = fits.open(outputdir+f"obsid_CSL_00086_00847_ellipse_table.fits")
ctabfss  = Table(cslfss[1].data)

# CSL pre-final
csl99 = fits.open(outputdir+f"obsid_CSL_00088_00899_ellipse_table.fits")
ctab99  = Table(csl99[1].data)

# CSL last
csl90 = fits.open(outputdir+f"obsid_CSL_00088_00900_ellipse_table.fits")
ctab90  = Table(csl90[1].data)

# SRON EM 1 First
fsron = fits.open(outputdir+f"obsid_SRON_00041_02088_ellipse_table.fits")
sron  = Table(fsron[1].data)

# SRON EM 1 Vacuum
fsronvac = fits.open(outputdir+f"obsid_SRON_00042_02099_ellipse_table.fits")
sronvac  = Table(fsronvac[1].data)

# SRON EM 1 Ambient end of cold phase 1
fsronem1end = fits.open(outputdir+f"obsid_SRON_00048_02292_ellipse_table.fits")
sronem1end  = Table(fsronem1end[1].data)

# SRON EM 2 Ambient First
fsronem2start = fits.open(outputdir+f"obsid_SRON_00060_02441_ellipse_table.fits")
sronem2start  = Table(fsronem2start[1].data)

# SRON EM 2 Vacuum First attenuation 1.e-3
fsronem2vac = fits.open(outputdir+f"obsid_SRON_00060_02454_ellipse_table.fits")
sronem2vac  = Table(fsronem2vac[1].data)

# SRON EM 2 Vacuum First attenuation 3.e-4
fsronem2vac2 = fits.open(outputdir+f"obsid_SRON_00060_02464_ellipse_table.fits")
sronem2vac2 = Table(fsronem2vac2[1].data)

# SRON EM 2 cooldown
# fsronem2c0 = fits.open(outputdir+f"obsid_SRON_00060_    _ellipse_table.fits")
# sronem2vc0 = Table(fsronem2vac2[1].data)

ref,oref = ctab90, 900 # CSL last
ref,oref = sron,2088 # SRON EM 1 pre
ref,oref = sronem1end,2292 # SRON EM 1 post
ref,oref = sronvac,2099 # SRON EM 1 pre, vacuum
ref,oref = sronem2vac,2454 # SRON EM 2 vacuum
#meas,omeas = sronem1end,2292 # SRON EM 1 post
#meas,omeas = sronem2start,2441 # SRON EM 2 start
#meas,omeas = sronem2vac,2454 # SRON EM 2 vacuum att 1.e-3
meas,omeas = sronem2vac2,2464 # SRON EM 2 vacuum att 3.e-4

cv.stats((ref['ellsizesci'][valid_cubes(omeas)] - meas['ellsizesci'][valid_cubes(omeas)])*65)




from scipy.optimize import curve_fit
def sine_func(x, freq, amplitude, phase, offset):
    return np.sin(x * freq + phase) * amplitude + offset
def cosine_func(x, freq, amplitude, phase, offset):
    return np.cos(x * freq + phase) * amplitude + offset

def sine_funcfixf(x, amplitude, phase, offset):
    return np.sin(x * 2. * np.pi / 360. + phase) * amplitude + offset
def cosine_funcfixf(x, amplitude, phase, offset):
    return np.cos(x * 2. * np.pi / 360. + phase) * amplitude + offset

## FIT SINE WAVE, FIXING THE PERIOD TO 360 DEG
# p0=[guess_freq, guess_amplitude,
#     guess_phase, guess_offset]
p0 = [0.5, 0.5, 29.6]
#sinx = np.linspace(-180,180,361)
sinx = np.arange(-180,189,9.)
fitnf = curve_fit(sine_funcfixf, ctabn['phi_meas'][valid_cubes(560)], ctabn['ellsizesci'][valid_cubes(560)], p0=p0)
sinynf = sine_funcfixf(sinx, *fitnf[0])
fitmf = curve_fit(sine_funcfixf, ctabm['phi_meas'][valid_cubes(565)], ctabm['ellsizesci'][valid_cubes(565)], p0=p0)
sinymf = sine_funcfixf(sinx, *fitmf[0])
p0b = [0.25, 0.5, 26.]
fitbf = curve_fit(sine_funcfixf, ctabb['phi_meas'][valid_cubes(569)], ctabb['ellsizesci'][valid_cubes(569)], p0=p0b)
sinybf = sine_funcfixf(sinx, *fitbf[0])

p0b = [0.25, 0.5, 26.]
fithm = curve_fit(sine_funcfixf, ctahm['phi_meas'][valid_cubes(647)], ctahm['ellsizesci'][valid_cubes(647)], p0=p0b)
sinyhm = sine_funcfixf(sinx, *fithm[0])
fithl = curve_fit(sine_funcfixf, ctahl['phi_meas'][valid_cubes(649)], ctahl['ellsizesci'][valid_cubes(649)], p0=p0b)
sinyhl = sine_funcfixf(sinx, *fithl[0])


plt.figure("InPhiRadii2")

alpha = 1
plt.plot(ldophi8,ldosize8,c='k',marker='o',ls='-',label=f"LDO 8 deg")
#plt.plot(ctabc['phi_meas'][valid_cubes(553)],ctabc['ellsizesci'][valid_cubes(553)],c=lightblue,marker='o',ls='--',label="CSL 8 deg NEW")
#plt.plot(ctab8th['phi_meas'],ctab8th['ellsizesci'],c=orange,marker='o',ls='--',label="CSL 8 deg OLD")
plt.plot(ctabh['phi_meas'][valid_cubes(636)],ctabh['ellsizesci'][valid_cubes(636)],c=lightgreen,alpha=1.,marker='o',ls='--',label=r"Hartmann")
plt.plot(ctabb['phi_meas'][valid_cubes(641)],ctabb['ellsizesci'][valid_cubes(641)]+4.7,c=pink,alpha=alpha,marker='o',ls='--',label=r"Bolting Plane +4.7 (65um/pix)")
plt.plot(ctahb['phi_meas'][valid_cubes(645)],ctahb['ellsizesci'][valid_cubes(645)],c=pink,alpha=1,marker='o',ls='-',label=r"Hartmann-z, // to TOU_BIP")
plt.plot(ctahm['phi_meas'][valid_cubes(647)],ctahm['ellsizesci'][valid_cubes(647)],c=lightgray,alpha=alpha,marker='o',ls='--',label=r"Hartmann-z, // to TOU_MEC")
plt.plot(ctahl['phi_meas'][valid_cubes(649)],ctahl['ellsizesci'][valid_cubes(649)],c=orange,alpha=alpha,marker='o',ls='--',label=r"Hartmann-z, // to TOU_LOS")
#plt.plot(ctabn['phi_meas'][valid_cubes(560)],ctabn['ellsizesci'][valid_cubes(560)],c=lightgreen,alpha=alpha,marker='o',ls='--',label=r"CSL 8 deg NEW No $\theta$ corr")
# plt.plot(ctabm['phi_meas'][valid_cubes(565)],ctabm['ellsizesci'][valid_cubes(565)],c=lightgray,alpha=alpha,marker='o',ls='--',label=r"CSL 8 deg // to TOU_MEC")
# plt.plot(ctabb['phi_meas'][valid_cubes(569)],ctabb['ellsizesci'][valid_cubes(569)]+2,c=pink,alpha=alpha,marker='o',ls='--',label=r"CSL 8 deg // to BIP +2")
# plt.plot(ctabf['phi_meas'][valid_cubes(597)],ctabf['ellsizesci'][valid_cubes(597)],c=orange,alpha=alpha,marker='o',ls='--',lw=2,label=r"CSL 8 deg 'Flat' ")
# plt.plot(ctabfl['phi_meas'][valid_cubes(600)],ctabfl['ellsizesci'][valid_cubes(600)],c='r',alpha=1,marker='o',ls='--',lw=2,label=r"CSL 8 deg 'new TOU_MEC-flat' ")
#plt.plot(ctablt['phi_meas'][valid_cubes(606)],ctablt['ellsizesci'][valid_cubes(606)],c=brown,marker='o',ls='--',lw=2,label=r"CSL 12 deg 'ldo-tilt' ")
#plt.plot(cpd.phi_meas[sel_valid[obsid]],cpd.ellsizesci[sel_valid[obsid]],c=lightgray,marker='o',ls='--',label="CSL 8 deg")
plt.grid(alpha=0.25)
plt.legend(loc=(0.8,0.9))
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("Ellipse size [pix]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- TOU REMEAS",size=fsize+5)
#plt.ylim(26,38)
# plt.plot(sinx,sinynf,c=verylightgreen,marker='.',ls='--',alpha=alpha)#,label=r"CSL 8 deg NEW sinefit fix freq")
# plt.plot(sinx,sinymf,c=verylightgray,marker='.',ls='--',alpha=alpha)#,label=r"CSL 8 deg // TOU_MEC sinefit")
# plt.plot(sinx,sinybf+2.,c=(1, 0.75, 0.9),marker='.',ls='--',alpha=alpha)#,label=r"CSL 8 deg // TOU_BIP sinefit + 2.35")
plt.plot(sinx,sinyhm,c=lightgray,marker='.',ls='--',alpha=alpha)
plt.plot(sinx,sinyhl,c=lightorange,marker='.',ls='--',alpha=alpha)
plt.savefig(pngdir+f"em_ldo_compare_8_deg_after_TOU_remeasure_5obsids_inclfits.png")


x, y = ctabfl['phi_meas'][valid_cubes(600)],ctabfl['ellsizesci'][valid_cubes(600)]
f = interp1d(x,y,kind='linear')
csl_at_ldophis = f(ldophi8)

cv.stats(csl_at_ldophis-ldosize8)

x, y = ctabn['phi_meas'][valid_cubes(560)],ctabn['ellsizesci'][valid_cubes(560)]
f = interp1d(x,y,kind='linear')
csl_at_ldophis = f(ldophi8)

cv.stats((csl_at_ldophis-ldosize8)*65)



## REPRODUCIBILITY ANALYSIS
# At hartmann
cslh1 = fits.open(outputdir+f"obsid_CSL_00084_00636_ellipse_table.fits")
ctabh1  = Table(cslh1[1].data)
# Shifted by 1/2 pix in X
cslh2 = fits.open(outputdir+f"obsid_CSL_00084_00652_ellipse_table.fits")
ctabh2  = Table(cslh2[1].data)
# Shifted by 1/2 pix in X and Y
cslh3= fits.open(outputdir+f"obsid_CSL_00084_00654_ellipse_table.fits")
ctabh3  = Table(cslh3[1].data)


# At Hartmann -- 17 cycles --> 5 x 3 layers
allsizes = np.zeros([20,8],dtype=float)
alpha = 0.5
plt.figure("Cyc17")
for c in range(5):
    csl = fits.open(outputdir+f"obsid_CSL_00084_00656_ellipse_table_sel{c}.fits")
    ctab  = Table(csl[1].data)
    plt.plot(ctab['phi_meas'][valid_cubes(656)],ctab['ellsizesci'][valid_cubes(656)],c=colors[c],alpha=alpha,marker='o',ls='--',label=f"Hartmann Select {c}")
    allsizes[:,c] = ctab['ellsizesci'][valid_cubes(656)]
    del csl, ctab
plt.grid(alpha=0.25)
plt.legend(loc=(0.8,0.9))
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("Ellipse size [pix]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- Reproducibility ",size=fsize+5)
plt.savefig(pngdir+f"em_ldo_compare_8_deg_reproducibility_all.png")


alpha = 1

plt.figure("Reproducibility")
plt.plot(ctabh1['phi_meas'][valid_cubes(636)],ctabh1['ellsizesci'][valid_cubes(636)],c='k',alpha=alpha,marker='o',ls='--',label=r"Hartmann")
plt.plot(ctabh2['phi_meas'][valid_cubes(652)],ctabh2['ellsizesci'][valid_cubes(652)],c=gray,alpha=alpha,marker='o',ls='--',label=r"Hartmann +1/2 pix X")
plt.plot(ctabh3['phi_meas'][valid_cubes(654)],ctabh3['ellsizesci'][valid_cubes(654)],c=lightblue,alpha=alpha,marker='o',ls='--',label=r"Hartmann +1/2 pix X & Y")
plt.grid(alpha=0.25)
plt.legend(loc=(0.8,0.7))
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("Ellipse size [pix]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- Reproducibility: Pixelisation",size=fsize+5)
plt.savefig(pngdir+f"em_ldo_compare_8_deg_reproducibility_pixelisation.png")

allsizes[:,5] = ctabh1['ellsizesci'][valid_cubes(636)]
allsizes[:,6] = ctabh2['ellsizesci'][valid_cubes(652)]
allsizes[:,7] = ctabh3['ellsizesci'][valid_cubes(654)]

mallsizes = np.mean(allsizes,axis=1)
mallsizes.shape

resall = np.array([(allsizes[:,i] - mallsizes) for i in range(allsizes.shape[1])])

print("Reproducibity of the measures, incl. pixelisation")
print(f"{np.mean(resall,axis=0)} +- {np.std(resall,axis=0)}")
print(f"MEAN stddev     {np.mean(np.std(resall,axis=0)):.3f} pix, {np.mean(np.std(resall,axis=0))*65:.3f} microns")
print(f"MAX diff to avg {np.max(np.max(resall,axis=0)):.3f} pix, {np.max(np.max(resall,axis=0))*65:.3f} microns")


# SINE WAVE : rising at azimuth=(-phase), max at (-phase+90)
#  fitnf[0]  - obsid 560 -- Hartmann
#  array([-0.41318506,  0.68775039, 29.63897794]) : phase = np.rad2deg(0.68775039) = 39 : MIN = 51  (neg. amplitude -> MIN instead of MAX)
#  fitmf[0]  - obsid 565 -- // TOU_MEC
#  array([ 0.56283606, -0.16454535, 29.62898341]) : phase = np.rad2deg(-0.16454535) = -9 : MAX = 99
#  fitbf[0]  - obsid 569 -- // TOU_BIP
#  array([ 0.18232453, -0.12472319, 26.10129636]) : phase = np.rad2deg(-0.12472319) = -7  : MAX = 97

# fitmcf[0] - obsid 565
# array([-0.56283605,  1.40625097, 29.62898341]) : phase = np.rad2deg(1.40625097) =  80 : MIN : 80 (neg ampl.) --> MAX = 99  (-80+180)


"""
## FREE FIT --> ISSUE WITH THE FREQUENCY -- DOESN'T CORRESPOND TO 360 deg PERIOD
# p0=[guess_freq, guess_amplitude,
#     guess_phase, guess_offset]
p0 = [2*np.pi/360., 0.5, 0.5, 29.6]
#sinx = np.linspace(-180,180,361)
sinx = np.arange(-180,189,9.)
fitn = curve_fit(sine_func, ctabn['phi_meas'][valid_cubes(560)], ctabn['ellsizesci'][valid_cubes(560)], p0=p0)
sinyn = sine_func(sinx, *fitn[0])
plt.plot(sinx,sinyn,c=verylightgreen,marker='o',ls='--',label=r"CSL 8 deg NEW sinefit")
fitm = curve_fit(sine_func, ctabm['phi_meas'][valid_cubes(565)], ctabm['ellsizesci'][valid_cubes(565)], p0=p0)
sinym = sine_func(sinx, *fitm[0])
plt.plot(sinx,sinym,c=verylightgray,marker='o',ls='--',label=r"CSL 8 deg // TOU_MEC sinefit")
p0b = [2*np.pi/360., 0.25, 0.5, 26.]
fitb = curve_fit(sine_func, ctabb['phi_meas'][valid_cubes(569)], ctabb['ellsizesci'][valid_cubes(569)], p0=p0b)
sinyb = sine_func(sinx, *fitb[0])
plt.plot(sinx,sinyb+2.35,c=(1, 0.75, 0.9),marker='o',ls='--',label=r"CSL 8 deg // TOU_BIP sinefit + 2.35")

#  fitn[0]  - obsid 560 -- Hartmann
# array([ 1.51425169e-02, -4.20169614e-01,  7.59369801e-01,  2.96801908e+01])  # phase np.rad2deg(7.59369801e-01) = 43.509 : MAX 133   FREQ 2*np.pi/1.51425169e-02 = 414 deg
#  fitm[0]  - obsid 565 -- // TOU_MEC
# array([ 1.83214136e-02,  5.78452326e-01, -1.49847698e-01,  2.96236288e+01])  # phase np.rad2deg(-1.49847698e-01) = -8.687 deg : MAX 81   FREQ 2*np.pi/1.83214136e-02 = 342 deg
#  fitb[0]  - obsid 569 -- // TOU_BIP
#array([ 2.03193068e-02,  2.06731065e-01, -5.61072302e-02,  2.60982806e+01])  # phase np.rad2deg(-5.61072302e-02) = -3.2147 deg : MAX 87   FREQ 2*np.pi/2.03193068e-02 =  309 deg
"""





ctab  = ctabf
fpcoords_meas = ctab["fpcoords_meas"]
pars_meas, circle_meas = cv.fitCircle(fpcoords_meas[valid_cubes(560),:])  # kick the NaNs out!!
cenx_meas,ceny_meas,radius_meas = pars_meas
distxy = np.sqrt(cenx_meas**2. + ceny_meas**2)
print(f"{cenx_meas:.4f} {ceny_meas:.4f} {distxy:.4f}")





"""
plt.figure("InPhiRadii")
plt.plot(ldophi16,ldosize16,c=lightgray,marker='o',ls='-',label=f"LDO 16 deg")
plt.plot(ldophi12,ldosize12,c=gray,marker='o',ls='-',label=f"LDO 12 deg")
plt.plot(ldophi8,ldosize8,c=lightblue,marker='o',ls='-',label=f"LDO 8 deg")
plt.plot(ldophi3,ldosize3,c='k',marker='o',ls='-',label=f"LDO 3 deg")
plt.plot(ctab16['phi_meas'][sel_valid[hobsids[16]]],ctab16['ellsizesci'][sel_valid[hobsids[16]]],c=lightgray,marker='o',ls='--',label="CSL 16 deg")
plt.plot(ctab12['phi_meas'][sel_valid[hobsids[12]]],ctab12['ellsizesci'][sel_valid[hobsids[12]]],c=gray,marker='o',ls='--',label="CSL 12 deg")
plt.plot(ctab8['phi_meas'][sel_valid[hobsids[8]]],ctab8['ellsizesci'][sel_valid[hobsids[8]]],c=lightblue,marker='o',ls='--',label="CSL 8 deg")
plt.plot(ctab3['phi_meas'][sel_valid[hobsids[3]]],ctab3['ellsizesci'][sel_valid[hobsids[3]]],c='k',marker='o',ls='--',label="CSL 3 deg")
#plt.plot(ctab16t['phi_meas'][sel_valid[hobsidst[16]]],ctab16t['ellsizesci'][sel_valid[hobsidst[16]]],c=lightgray,marker='o',ls='--',label=r"CSL 16 w/ $\theta$ corr")
plt.plot(ctab12t['phi_meas'][sel_valid[hobsidst[12]]],ctab12t['ellsizesci'][sel_valid[hobsidst[12]]],c=gray,marker='o',ls=':',label=r"CSL 12 w/ $\theta$ corr")
plt.plot(ctab8t['phi_meas'][sel_valid[hobsidst[8]]],ctab8t['ellsizesci'][sel_valid[hobsidst[8]]],c=lightblue,marker='o',ls=':',label=r"CSL 8 w/ $\theta$ corr")
#plt.plot(ctab3t['phi_meas'][sel_valid[hobsidst[3]]],ctab3t['ellsizesci'][sel_valid[hobsidst[3]]],c='k',marker='o',ls='--',label=r"CSL 3 w/ $\theta$ corr")
plt.grid(alpha=0.25)
plt.legend()
plt.xlabel("Azimuth $[^\circ]$",size=fsize)
plt.ylabel("Ellipse size [pix]",size=fsize)
plt.title(f"Ellipse size vs azimuth",size=fsize)
plt.ylim(26,38)
plt.savefig(pngdir+"em_ldo_compare_ellipse_size_bckgndsub_yen_centroid_binned2x2_reference_vs_phi_absolute_incl_csl_with_thetacorr_812.png")
"""





"""
# BRING BOTH IN LINE
lselok = np.where(np.isfinite(cpd.theta_meas))[0]
selok = lselok
len(selok)

# for ct, lt, cp, lp in zip(cpd.theta_meas[selok], lpds.theta_meas[selok], cpd.phi_meas[selok], lpds.phi_meas[selok]):
#     print(f"[{ct:6.3f},{lt:6.3f}]   [{cp:8.3f}  {lp:8.3f}]")

cpdk = cpd.loc[selok]
lpdk = lpds.loc[selok]

c=0
for ct, lt, cp, lp in zip(cpdk.theta_meas, lpdk.theta_meas, cpdk.phi_meas, lpdk.phi_meas):
    print(f"{c:2d}  [{ct:6.3f},{lt:6.3f}]   [{cp:8.3f}  {lp:8.3f}]")
    c+=1

# Normally the two dataframes are in line --> the selections should be identical
csel3 = (cpdk.theta_meas<4)
csel8 = (cpdk.theta_meas>6) & (cpdk.theta_meas<10)
csel12 = (cpdk.theta_meas>10) & (cpdk.theta_meas<14)
csel16 = (cpdk.theta_meas>14)
lsel3 = (lpdk.theta_meas<4)
lsel8 = (lpdk.theta_meas>6) & (lpdk.theta_meas<10)
lsel12 = (lpdk.theta_meas>10) & (lpdk.theta_meas<14)
lsel16 = (lpdk.theta_meas>14)
print(np.allclose(lsel3, csel3))
print(np.allclose(lsel8, csel8))
print(np.allclose(lsel12, csel12))
print(np.allclose(lsel16, csel16))
s3,s8,s12,s16 = csel3,csel8,csel12,csel16
"""


# CSL Hartmann tests - measured tilts:
# rxn,ryn = rxry_to_flat(ctabn['phi_meas'][valid_cubes(560)], ctabn['ellsizesci'][valid_cubes(560)], guesspars = [0.5, 0.5, 29.6], radiusmm=36., mmperpix = 0.065)
# rxm,rym = rxry_to_flat(ctabm['phi_meas'][valid_cubes(565)], ctabm['ellsizesci'][valid_cubes(565)], guesspars = [0.5, 0.5, 29.6], radiusmm=36., mmperpix = 0.065)
# rxb,ryb = rxry_to_flat(ctabb['phi_meas'][valid_cubes(569)], ctabb['ellsizesci'][valid_cubes(569)], guesspars = [0.5, 0.5, 29.6], radiusmm=36., mmperpix = 0.065)

print("TOU MEC to 'flat curve':")
rxhm,ryhm, normalhm, tilthm, pmaxhm, gammhm, parsm = rxry_to_flat(ctahm['phi_meas'][valid_cubes(647)], ctahm['ellsizesci'][valid_cubes(647)], guesspars = [0.5, 0.5, 29.6], radiusmm=36., mmperpix = 0.065)
print(f"tilt : {tilthm} = {np.rad2deg(gammhm)*60}")

print("TOU LOS to 'flat curve':")
rxhl,ryhl, normalhl, tilthl, pmaxhl, gammhl, parsl = rxry_to_flat(ctahl['phi_meas'][valid_cubes(649)], ctahl['ellsizesci'][valid_cubes(649)], guesspars = [0.5, 0.5, 29.6], radiusmm=36., mmperpix = 0.065)
print(f"tilt : {tilthl} = {np.rad2deg(gammhl)*60}")







alpha = 1

plt.figure("InPhiBolt")
plt.plot(ctabb['phi_meas'][valid_cubes(641)],ctabb['ellsizesci'][valid_cubes(641)],c=pink,alpha=alpha,marker='o',ls='--',label=r"Pre-Bolting")
plt.plot(ctabb1['phi_meas'][valid_cubes(841)],ctabb1['ellsizesci'][valid_cubes(841)],c='r',alpha=alpha,marker='o',ls='--',label=r"Post-Bolting")
plt.plot(ctabfss['phi_meas'][valid_cubes(847)],ctabfss['ellsizesci'][valid_cubes(847)],c='g',alpha=alpha,marker='o',ls='--',label=r"FSS installed")
plt.plot(ctab99['phi_meas'][valid_cubes(899)],ctab99['ellsizesci'][valid_cubes(899)],c=gray,alpha=alpha,marker='o',ls='--',label=r"CSL (899)")
plt.plot(ctab90['phi_meas'][valid_cubes(900)],ctab90['ellsizesci'][valid_cubes(900)],c='k',alpha=alpha,marker='o',ls='--',label=r"CSL Final (900)")
plt.grid(alpha=0.25)
plt.legend(loc=(0.8,0.9))
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("Ellipse size [pix]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- Pre-Post Bolting #2 -- FSS installed",size=fsize+5)
plt.savefig(pngdir+f"em_ldo_compare_8_deg_bolting_pre-post_bolting_2_FSS.png")

plt.figure("InPhiBolt")
plt.plot(ctab90['phi_meas'][valid_cubes(900)],ctab90['ellsizesci'][valid_cubes(900)],c='k',alpha=alpha,marker='o',ls='--',label=r"CSL Final (900)")
plt.plot(sron['phi_meas'][valid_cubes(2088)],sron['ellsizesci'][valid_cubes(2088)],c='r',alpha=alpha,marker='o',ls='--',label=r"SRON EM1 start (2088)")
plt.plot(sronvac['phi_meas'][valid_cubes(2099)],sronvac['ellsizesci'][valid_cubes(2099)],c=orange,alpha=alpha,marker='o',ls='--',label=r"SRON EM1 vacuum (2099)")
plt.plot(sronem1end['phi_meas'][valid_cubes(2292)],sronem1end['ellsizesci'][valid_cubes(2292)],c=pink,alpha=alpha,marker='o',ls='--',label=r"SRON EM1 end (2292)")
plt.plot(sronem2start['phi_meas'][valid_cubes(2441)],sronem2start['ellsizesci'][valid_cubes(2441)],c='b',alpha=alpha,marker='o',ls='--',label=r"SRON EM2 start (2441)")
plt.plot(sronem2vac['phi_meas'][valid_cubes(2454)],sronem2vac['ellsizesci'][valid_cubes(2454)],c=gray,alpha=alpha,marker='o',ls='--',label=r"SRON EM2 vacuum att 1e-3 (2454)")
plt.plot(sronem2vac2['phi_meas'][valid_cubes(2464)],sronem2vac2['ellsizesci'][valid_cubes(2464)],c=lightgray,alpha=alpha,marker='o',ls='--',label=r"SRON EM2 vacuum att 3e-4 (2464)")
plt.grid(alpha=0.25)
plt.legend(loc=(0.6,0.3), fontsize=fsize)
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("Ellipse size [pix]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- CSL-OUT vs SRON EM1 EM2",size=fsize+5)
plt.savefig(pngdir+f"em_compare_csl_out_sron_in_csl_900_sron_2088_2099_2292_2441_2454_2464.png")
plt.ylim(23.6,24.8)
plt.legend(loc=(0.65,0.71), fontsize=fsize-2)
plt.savefig(pngdir+f"em_compare_csl_out_sron_in_csl_900_sron_2088_2099_2292_2441_2454_zoom.png")
plt.legend(loc=(0.7, 0.3), fontsize=fsize-2)
plt.legend(loc=(0.75,0.65), fontsize=fsize-2)
plt.savefig(pngdir+f"em_compare_csl_out_sron_in_csl_900_sron_2088_2099_2292_2441_2454__2464_zoom.png")



# Post - pre bolting (bolting #1 2021 10 07)
dbolt1 = ctabb1['ellsizesci'][valid_cubes(811)] - ctabb['ellsizesci'][valid_cubes(641)]
plt.figure("InPhiBoltDiff")
plt.plot(ctabb1['phi_meas'][valid_cubes(811)],dbolt1*65,c='r',alpha=alpha,marker='o',ls='--',label="Post-Pre Bolting [$\mu$m]")
plt.grid(alpha=0.25)
plt.legend(loc=(0.8,0.9))
plt.xlabel("Azimuth $[^\circ]$",size=fsize+5)
plt.ylabel("$\delta\Sigma$ = $\delta$Ellipse size [$\mu$m]",size=fsize+5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- Diff Post-Pre Bolting #2",size=fsize+5)
plt.savefig(pngdir+f"em_ldo_compare_8_deg_bolting_diff_post-pre_bolting_2.png")

cv.stats(dbolt1)



for i in range(20):
    #print (f"{i} {ctabb1['phi_meas'][valid_cubes(841)][i]:.3f}, {ctabfss['phi_meas'][valid_cubes(847)][i]:.3f}")
    print (f"{i} {angles_comm[i,1]:.3f}, {ctabfss['phi_meas'][valid_cubes(847)][i]:.3f}")


cv.stats((ctabfss['ellsizesci'][valid_cubes(847)] - ctabb1['ellsizesci'][valid_cubes(841)])*65.)



filenames = cv.fileSelect([f'{sobsid}_','fits'],location=datadir+obsidir)
cv.print1(filenames)
ffilenames = [datadir + obsidir + filename for filename in filenames]


alpha = 1
plt.figure("InPhiBolt",figsize=(12,12))
plt.plot(ctab90['phi_meas'][valid_cubes(900)],ctab90['ellsizesci'][valid_cubes(900)],c='k',alpha=alpha,marker='o',ls='-',label=r"CSL Final (900)")
plt.plot(sron['phi_meas'][valid_cubes(2088)],sron['ellsizesci'][valid_cubes(2088)],c='r',alpha=alpha,marker='o',ls='-',label=r"SRON 1 atm (2088)")
plt.plot(sronvac['phi_meas'][valid_cubes(2099)],sronvac['ellsizesci'][valid_cubes(2099)],c=orange,alpha=alpha,marker='o',ls='-',label=r"SRON vacuum (2099)")

c = 0
for obsid in [2107, 2109, 2111, 2113, 2115, 2117, 2119, 2121,2123, 2125, 2128]:#, 2131]:
    c+=1
    resultfiles = cv.fileSelect([f'{obsid}_', 'table.fits'], location=outputdir)
    resulthdu = fits.open(outputdir+resultfiles[0])
    rtab  = Table(resulthdu[1].data)

    plt.plot(rtab['phi_meas'][valid_cubes(obsid)],rtab['ellsizesci'][valid_cubes(obsid)],c=colors[c%len(colors)],alpha=alpha,marker='o',ls='--',label=f"Cooldown {obsid=}")

plt.grid(alpha=0.25)
plt.legend(loc=(-0.1, 0.75), fontsize=10)
plt.xlabel("Azimuth $[^\circ]$", size=fsize + 5)
plt.ylabel("Ellipse size [pix]", size=fsize + 5)
plt.title(f"Ellipse size vs azimuth\n8 degrees -- SRON COOL DOWN", size=fsize + 5)
plt.savefig(pngdir + f"em_compare_csl_out_sron_in_csl_900_sron_cooldown.png")










#################  OBS BASED  #######################


obsid = 2423

download_observation(obsid=obsid, selection='cube', setup=41, em1=True)
download_observation(obsid=obsid)

obs = Observation(obsid=obsid)

obs.print_cube_shapes(2)

cv.print1(obs.get_filenames_cubes())

hduc = obs.get_cube_hdu(1)

hduc.info()

for n in range(len(obs.get_filenames_cubes())):
    hduc = obs.get_cube_hdu(n, verbose=False)
    print(f"{n:2d} : [{hduc[2].header['CRPIX1']}, {hduc[2].header['CRPIX2']}]")







#################  COOLDOWN PHASE -- MULTI OBSID -- TEMPERATURE  #######################


obsid = 2493
sobsid = str(obsid).zfill(5)

obs = Observation(obsid)

obs.get_hk_devices()

device = "SYN-HK"
obs.get_hk_names(device=device)

keys = ["GSYN_TRP1", "GSYN_TRP8"]
hkc = obs.get_hk_per_cube(device=device,keys=keys,outputfile=None,decimals=6,func=np.nanmean)

hkc.colnames
hkc["finetime"]

t0 = hkc['finetime'][0]
reltime = hkc['finetime'] - t0

resultfile = cv.fileSelect([f'{sobsid}', 'table.fits'], location=resultdir)[0]

obsh = fits.open(resultdir+resultfile)
obstab  = Table(obsh[1].data)
obstab.colnames
obstab["ellsize"]

########################################################################################################################
device = "SYN-HK"
keys = ["GSYN_TRP1", "GSYN_TRP8"]

obsids = [2487,2493,2494]
obsids.extend([i for i in range(2500,2518)])
obsids = [i for i in range(2500,2521)]
nobs = len(obsids)

trp1s = []
trp8s = []
ellsizes = []
reltimes = []

doPlot=1
if doPlot:
    plt.figure("Cooldown")

for c,obsid in enumerate(obsids):
    sobsid = str(obsid).zfill(5)

    ## EXTRACT HK / CUBE
    obs = Observation(obsid)
    hkc = obs.get_hk_per_cube(device=device,keys=keys,outputfile=None,decimals=6,func=np.nanmean)

    ncubes = len(hkc)

    if c==0:
        t0 = hkc["finetime"][0]


    ## READ RESULT TABLE FROM THE HARTMANN PATTERN ANALYSIS
    resultfile = cv.fileSelect([f'{sobsid}', 'table.fits'], location=resultdir)[0]
    obsh = fits.open(resultdir + resultfile)
    obstab = Table(obsh[1].data)

    obstab.colnames

    if len(obstab["ellsizesci"]) != ncubes:
        print(f"ERROR: NB CUBES MISMATCH BETWEEN RESULT TABLE AND HK DATA FOR OBSID {obsid}")
        break

    trp1 = hkc["GSYN_TRP1"]
    trp8 = hkc["GSYN_TRP8"]
    ellsize = obstab["ellsizesci"]
    reltime = hkc["finetime"]-t0

    reltimes.extend(reltime)
    trp1s.extend(trp1)
    trp8s.extend(trp8)
    ellsizes.extend(ellsize)

    if doPlot:
        plt.plot(trp8, ellsize, c=colors[c%len(colors)], label=f"{obsid} - <TRP8> {np.mean(trp8):6.2f}")


sel = np.where(np.isfinite(ellsizes))
trp1s = np.array(trp1s)[sel]
trp8s = np.array(trp8s)[sel]
reltimes = np.array(reltimes)[sel]
ellsizes = np.array(ellsizes)[sel]

xs,ys = trp8s, ellsizes

x_ext = np.linspace(20, -120, 141)

# ORDER 1
fitpars,yfit,model = cv.mypolyfit(xs,ys,order=1)
y_ext = model(x_ext)
#focus = cv.allRoots(x_ext,y_ext)[0]
focus1 = allRoots(x_ext,y_ext)[0]
plt.plot(xs, yfit, c=lightgray, ls='--', alpha=0.5, label=f"Extrapolated focus 1st {focus1:7.2f}")

# ORDER 2
fitpars2,yfit2,model2 = cv.mypolyfit(xs,ys,order=2)
y_ext2 = model2(x_ext)
#focus = cv.allRoots(x_ext,y_ext)[0]
focus2 = allRoots(x_ext,y_ext2)[0]
#plt.plot(xs, yfit2, c=lightgreen, ls='--', alpha=0.5, label=f"Extrapolated focus 2nd {focus2:7.2f}")

# 1 fit / position  !!! TODO : TAKE CARE FOR THE MISSING DATAPOINTS -- THIS ASSUMES ALL ARRAYS ARE FULL (20 MEAS)
focii = np.zeros(20)
order = 1
for j in range(1,20):
    fitpars, yfit, model = cv.mypolyfit(xs[i::nobs], ys[i::nobs], order=order)
    y_ext = model(x_ext)
    # focus = cv.allRoots(x_ext,y_ext)[0]
    focus = allRoots(x_ext, y_ext)[0]
    focii[i] = focus
cv.stats(focii)

fsize = 14
plt.xlabel("TRP8",size=fsize)
plt.ylabel("Size of Harmann ellipse [pix]",size=fsize)
plt.title("Cooldown",size=fsize)
plt.grid(alpha=0.2)
plt.legend(loc=(0.8,0.3),fontsize=fsize-5)
plt.xlim(np.max(xs)+1, np.min(xs)-1)
plt.savefig(pngdir+"sron_em2_cooldown_hartmann_vs_TRP8_2500_2520.png")

# ---



""" --> convenience
def allRoots(x, y, rootfunction=None):
    ""
    SYNTAX
    xroots = allRoots(x,y, rootfunction=<rootfunction>)

    PURPOSE
    Find all roots (y=0) in a tabulated function (x,y)

    INPUTS
    x,y : input function
    rootfunction : any root-finding function from scipy.optimize.zeros (default = ridder)

    OUTPUT
    The x-values of the roots
    ""
    import numpy as np
    from scipy.interpolate import interp1d
    from scipy.optimize.zeros import ridder

    if rootfunction is None:
        rootfunction = ridder

    #
    # Build an interpolator over the input data
    f = interp1d(x, y, kind='linear')
    #
    # Select segments where the sign is changing
    idx = np.where((y * np.roll(y, 1))[1:] <= 0.)[0]
    #
    # Compute the position of the root in every segment
    # The unique function is applied to be robust vs segments at y=0.
    return np.unique(np.array([rootfunction(f, x[i], x[i + 1]) for i in idx]))
"""

np.allclose(trp1s, trp8s)


