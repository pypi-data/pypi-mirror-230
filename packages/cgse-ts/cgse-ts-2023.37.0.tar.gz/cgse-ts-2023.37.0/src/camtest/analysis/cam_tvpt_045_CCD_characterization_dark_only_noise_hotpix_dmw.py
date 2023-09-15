# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 12:27:02 2021

@author: dmw
"""

#A Dave Walton (UCL/MSSL) program to look at FITs files,
#in particular for Plato.
#Can be tweaked to tinker with images.


import fnmatch
import os

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

#File picker widget
#root=tk.Tk()
#flPathNam=filedialog.askopenfilename(initialdir='c:/', title='Open File',
#      filetypes=(('fits', '*.fits'), ('All Files', '*.*')))
#root.destroy()

fRootwo=np.sqrt(2.0)

#EM1
flPath=["d:/plato/em1_spring_2021/18_06_2021/Image_data_fits/long_dark",
        "d:/plato/em1_spring_2021/17_06_2021/Image_data_fits/long_dark"]
dateString=['2021_06_18', '2021_06_17']
lsFlNum=['ID12670_E_image_1', 'ID12011_E_image_1']

flPath0=["d:/plato/qm1/Tests_QM_qualification_Tests_7_10_2021_performed_on_plastic_NFEE/"]
flPath1=["Test1/Repeat_for_Yves/Test1_c_inj_70p_baseline_FPA_ccd2/With_Both_ON"]
lsFlNum=['ID15634', 'ID15635']  #Strings only needs to be long enough to uniquely identify the file(s)

flPath0=["d:/plato/em1_spring_2021/16_06_2021/image_data_fits/linearity_well/"]
flPath1=["ccd1e"]
lsFlNum=['ID11686', 'ID11711']  #Strings only needs to be long enough to uniquely identify the file(s)

flPath01=flPath0[0] + flPath1[0]
wNFile=len(lsFlNum)

#if wNFile & 1:
#    print("Bailing due to odd number of files")
#    raise SystemExit(0)
#wNPair=np.int(wNFile//2)  #// is round-down integer division
    
waIndex=np.arange(wNFile)

faPreUnInjMean=np.empty(wNFile)
faPostUnInjMean=np.empty(wNFile)
faPreInjMean=np.empty(wNFile)
faPostInjMean=np.empty(wNFile)
faImUnInjMean=np.empty(wNFile)
faPreUnInjStDev=np.empty(wNFile)
faPostUnInjStDev=np.empty(wNFile)
faPreInjStDev=np.empty(wNFile)
faPostInjStDev=np.empty(wNFile)
faImUnInjStDev=np.empty(wNFile)

faDiffPreUnInjMean=np.empty(wNFile)
faDiffPostUnInjMean=np.empty(wNFile)
faDiffPreInjMean=np.empty(wNFile)
faDiffPostInjMean=np.empty(wNFile)
faDiffImUnInjMean=np.empty(wNFile)
faDiffPreUnInjStDev=np.empty(wNFile)
faDiffPostUnInjStDev=np.empty(wNFile)
faDiffPreInjStDev=np.empty(wNFile)
faDiffPostInjStDev=np.empty(wNFile)
faDiffImUnInjStDev=np.empty(wNFile)

#Bright=[]*3  #List of bright defects
flNamExt=['']*wNFile
flNam=['']*wNFile
waSize=[wNFile, 0, 0] #For PTC, 2 frames of size [., y, x]
for wJ in waIndex:
  #for wI in range(2):
    #wK=wJ       #*2+wI
    os.chdir(flPath01)
    files=os.listdir()
    #wK=wJ*2+wI
    #wI=wJ
    flNamExt[wJ]=fnmatch.filter(files, lsFlNum[wJ]+'*.fits')[0]
    flNam, flExt=os.path.splitext(flNamExt[wJ])
    #efPosn=flNam.find('_')+1
    #ef=flNam[efPosn:(efPosn+1)]
    #print('\n\n',lsFlNum[wK], ef) #, flNamExt[wI])
 
    with fits.open(flNamExt[wJ], mode='denywrite') as hdulist:  #hdulist is a list of the HDUs
      if len(hdulist)==1: hduImage=hdulist[0]  #If a 'simple' single HDU file.
      else:
        hdu0=hdulist[0]
        hduImage=hdulist[1]  #Use 0 if it's a 'simple' image file,
        # 1 if the fits has a hierarchical structure (i.e. a short master header then
        # one or more images (each in an HDU)). Plato files (usually) use [1].
        #See https://docs.astropy.org/en/stable/io/fits/ for details.
      if wJ==0:
        hdulist.info()  #Prints the hdulist. For this file, hduist[0] is the top-level HDU
        waSize[1]=hduImage.header['NAXIS2']  #Y
        waSize[2]=hduImage.header['NAXIS1']  #X
        uaAll=np.empty((waSize), dtype=np.uint16)

      
      ExtName=hduImage.header['EXTNAME']  #Needed for image number
      Mirror=hduImage.header['MIRROR']  #'E' or 'F'
      T1_C2DegC=hduImage.header['T1_C2']  #T CCD2
      READ_ORD=hduImage.header['READ_ORD']
      
      
      uaAll[wJ, :, :]=np.uint16(hduImage.data+0.5)  #Ensures it's read as a uint rather than e.g. float.
      hdulist.close()

    if  Mirror!= '0': uaAll[wJ, :, :]=np.fliplr(uaAll[wJ, :, :])

    uaPre=uaAll[:, :, 20:25]
    uaPreMeanCol=np.mean(uaPre, axis=2)  #Form an average col per frame
    uaSOver=uaAll[:, :, 2289:2294] #Ignore final pix, which has a different offset due to different clock edges.
    uaSOverMeanCol=np.mean(uaSOver, axis=2)  #Form an average col per frame
    faOffsetMeanCol=(np.mean(uaPreMeanCol, axis=0) + np.mean(uaSOverMeanCol, axis=0))/2.0

    titleString= lsFlNum[wJ] + ' '

  
    #Display the raw images
    fig0, ax = plt.subplots(num=flNamExt[wJ]) #Create a window/framework for a plot
    ax.set(title=flNamExt[wJ])
    uZMin0=np.amin(uaAll[wJ, :, :]) ; uZMax0=np.amax(uaAll[wJ, :, :])
    plt.imshow(uaAll[wJ, :, :], origin='lower', vmin=uZMin0, vmax=uZMax0)  #Also works for PIL image. #ax.set(title='Fig B')
    plt.colorbar()
    #plt.savefig('c:/home/dmw/plato/em2_oct2020/' + flNam)
    
    #Calculate Mean and Noise for different areas
    #Following y co-ords work forChInj=99, Gap=99 images.
    #X serial overscan (called 'Post' below) coords:
    #  EM1 CCDs are early manufacture, with poor serial CTE.
    #  So injected images have charge spreading into the serial overscans.
    #  Serial Overscans are X=2280 onwards, but charge and NFEE effects affect up to
    #  the first 6 pixels. Also the last pixel is affected by NFEE clocks, so for
    #  noise measurements, leave out these pixels with systematics.
    faPreUnInjMean[wJ]=np.mean(uaAll[wJ, 2280:2360, 12:24])
    faPostUnInjMean[wJ]=np.mean(uaAll[wJ, 2280:2360, 2286:2294])  #Skip last col
    faImUnInjMean[wJ]=np.mean(uaAll[wJ, 2280:2360, 1125:1225])
    faPreInjMean[wJ]=np.mean(uaAll[wJ, 2180:2260, 12:24])
    faPostInjMean[wJ]=np.mean(uaAll[wJ, 2180:2260, 2286:2294])  #Skip last col
    
    faPreUnInjStDev[wJ]=np.std(uaAll[wJ, 2280:2360, 12:24], ddof=1)  #Skip last col
    faPostUnInjStDev[wJ]=np.std(uaAll[wJ, 2280:2360, 2286:2294], ddof=1)  #Skip last col
    faImUnInjStDev[wJ]=np.std(uaAll[wJ, 2280:2360, 1125:1225], ddof=1)
    faPreInjStDev[wJ]=np.std(uaAll[wJ, 2180:2260, 12:24], ddof=1)
    faPostInjStDev[wJ]=np.std(uaAll[wJ, 2180:2260, 2286:2294], ddof=1)  #Skip last col

    print(lsFlNum[wJ])
    print('Prescan  UnInj Mean, StDev', faPreUnInjMean[wJ], faPreUnInjStDev[wJ])
    print('Overscan UnInj Mean, StDev', faPostUnInjMean[wJ], faPostUnInjStDev[wJ])
    print('Image UnInj Mean, StDev', faImUnInjMean[wJ], faImUnInjStDev[wJ])
    print('Prescan  Inj Mean, StDev', faPreInjMean[wJ], faPreInjStDev[wJ])
    print('Overscan Inj Mean, StDev', faPostInjMean[wJ], faPostInjStDev[wJ])
    print('\n')
    
    
    #Find bright defect pixels.
    #For an image with charge injection, only do this for uninjected rows.
    fT1_C2DegC=float(T1_C2DegC)
    

#Calculate and print noise values
if wNFile > 1:
    laDiff=uaAll[1].astype('int32') - uaAll[0]
    lDiffMean=np.mean(laDiff) ; lDiffStDev=np.std(laDiff)
    fig0, ax = plt.subplots(num='DIFF') #Create a window/framework for a plot
    ax.set(title=lsFlNum[1] + ' - ' + lsFlNum[0])
    #lZMin0=np.amin(laDiff) ; lZMax0=np.amax(laDiff)
    lZMin0=lDiffMean-1.5*lDiffStDev ; lZMax0=lDiffMean+1.5*lDiffStDev
    plt.imshow(laDiff, origin='lower', vmin=lZMin0, vmax=lZMax0)  #Also works for PIL image. #ax.set(title='Fig B')
    plt.colorbar()
    
    #Calculate Mean and Noise for different areas of laDiff
    #Following co-ords work forChInj=99, Gap=99 images.
    faDiffPreUnInjMean=np.mean(laDiff[2280:2360, 12:24])
    faDiffPostUnInjMean=np.mean(laDiff[2280:2360, 2286:2294])  #Skip last col
    faDiffImUnInjMean=np.mean(laDiff[2280:2360, 1125:1225])
    faDiffPreInjMean=np.mean(laDiff[2180:2260, 12:24])
    faDiffPostInjMean=np.mean(laDiff[2180:2260, 2286:2294])  #Skip last col

    #Divide StDevs by sqrt(2) to make them comparable with single frame values
    faDiffPreUnInjStDev=np.std(laDiff[2280:2360, 12:24], ddof=1)/fRootwo
    faDiffPostUnInjStDev=np.std(laDiff[2280:2360, 2286:2294], ddof=1)/fRootwo  #Skip last col
    faDiffImUnInjStDev=np.std(laDiff[2280:2360, 1125:1225], ddof=1)/fRootwo
    faDiffPreInjStDev=np.std(laDiff[2180:2260, 12:24], ddof=1)/fRootwo
    faDiffPostInjStDev=np.std(laDiff[2180:2260, 2286:2294], ddof=1)/fRootwo  #Skip last col
    
    
    print('\nDiff')
    print('Prescan  UnInj Mean, StDev', faDiffPreUnInjMean, faDiffPreUnInjStDev)
    print('Overscan UnInj Mean, StDev', faDiffPostUnInjMean, faDiffPostUnInjStDev)
    print('Image    UnInj Mean, StDev', faDiffImUnInjMean, faDiffImUnInjStDev)
    print('Prescan  Inj Mean, StDev', faDiffPreInjMean, faDiffPreInjStDev)
    print('Overscan Inj Mean, StDev', faDiffPostInjMean, faDiffPostInjStDev)


#Find bright defect pixels
fTintStaticSec=2.25  #For these particular images
fThresholdEPerSec=10.0  #From CCD Reqmts
fThresholdE=fThresholdEPerSec*fTintStaticSec
fEPerAdu=26.0  #Approx from EM1 Photon Transfer Curves
fThresholdAdu=fThresholdE/fEPerAdu
if fThresholdAdu < 6.0:
  fThresholdAdu=6.0  #Approx practical lower limit
  print('\nHot Pixel threshold used is default minimum (ADU) = ', fThresholdAdu, '\n')
else:
  print('\nHot Pixel threshold used is default minimum (ADU) = ', fThresholdAdu, '\n')


#Go through 1st image looking for bright pixels above the local mean
#Using 3x3 block means the edge pixels can't be used.
waBrightMap0=np.zeros([waSize[1], waSize[2]], dtype=int)  
for wL in range(500, 4509):  #For the sample images tried, rows below 500 are saturated from previous frame.
  if (wL//100)*100 == wL: print(wL)
  for wK in range(26, 2279):
    fLocalMean=(np.sum(uaAll[0, (wL-1):(wL+2), (wK-1):(wK+2)])-uaAll[0, wL, wK])/8.0
    fExcess=uaAll[0, wL, wK] -fLocalMean
    if fExcess >= fThresholdAdu: waBrightMap0[wL, wK]=1

wNBright0=np.sum(waBrightMap0)
whereBright0=np.where(waBrightMap0==1)

print('After Frame0, wNBright= ', wNBright0)

#Display the Frame0 map
fig0, ax = plt.subplots(num='Bright Pixels Frame0') #Create a window/framework for a plot
ax.set(title='Bright Pixels Frame0')
plt.imshow(waBrightMap0, origin='lower')  #Also works for PIL image. #ax.set(title='Fig B')
plt.colorbar()

if wNFile > 1:  #If there's another image:
  #Check for brightness in both images. Otherwise it's a transient event.
  #whereBright0=[np.ndarray.tolist(whereBright0[0]),  np.ndarray.tolist(whereBright0[1])]
  
  waBrightMap01=waBrightMap0
  for wL in range(wNBright0):
    wY=whereBright0[0][wL] ; wX=whereBright0[1][wL]
    fLocalMean=(np.sum(uaAll[1, (wY-1):(wY+2), (wX-1):(wX+2)])-uaAll[1, wY, wX])/8.0
    fExcess=uaAll[1, wY, wX] -fLocalMean
    if fExcess < fThresholdAdu: waBrightMap01[wY, wX]=0  #Eliminate transients
    
  wNBright01=np.sum(waBrightMap01)
  whereBright01=np.where(waBrightMap01==1)

  print('After Frame1, wNBright= ', wNBright01)
  
  #Display the Frame01 map
  fig0, ax = plt.subplots(num='Bright Pixels Frame01') #Create a window/framework for a plot
  ax.set(title='Bright Pixels Frame01')
  plt.imshow(waBrightMap01, origin='lower')  #Also works for PIL image. #ax.set(title='Fig B')
  plt.colorbar()

  #Make an array-list of coords and ADU values
  faHotPix=np.empty((wNBright01, 3))
  for wL in range(wNBright01):
    wY=whereBright01[0][wL] ; wX=whereBright01[1][wL]
    fLocalMean0=(np.sum(uaAll[0, (wY-1):(wY+2), (wX-1):(wX+2)])-uaAll[0, wY, wX])/8.0
    fExcess0=uaAll[0, wY, wX] -fLocalMean0
    fLocalMean1=(np.sum(uaAll[1, (wY-1):(wY+2), (wX-1):(wX+2)])-uaAll[1, wY, wX])/8.0
    fExcess1=uaAll[1, wY, wX] -fLocalMean1
    faHotPix[wL]=[wX, wY, 0.5*(fExcess0+fExcess1)]


#end
