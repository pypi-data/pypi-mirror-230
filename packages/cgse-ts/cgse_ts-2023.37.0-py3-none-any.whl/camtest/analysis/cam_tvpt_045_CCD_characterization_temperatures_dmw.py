# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 16:59:22 2021

@author: dmw
"""

#A Dave Walton (UCL/MSSL) program to look at Plato NFEE temperature runs,
#e.g. from 

import os

import matplotlib.pyplot as plt
import numpy as np
# import subprocess  #For OS commands. Supposed to be better than os
from astropy.io import fits

#Flags for processing/plotting blocks
wStabilityFlag=1
wGdFlag=0

#QM1
#flPath="d:/plato/qm/Tests_QM_qualification_Tests_7_10_2021_performed_on_plastic_NFEE/Soak_test_at_ambient_with_CCD_cold_in_chamber/Long_soak_c_inj_70p_baseline_FPA_ccd2"
dateString='2021_10_07'
#Below, strings only need to be long enough to uniquely identify the file.
#Store in order 1F, 1E, 2F, 2Eetc. to give conventional anticlockwise order from theta=0 in MSSL chamber.
lsFlNum=['ID19146', 'ID20226', 'ID20515']  #All F_image_4_CCD2
wavelen='500nm'

#For selected range
#uaNum=np.arange(20000, 20100, dtype=int)
#wNFile=len(uaNum)
#lsFlNum=''*wNFile
#for wK in range(wNFile):
#  lsFlNum[wK]='ID' + str(uaNum[wK])


#For multi-folder tests, e.g. Test3
#Create a multi-folder list
#Can do this more simply using os.walk if all files are to be used.
#But the method below makes it easier to use particular ranges.

#Test3
#Room temperature tripod CCD, ~Wed 06oct2021 (maybe Thu 07)
flPathLevel0="c:/Users/dmw/Downloads/Test3/3a_CI_Stability_with_CCD_Tripod/"
flPathLevel1='Test3a_c_inj_stability_test_on_ccd2_only_Ambient/'
flPathLevel2=['with_70_percent_saving_data_first_leg/', 'with_30_percent_saving_data_second_leg/', 'with_70_percent_saving_data_last_leg/']

#Same data, different location, also with Ambient+10 and A+20C.
flPathLevel0="d:/plato/qm1/Tests_QM_qualification_Tests_7_10_2021_performed_on_plastic_NFEE/Test3/CI_Stability/"
flPathLevel1='Test3a_c_inj_stability_test_on_ccd2_only_Ambient/'
flPathLevel1='Test3a_c_inj_stability_test_on_ccd2_only_10_degrees_higher_than_Ambient/'
#flPathLevel1='Test3a_c_inj_stability_test_on_ccd2_only_20_degrees_higher_than_Ambient/'
flPathLevel2=['with_70_percent_saving_data_first_leg/', 'with_30_percent_saving_data_second_leg/', 'with_70_percent_saving_data_last_leg/']

#Cold CCD Soak test
flPathLevel0="d:/plato/qm1/Tests_QM_qualification_Tests_7_10_2021_performed_on_plastic_NFEE/"
flPathLevel1='Soak_test_at_ambient_with_CCD_cold_in_chamber/'
flPathLevel2=['Long_soak_c_inj_70p_baseline_FPA_ccd2/']


#Test2
#Injection v. V_GD
#flPathLevel0="d:/plato/qm1/Tests_QM_qualification_Tests_7_10_2021_performed_on_plastic_NFEE/"
#flPathLevel1='Test2/2a_c_inj_tests_with_FPAnumbering_ccd2_with_cold_CCD/'
#flPathLevel2=['with_12V/', 'with_13V/', 'with_135V/', 'with_14V/', 'with_15V/', 'with_16V/', 'with_17V/', 'with_18V/', 'with_19V/', 'with_20V/']


flPathLevel01=flPathLevel0 + flPathLevel1
wNFolderLevel2=len(flPathLevel2)
os.chdir(flPathLevel01)


#wNFileLevel2=wNFolderLevel2*[0]  #Int
#for wK in range(wNFolderLevel2):
#  os.chdir(flPathLevel2[wK])
#  wNFileLevel2[wK]=len([name for name in os.listdir('.') if os.path.isfile(name)])

#wNFileTot=np.sum(wNFileLevel2)

    


for wL in range(wNFolderLevel2):
  os.chdir(flPathLevel2[wL])
  #See https://www.askpython.com/python/examples/list-files-in-a-directory-using-python
  #for the syntax of the line below. Keeps only files, not dirs.
  lsFiles=[f for f in os.listdir() if os.path.isfile(f)]

  #Create folder for results file(s)
  #sRelPath='temperature_results'
  #RelPath=Path(sRelPath)
  #try:
  #  Path.mkdir(RelPath)
  #except OSError as error:
  #  print(error)
  #  print('Error probably due to directory already existing, so continuing.')
  #  print('No existing directories will be deleted.\n')

  wNFile=len(lsFiles)
  
  ###################### Bodge ###########
  #wNFile=100
  ########################################

  waNFile=np.arange(wNFile)
  waSize=[wNFile, 0, 0] #For PTC, 2 frames of size [., y, x]
  #waIndex=np.arange(wNFile)
  flNamExt=['']*wNFile
  flNam=['']*wNFile
  faTemperaturesHk=np.zeros((wNFile))  #HK Temp sequence for each CCD
  faOffset=np.empty(wNFile)
  faDark=np.empty(wNFile)
  faChInj=np.empty(wNFile)
  faOffsetCh=np.empty(wNFile)
  faTemperaturesHk=np.zeros((wNFile))  #HK Temp sequence for each CCD
  saReadOrd=['']*wNFile
  waSumReadOrdTot=np.empty(wNFile)

  for wK in range(wNFile):
    print(wK)
    #flNamExt[wK]=fnmatch.filter(files, lsFlNum[wK]+'*.fits')[0]
    #flNam[wK], flExt=os.path.splitext(flNamExt[wK])
    #efPosn=flNam[wK].find('_')+1
    #ef=flNam[wK][efPosn:(efPosn+1)]
    #print('\n\n',lsFlNum[wK], ef) #, flNamExt[wI])
 
    with fits.open(lsFiles[wK], mode='denywrite') as hdulist:  #hdulist is a list of the HDUs
      if len(hdulist)==1: hduImage=hdulist[0]  #If a 'simple' single HDU file.
      else:
        hdu0=hdulist[0]
        hduImage=hdulist[1]  #Use 0 if it's a 'simple' image file,
        # 1 if the fits has a hierarchical structure (i.e. a short master header then
        # one or more images (each in an HDU)). Plato files (usually) use [1].
        #See https://docs.astropy.org/en/stable/io/fits/ for details.
      if wK==0:
        hdulist.info()  #Prints the hdulist. For this file, hduist[0] is the top-level HDU
        waSize[1]=hduImage.header['NAXIS2']  #Y
        waSize[2]=hduImage.header['NAXIS1']  #X
        #faAll=np.empty(waSize)
        uaAll=np.empty((waSize[1:3]), dtype=np.uint16)
      
      uaAll=hduImage.data
      faTemperaturesHk[wK]=hduImage.header['T1_C2']  #CCD Temperature
      saReadOrd[wK]=hduImage.header['READ_ORD']  #Readout order, e.g. '1-2-3-4 '
      hdulist.close()

    faOffset[wK]=np.mean(uaAll[2476:2566, 1:13])  #Overscan
    faDark[wK]=np.mean(uaAll[2476:2566, 20:32])
    faChInj[wK]=np.mean(uaAll[2575:2665, 20:32])
    faOffsetCh[wK]=np.mean(uaAll[2575:2665, 1:13])  #Overscan
  
  os.chdir('../')
  if wL==0:
    faTemperaturesHkTot=faTemperaturesHk
    saReadOrdTot=saReadOrd
    faOffsetTot=faOffset
    faDarkTot=faDark
    faChInjTot=faChInj
    faOffsetChTot=faOffsetCh
  else:
    faTemperaturesHkTot=np.concatenate((faTemperaturesHkTot, faTemperaturesHk))
    saReadOrdTot=np.concatenate(saReadOrdTot, saReadOrd)
    faOffsetTot=np.concatenate((faOffsetTot, faOffset))
    faDarkTot=np.concatenate((faDarkTot, faDark))
    faChInjTot=np.concatenate((faChInjTot, faChInj))
    faOffsetChTot=np.concatenate((faOffsetChTot, faOffsetCh))

faDarkMinus=faDarkTot-faOffsetTot
faChInjMinus=faChInjTot-faOffsetChTot
faChInjMinusMinus=faChInjMinus - faDarkMinus


#Some FITs files have T in ADU, others have degC
if faTemperaturesHkTot[0] > 20000.0:
  faT=faTemperaturesHkTot
  faT*=4.096/65535.0  #ADC to Voltage
  faT*=1.0/9.94/.003   #Voltage to Resistance
  faT=-242.02+(faT*2.2228)+(faT*faT*0.0025859)-(0.000004826*faT*faT*faT)-(0.000000028183*faT*faT*faT*faT)+(0.00000000015243*faT*faT*faT*faT*faT)
  faTemperaturesHkTot=faT
  del faT
  for wI in range(wNFile):
    waSumReadOrdTot[wI]=int(saReadOrdTot[wI][0]) + int(saReadOrdTot[wI][2]) + int(saReadOrdTot[wI][4]) + int(saReadOrdTot[wI][6])
  
wLoLim=0
wHiLim=wNFile
    
#Plots etc.
if wStabilityFlag==1:
  fig, ax = plt.subplots()
  ax.set(title='ReadOrder, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], waSumReadOrdTot[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ##ax.set_aspect('equal')
  ax.set(title='T_CCD, N-FEE=' + flPathLevel1[40:], xlabel='time', ylabel='degC')
  ax.plot(waNFile[wLoLim:wHiLim], faTemperaturesHkTot[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='ADC_Offset, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], faOffsetTot[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='Dark_Area, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], faDarkTot[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='Dark_Area - Offset, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], faDarkMinus[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='ChInj_Area, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], faChInjTot[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='ChInj_Area - Dark, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[wLoLim:wHiLim], faChInjMinusMinus[wLoLim:wHiLim])

  fig, ax = plt.subplots()
  ax.set(title='ChInj_Area_1st - Dark, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[0:48], faChInjMinusMinus[0:48])

  fig, ax = plt.subplots()
  ax.set(title='ChInj_Area_2nd - Dark, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[48:96], faChInjMinusMinus[48:96])

  fig, ax = plt.subplots()
  ax.set(title='ChInj_Area_3rd - Dark, N-FEE=' + flPathLevel1[40:], xlabel='FrameID', ylabel='ADU')
  ax.plot(waNFile[96:], faChInjMinusMinus[96:])


if wGdFlag==1:
  faChInjMean=np.empty([10])
  faVGd=np.array([ 12.0, 13, 13.5, 14, 15, 16, 17, 18, 19, 20])
  waNGd=    np.array([2,  2,  2,    3,  3,  6,  3,  2,  2,  2])
  waStartGd=np.array([0, 2, 4, 6, 9, 12, 18, 21, 23, 25, 27])
  for wL in range(10):
    faChInjMean[wL]=np.mean(faChInjMinusMinus[waStartGd[wL]:waStartGd[wL+1]])

  fig, ax = plt.subplots()
  ax.set(title='ChInj v. V_GD', xlabel='V_GD', ylabel='ADU')
  ax.plot(faVGd, faChInjMean)     

  fig, ax = plt.subplots()
  ax.set(title='Log(ChInj) v. V_GD', xlabel='V_GD', ylabel='ADU')
  plt.yscale('log')
  ax.plot(faVGd, faChInjMean)     
    
#end