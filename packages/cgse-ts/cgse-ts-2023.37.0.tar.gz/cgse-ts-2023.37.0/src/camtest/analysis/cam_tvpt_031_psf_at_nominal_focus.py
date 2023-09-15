# -*- coding: utf-8 -*-
"""
CAM ANALYSIS SCRIPT 

@author: Andrea Cottinelli
@editor: Francesco Borsa
@editor: Nicolas Gorius

Synopsis:
    - divided in three modules:
        - import and parameters definition
        - EE extraction
        - EE maximization over dithered position and check plot

This script was used for:
    CAM-TVPT-031 PSF at nominal focus
    CAM-TVPT-XXX Impact of TEB temperature on PSF
    CAM-TVPT-XXX Transient Focus Monitoring - Hartmann and PSF measurements
    CAM-TVPT-XXX Impact on image geometry


Versions:
    2021 11 13 - 0.1 first draft - creation
    2022 05 24 - 1.0 Published - SRON EM #2 version
    2022 06 07 - 1.1 minor corrections
    2022 10 11 - 1.2 updates - IAS EM version

for any question write to andrea.cottinelli@inaf.it

"""

#IMPORT PACKAGES
import os
import numpy as np
from cam_tvpt_031_tools import tvc

### DATA STRUCTURE REQUIRED
# - gen_path
#   - main_data_dir
#       - obsid dir             # img directory
#           - .fits files
#       - obsid_D dir           # darks directory
#           - dark.fits files

### parameters definition   
  
gen_path  = r'D:\2022.07_IAS_EM'
main_data_dir  = "raw_data_psf"

out_1_dir = "out_plateau"
out_2_dir = "out_plateau_2"

bkg_mode = "dark"                         # choose between "dark" for dark frame subtraction and "local" for local background subtraction
bcrop = 35                                # background crop, half size
min_bcrop = 30                            # minimum background crop, half size, for psf close to the edge
s2n=1.05                                  # signal 2 background ratio

reduction = "median"                      # choose  "median" or "mean" for raw data reduction, it means for the 4 images (-1) for each dithering position      
widths = np.array([1,2,4,5,7,10,15)       # square size for EE extraction, in the list both value and norm width has to be present, for example 2x2 and 10x10
n_EE =                len(widths)         # EE squares sizes
n_dither=                    25           # 25 dithered images
nid =                         4           # images per dithering position
pixelsize =               0.018           # mm
numSubPixels =                1           # if you want to add subpixels to analysis
crop =                       16           # crop window for EE, half size
sigmaf=                     0.3           # gaussian smoothing over image
                   
obsid_list=["00500"]                      # insert list of obsid to be processed
n_obs= len(obsid_list)
                                                                                                   

# The next two modules below can be run separately. First one extracts EE from files, create an output directory and save a hdf5 file for each obsid. 
# Second one maximize over dithered position, create an output 2 directory and save an hdf5 file for each obsid
# The two modules are separated by symbol "#%%"

#%%

for ob in range(n_obs):
    obsid=obsid_list[ob]
    now = datetime.datetime.now()    # to make output unique 
    
    if os.path.isdir(os.path.join(gen_path, out_1_dir))==False:                # if output 1 dir does not exist, it's created
        os.mkdir(os.path.join(gen_path, out_1_dir))
        print("'",os.path.join(gen_path, out_1_dir),"'", "directory created")
        
    out_1_name = os.path.join(gen_path, out_1_dir,'OBSID_%s_S%s_%s_%s_%s_%s_%s_%s_EE_CUBE.hdf5'%(obsid, numSubPixels, now.year, now.month, now.day, now.hour, now.minute, now.second))   
    
    img_dir = os.path.join(gen_path, main_data_dir, obsid)
    drk_dir = os.path.join(gen_path, main_data_dir, obsid + "_D")
    
    list_img = os.listdir(img_dir)
    n_img = len(list_img)
    list_drk = os.listdir(drk_dir)
    n_drk = len(list_drk)
    
    # checks on parameters
    if bkg_mode=="dark" and n_img != n_drk:
        raise Exception("Different number of images and darks frame")
    else:
        n_fields=n_img
    
    if n_EE<2:
        raise Exception("Widths has to be at least 2, one for the absolute value, one for normalization")
    
    if crop <= np.max(widths):
        raise Exception("Crop window size has to be bigger than max width")
    
    if bcrop <= np.max(widths):
        raise Exception("Crop window size has to be bigger than max width")
    
    # storage arrays definition  
    EE_cube  = np.zeros((n_fields, n_dither, 2, n_EE)) #Ensquared energies data
    psf_data = np.zeros((n_fields, n_dither, 8)) # position data of psf
    TS_data  = np.zeros((n_fields,2)) # timestamp and exptime for each field
    TS_dataD  = np.zeros((n_fields,2))  #timestamp and exptime for each field for darks
    
    #% PHASE 1:  DATA COLLECTION and REDUCTION    
    for ff in range(len(list_img)):                                            # cycle over fields
        
        img_name  = list_img[ff]  
        img_path  = os.path.join(img_dir,img_name)
        fits_cube, img_or_r, img_or_c, FPx, FPy, rot, TS_data[ff,0], TS_data[ff,1] = tvc.fits_reader(img_path)
        sub_level, nax1, nax2 = fits_cube.shape
        
        if bkg_mode=="dark":                                                   # in dark background mode also darks are extracted from fits
            drk_name = list_drk[ff] 
            drk_path = os.path.join(drk_dir, drk_name)
            drk_cube, drk_or_r, drk_or_c, FPxD, FPyD, rotD , TS_dataD[ff,0], TS_dataD[ff,1] = tvc.fits_reader(drk_path)
     
        for dd in range(n_dither):                                             # cycle over dithered images 
            #i=dd//5
            #j=dd%5                                                 
            start_time = time.time()
            
            ### STEP 1: raw reduction
            if reduction == "median":
                sign = np.median(fits_cube[(dd*nid):(dd+1)*nid,:,:],0)       # first image excluded as it is saturated, median avoid cosmic rays
            elif reduction == "mean":
                sign = np.mean(fits_cube[(dd*nid):(dd+1)*nid,:,:],0)         # first image excluded as it is saturated
           
            xmax = np.where(sign==np.max(sign))[0][0]                          # max flux pixel searched
            ymax = np.where(sign==np.max(sign))[1][0]
            
            if bkg_mode == "dark":
                #bkg = np.mean(drk_cube,0)                                     # average between 2 images
                bkg = drk_cube[1,:,:]                                          # using only second one as first is saturated
            
            elif bkg_mode == "local":
                rbcrop=np.min([bcrop, xmax, ymax, nax1-xmax, nax2-ymax])       # local bkg is defined if there's enough space around psf max
                if rbcrop < min_bcrop:
                    raise Exception("Crop window smaller than limit, dark background suggested")
                else:
                    print("real background crop: %s pixels"% rbcrop)           # if there is not enough space around psf max, it uses the distance from edge only if it is bigger than minimum bkg crop window
                    bkg  = np.median(sign[xmax-rbcrop:xmax+rbcrop+1,ymax-rbcrop:ymax+rbcrop+1])
    
     
            sign = ndimage.gaussian_filter(sign, sigma=sigmaf)
            
            
            if np.max(sign)/np.median(sign)>s2n: #filter on signal/noise ratio
            
                img  = sign - bkg                                                  # image reduction
                
                ### STEP 2 crop e subpixels
                sub_img, xmax, ymax = tvc.subpixeler(img, numSubPixels, rbcrop, interp = False) # if NumSubPixels = 1, it only crops the image 
                
                ### STEP 3: find centroid
                
                # 2D Gaussian fit 
                if sub_img.shape[0]==0 or sub_img.shape[1]==0:#or np.max(sub_img)<=1500:# or (ff==6 and dd==23):
                    EE_img = np.array([0.]*n_EE)
                    mean_y, mean_x, fwhm_y, fwhm_x, amplitude, theta = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
                    xcm=np.nan
                    ycm=np.nan
                else:
                    mean_y, mean_x, fwhm_y, fwhm_x, amplitude, theta = tvc.fit_2dgaussian(sub_img, crop=False, cent=None, fwhmx=4, fwhmy=4, theta=0, threshold=False, sigfactor=6, full_output=True, debug=False)
                    xcm, ycm = tvc.centroid_finder(sub_img)
                    
                    
                ### STEP 4: calculate EE2
                    EE_img, err_EE_img = tvc.EE_calculator_sub(sub_img, xcm, ycm, widths, numSubPixels)    # array of n_EE values                                                                 
                    EE_cube[ff,dd,0,:] = EE_img
                                        
                    if reduction == "mean":
                        EE_cube[ff,dd,1,:] = err_EE_img/np.sqrt(nid-1)
                    elif reduction == "median":
                        EE_cube[ff,dd,1,:] = err_EE_img
                
                
                # translation and rotation to convert psf info to FPA coordinates
                x_gauss, y_gauss = tvc.FPA_trasform(xmax, ymax, crop, mean_x, mean_y, img_or_c, img_or_r, FPx, FPy, rot, pixelsize)
                x_cent,   y_cent = tvc.FPA_trasform(xmax, ymax, crop,    xcm,    ycm, img_or_c, img_or_r, FPx, FPy, rot, pixelsize)
                
                # storing all psf data into one array
                psf_data[ff,dd,:]=[mean_x, mean_y, x_cent, y_cent, x_gauss, y_gauss, fwhm_x, fwhm_y, amplitude, theta]
            
            else: #if signal/noise is too low, set everithig to 0
                EE_img=np.array([0.]*len(widths))
                err_EE_img=np.array([0.]*len(widths))
            
            # service print
            if EE_img[widths==10] != 0.:
                EE_2_10 = EE_img[widths==2]/EE_img[widths==7]
                err_EE_2_10 = EE_2_10*np.sqrt((err_EE_img[widths==2]/EE_img[widths==2])**2 + (err_EE_img[widths==7]/EE_img[widths==7])**2)
            else:
                EE_2_10 = np.array([0.])
                err_EE_2_10 = np.array([0.])
            ### SERVICE PRINT
            print("")
            print("-- OBSID {:05d}, FIELD {:02d}, DITH {:02d}  --".format(int(obsid), ff+1, dd+1))
            print("EEF 2x2: {:.3f} +/- {:.3f}".format(EE_2_10[0], err_EE_2_10[0]))
            rem_t = (time.time() - start_time)*(n_obs*n_fields*n_dither - ob*n_fields*n_dither - ff*n_dither - dd)
            print("--  remaining {:02d} h : {:02d} m : {:02d} s  --".format(int(rem_t//3600),int(rem_t%3600//60),int(rem_t%3600%60)))  
            
    
    ### SAVE DATACUBE 
    fee = h5py.File(out_1_name, 'w')
    fee.create_dataset("EECUBE", data = EE_cube)
    fee.create_dataset("PSF", data = psf_data)
    fee.create_dataset("TIMEDATA", data = TS_data)
    fee.close()



#%% PHASE 2: DITHERING MAXIMIZATION
plot = True
plot_mode = "fields"  # set plot_mode to "fields" to list fields on x axis, or to "FoV" to see EE values distributed spacially

in_dir  = os.path.join(gen_path, out_1_dir)
if os.path.isdir(os.path.join(gen_path, out_2_dir))==False:                    # if output 2 dir does not exist
        os.mkdir(os.path.join(gen_path, out_2_dir))
        print("'",os.path.join(gen_path, out_2_dir),"'", "directory created")

filelist = os.listdir(in_dir)
filelist=[file for file in filelist if file.endswith(".hdf5")]                 # select only hdf5 files in directory
wee = 2                                                                        # EE square size in pixel
wnorm = 10                                                                     # normalization square size in pixel

for fil in filelist:                                                           # cycle over files in out_1_dir
    out_1_name=os.path.join(in_dir,fil)
    EE_hdf5 = h5py.File(out_1_name, 'r') 
    EE_CUBE = EE_hdf5['EECUBE']
    psf_data = EE_hdf5['PSF']
    
    n_fields = EE_CUBE.shape[0]
    n_dither = EE_CUBE.shape[1]
    EE_dith = np.zeros(n_fields)
    EE_dith_err = np.zeros(n_fields)
    PSF = np.zeros((n_fields,psf_data.shape[2]))
    EE_max = np.zeros( n_fields)
                   
    for ff in range(n_fields):                                                 # cycle over fields
        for dd in range(n_dither):                                             # cycle over dithering positions
            EEw    = EE_CUBE[ff,dd,0, np.where(widths==wee)[0][0]]
            EEn    = EE_CUBE[ff,dd,0, np.where(widths==wnorm)[0][0]]
            EEw_er = EE_CUBE[ff,dd,1, np.where(widths==wee)[0][0]]
            EEn_er = EE_CUBE[ff,dd,1, np.where(widths==wnorm)[0][0]]
            
            EEF = EEw / EEn   
            
            if np.isnan(EEF):
                EEF=0
            
            EEFerr = EEF * np.sqrt((EEw_er/EEw)**2 + (EEn_er/EEn)**2)
            
            if EEF > EE_dith[ff]:
                EE_dith[ff]     = EEF
                EE_dith_err[ff] = EEFerr
                PSF[ff,:] = psf_data[ff,dd,:] 
                EE_max[ff] = EE_CUBE[ff,dd,0, np.where(widths==1)[0][0]]
            
            #EE_dith[ff] = np.max([EE_dith[ff],EEF]) 

    
    obsid = fil.split("_")[1]
    
    ### SAVE DATACUBE 
    out_2_name= "EE_obsid_%s_dith_%s_%s.hdf5"%(obsid,wee,wnorm)
    out_2_path = os.path.join(gen_path, out_2_dir, out_2_name)
    
    with h5py.File(out_2_path, 'w') as fed:
        fed.create_dataset("EEdith",     data = EE_dith)
        fed.create_dataset("EEdith_err", data = EE_dith_err)
        fed.create_dataset("PSF",        data = PSF)
        print(fil+" maximized in --> " + out_2_name)


# CHECK PLOT ON LAST MAXIMIZED OBSID

data_path = out_2_path # for different file plot set data_path to another path
with h5py.File(data_path, 'r') as EE_hdf5:
    EE_CUBE = EE_hdf5['EEdith']
    EE_CUBE_err = EE_hdf5['EEdith_err']
    psf_data = EE_hdf5['PSF']
    data_name = data_path.split("\\")[-1].split(".")[0] 
    obsid= data_name.split("_")[2]
    wee=data_name.split("_")[4]
    wnorm=data_name.split("_")[5]
    n_fields=EE_CUBE.shape[0]
    
    if plot==True:
        if plot_mode=="FoV":
            xrange=np.linspace(min(psf_data[:,0]),max(psf_data[:,0]),200)
            yrange=np.linspace(min(psf_data[:,1]),max(psf_data[:,1]),200)
            xcord_dense, ycord_dense = np.meshgrid(xrange,yrange)
            data_dense = griddata((psf_data[:,0], psf_data[:,1]), EE_CUBE , (xcord_dense, ycord_dense), method="cubic")
            
            plt.scatter(xcord_dense,ycord_dense, c=data_dense)
            plt.scatter(psf_data[:,0], psf_data[:,1], c="black", marker="x",s=30)
            plt.colorbar()
            plt.xlabel("X axis [px]")
            plt.ylabel("Y axis [px]")
            plt.title("OBSID %s, EEF %sx%s/%sx%s"%(obsid,wee,wee,wnorm,wnorm))
            plt.axis("equal")
        
        elif plot_mode =="fields":
            plt.errorbar(np.arange(1,EE_CUBE.shape[0]+1,1), EE_CUBE[:], yerr=EE_CUBE_err[:], marker="o", label=obsid)
            plt.xlabel("fields")
            plt.ylabel("EEF %sx%s/%sx%s"%(wee,wee,wnorm,wnorm))
            plt.hlines( 0.77,0, n_fields+1, ls="--", color="gray", alpha=0.5)
            plt.text(n_fields, 0.78, s="REQ. PLT-CAM-872", color="gray", ha="right")
            plt.xlim(0,n_fields+1)
            plt.ylim(0,1.01)
            plt.grid()
            plt.legend()
            plt.title("EE %sx%s/%sx%s"%(wee,wee, wnorm, wnorm))
