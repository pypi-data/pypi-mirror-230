# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 12:27:02 2021

@author: dmw
"""

#A Dave Walton (UCL/MSSL) program to look at FITs dark current files,
#in particular for Plato.


import os
import fnmatch
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt


#File picker widget
#root=tk.Tk()
#flPathNam=filedialog.askopenfilename(initialdir='c:/', title='Open File',
#      filetypes=(('fits', '*.fits'), ('All Files', '*.*')))
#root.destroy()

#EM1
flPath=["d:/plato/em1_spring_2021/18_06_2021/Image_data_fits/long_dark",
        "d:/plato/em1_spring_2021/17_06_2021/Image_data_fits/long_dark"]
dateString=['2021_06_18', '2021_06_17']
lsFlNum=['ID12670_E_image_1', 'ID12011_E_image_1']

wNFile=len(lsFlNum)

if wNFile & 1:
    print("Bailing due to odd number of files")
    raise SystemExit(0)
wNPair=np.int(wNFile//2)  #// is round-down integer division
    
waIndex=np.arange(wNPair)


flNamExt=['']*2
flNam=['']*2
waSize=[2, 0, 0] #For PTC, 2 frames of size [., y, x]
for wJ in waIndex:
  for wI in range(2):
    wK=wJ*2+wI
    os.chdir(flPath[wK])
    files=os.listdir()
    #wK=wJ*2+wI
    flNamExt[wI]=fnmatch.filter(files, lsFlNum[wK]+'*.fits')[0]
    flNam, flExt=os.path.splitext(flNamExt[wI])
    efPosn=flNam.find('_')+1
    ef=flNam[efPosn:(efPosn+1)]
    #print('\n\n',lsFlNum[wK], ef) #, flNamExt[wI])
 
    with fits.open(flNamExt[wK], mode='denywrite') as hdulist:  #hdulist is a list of the HDUs
      if len(hdulist)==1: hduImage=hdulist[0]  #If a 'simple' single HDU file.
      else:
        hdu0=hdulist[0]
        hduImage=hdulist[1]  #Use 0 if it's a 'simple' image file,
        # 1 if the fits has a hierarchical structure (i.e. a short master header then
        # one or more images (each in an HDU)). Plato files (usually) use [1].
        #See https://docs.astropy.org/en/stable/io/fits/ for details.
      if wI==0:
        hdulist.info()  #Prints the hdulist. For this file, hduist[0] is the top-level HDU
        waSize[1]=hduImage.header['NAXIS2']  #Y
        waSize[2]=hduImage.header['NAXIS1']  #X
        uaAll=np.empty((waSize), dtype=np.uint16)

      uaAll[wI, :, :]=np.uint16(hduImage.data+0.5)  #Ensures it's read as a uint rather than e.g. float.
      hdulist.close()

    if ef == 'E': uaAll[wI, :, :]=np.fliplr(uaAll[wI, :, :])

    uaPre=uaAll[:, :, 20:25]
    uaPreMeanCol=np.mean(uaPre, axis=2)  #Form an average col per frame
    uaSOver=uaAll[:, :, 2289:2294]
    uaSOverMeanCol=np.mean(uaSOver, axis=2)  #Form an average col per frame
    faOffsetMeanCol=(np.mean(uaPreMeanCol, axis=0) + np.mean(uaSOverMeanCol, axis=0))/2.0

  titleString= lsFlNum[wK-1] + '_' + lsFlNum[wK]

  
  #Display the raw images and Difference
  fig0, ax = plt.subplots(num=flNamExt[0]) #Create a window/framework for a plot
  ax.set(title=flNamExt[0])
  uZMin0=np.amin(uaAll[0, :, :]) ; uZMax0=np.amax(uaAll[0, :, :])
  plt.imshow(uaAll[0, :, :], origin='lower', vmin=uZMin0, vmax=uZMax0)  #Also works for PIL image. #ax.set(title='Fig B')
  plt.colorbar()
  #plt.savefig('c:/home/dmw/plato/em2_oct2020/' + flNam)

  fig1, ax = plt.subplots(num=flNamExt[1]) #Create a window/framework for a plot
  ax.set(title=flNamExt[1])
  uZMin1=np.amin(uaAll[1, :, :]) ; uZMax1=np.amax(uaAll[1, :, :])
  plt.imshow(uaAll[1, :, :], origin='lower', vmin=uZMin1, vmax=uZMax1)  #Also works for PIL image. #ax.set(title='Fig B')
  plt.colorbar()
  #plt.savefig('c:/home/dmw/plato/em2_oct2020/' + flNam)

  figD, ax = plt.subplots(num='Diff') #Create a window/framework for a plot
  ax.set(title='Diff')
  laDiff=np.int32(uaAll[1, :, :])-uaAll[0, :, :]
  uZMinD=np.amin(laDiff) ; uZMaxD=np.amax(laDiff)
  plt.imshow(laDiff, origin='lower', vmin=uZMinD, vmax=uZMaxD)  #Also works for PIL image. #ax.set(title='Fig B')
  plt.colorbar()
  #plt.savefig('c:/home/dmw/plato/em2_oct2020/' + flNam)


#end
