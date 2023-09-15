# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 08:41:36 2022

@author: Andrea

Set of function required by CAM-TVPT-031-PSF_at_nominal_focus.py


"""

import datetime
import os
import time

import astropy as ast
# IMPORT PACKAGES
import numpy as np
import pandas as pd
import scipy.interpolate
from astropy import modeling
from astropy import stats
from astropy.io import fits
from scipy.linalg import lstsq

EPOCH_1958_1970 = 378691200
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

class tvc():
    def fits_reader(path):
        ff = fits.open(path)
        datacube = ff[2].data
        img_or_r = ff[2].header["CRPIX2"] # CCD origin row wrt 1st transmitted row
        img_or_c = ff[2].header["CRPIX1"] # CCD origin column wrt lower left corner
        FPx      = ff[2].header["CRVAL1"]  # FP x-coordinate of the CCD origin [mm]         
        FPy      = ff[2].header["CRVAL2"]  # FP y-coordinate of the CCD origin [mm]
        rot = ff[2].header["CROTA2"] #CCD orientation angle deg
        TS = ff[2].header["DATE-OBS"]
        expt = ff[2].header["EXPTIME"]
        #time conversione
        element = datetime.datetime.strptime(TS, '%Y-%m-%dT%H:%M:%S.%f%z')
        tuple = element.timetuple()
        timestamp = time.mktime(tuple)
        return datacube, img_or_r, img_or_c, FPx, FPy, rot, timestamp, expt
    
    def fits_reader_extended(path,extension):
        ff = fits.open(path)
        datacube = ff[extension].data
        return datacube
    
    ### make subpixel images
    def subpixeler(img, numSubPixels, crop, interp = False): 
            
        xmax, ymax = np.unravel_index(np.argmax(img, axis=None), img.shape) 
            
        ## cropped image
        img_crop=img[xmax-crop:xmax+crop+1, ymax-crop:ymax+crop+1]
    
        ### cropped dense image
        Xg,Yg = np.mgrid[0:(2*crop)+1:(1/numSubPixels),0:(2*crop)+1:1/(numSubPixels)]
        x,y = np.mgrid[1:(2*crop)+1,1:(2*crop)+1]
        
        if interp == True:
            sub_img = scipy.interpolate.griddata(points = (x.flatten(),y.flatten()), 
                                                  values = img_crop.flatten(), 
                                                  xi     = (Xg,Yg), 
                                                  method = 'cubic',
                                                  fill_value= 0.) 
        else:
            sub_img = img_crop.repeat(numSubPixels,0).repeat(numSubPixels,1)
        
        return sub_img,  xmax, ymax
    
    ### calculate tiptilt plane
    def tiptilter(data, x, y):
        
        # do fit
        tmp_A = []
        tmp_b = []
        for i in range(len(x)):
            tmp_A.append([x[i], y[i], 1])
            tmp_b.append(data[i])
        b = np.matrix(tmp_b).T
        A = np.matrix(tmp_A)
        fit, residual, rnk, s = lstsq(A, b)
        #print(fit)
        Z = np.zeros(len(x))
        for r in range(len(x)):
            Z[r] = fit[0] * x[r] + fit[1] * y[r] + fit[2]
    
        return Z  
      
    
    ### calculate EE in subpixel squares
    def EE_calculator_sub(image, xcent, ycent, widths, numSubPixels):   
        EE=np.zeros(len(widths))
        errEE=np.zeros(len(widths))
        ind=0
        for j in range(len(widths)):
            for i in range(numSubPixels*widths[j]):   
                for k in range(numSubPixels*widths[j]):
                    sub_image =  image[xcent-i:xcent-i+numSubPixels*widths[j],
                                       ycent-k:ycent-k+numSubPixels*widths[j]] 
                    sum_image =sub_image.sum()
                    err_image = np.sum(np.sqrt(np.abs(sub_image)))
                    if sum_image > EE[ind]:
                        EE[ind]   = sum_image
                        errEE[ind]= err_image                    
                    #EE[ind]=np.amax([sum_image,EE[ind]])
            ind+=1
        return EE, errEE
    
    def EE_calculator_sub_fast(image, xcent, ycent, widths, numSubPixels):   
        EE=np.zeros(len(widths))
        for j in range(len(widths)):
            hside=numSubPixels*widths[j]/2.
            sub_image =  image[xcent - hside : xcent + hside,
                               ycent - hside : ycent + hside] 
            EE[j]=sub_image.sum()
            
        return EE

    # fit 2d gaussian to psf subimage
    def fit_2dgaussian(array, crop=False, cent=None, cropsize=15, fwhmx=4, fwhmy=4, 
                       theta=0, threshold=False, sigfactor=6, full_output=False, 
                       debug=False):
        """ Fitting a 2D Gaussian to the 2D distribution of the data with photutils.
        
        Parameters
        ----------
        array : array_like
            Input frame with a single PSF.
        crop : {False, True}, optional
            If True an square sub image will be cropped.
        cent : tuple of int, optional
            X,Y integer position of source in the array for extracting the subimage. 
            If None the center of the frame is used for cropping the subframe (the 
            PSF is assumed to be ~ at the center of the frame). 
        cropsize : int, optional
            Size of the subimage.
        fwhmx, fwhmy : float, optional
            Initial values for the standard deviation of the fitted Gaussian, in px.
        theta : float, optional
            Angle of inclination of the 2d Gaussian counting from the positive X
            axis.
        threshold : {False, True}, optional
            If True the background pixels will be replaced by small random Gaussian 
            noise.
        sigfactor : int, optional
            The background pixels will be thresholded before fitting a 2d Gaussian
            to the data using sigma clipped statistics. All values smaller than
            (MEDIAN + sigfactor*STDDEV) will be replaced by small random Gaussian 
            noise. 
        full_output : {False, True}, optional
            If False it returns just the centroid, if True also returns the 
            FWHM in X and Y (in pixels), the amplitude and the rotation angle.
        debug : {True, False}, optional
            If True, the function prints out parameters of the fit and plots the
            data, model and residuals.
            
        Returns
        -------
        mean_y : float
            Source centroid y position on input array from fitting. 
        mean_x : float
            Source centroid x position on input array from fitting.
            
        If *full_output* is True it returns:
        mean_y, mean_x : floats
            Centroid. 
        fwhm_y : float
            FHWM in Y in pixels. 
        fwhm_x : float
            FHWM in X in pixels.
        amplitude : float
            Amplitude of the Gaussian.
        theta : float
            Rotation angle.
        
        """
        
        if not array.ndim == 2:
            raise TypeError('Input array is not a frame or 2d array')
        
        # If frame size is even we drop last row and last column
        if array.shape[0]%2==0:
            array = array[:-1,:].copy()
        if array.shape[1]%2==0:
            array = array[:,:-1].copy()
        
        if crop:
            if cent is None:
                #ceny, cenx = ast.frame_center(array)
                cenx= np.where(array==np.max(array))[0][0]
                ceny= np.where(array==np.max(array))[1][0]
            else:
                cenx, ceny = cent
            
            imside = array.shape[0]
            psf_subimage, suby, subx = ast.stats.get_square(array, min(cropsize, imside), 
                                                 ceny, cenx, position=True)  
        else:
            psf_subimage = array.copy()  
        
        if threshold:
            _, clipmed, clipstd = ast.sigma_clipped_stats(psf_subimage, sigma=2)
            indi = np.where(psf_subimage<=clipmed+sigfactor*clipstd)
            subimnoise = np.random.randn(psf_subimage.shape[0], psf_subimage.shape[1])*50
            psf_subimage[indi] = subimnoise[indi]
        
        yme, xme = np.where(psf_subimage==psf_subimage.max())
        # Creating the 2D Gaussian model
        gauss = ast.modeling.models.Gaussian2D(amplitude=psf_subimage.max(), x_mean=xme, 
                                  y_mean=yme, x_stddev=fwhmx*ast.stats.gaussian_fwhm_to_sigma, 
                                  y_stddev=fwhmy*ast.stats.gaussian_fwhm_to_sigma, theta=theta)
        
        
        # Levenberg-Marquardt algorithm
        fitter = ast.modeling.fitting.LevMarLSQFitter()                  
        y, x = np.indices(psf_subimage.shape)
        fit = fitter(gauss, x, y, psf_subimage, maxiter=1000, acc=1e-08)
    
        #if crop:
        #    mean_y = fit.y_mean.value + suby
        #    mean_x = fit.x_mean.value + subx
        
        #else:
        mean_y = fit.y_mean.value
        mean_x = fit.x_mean.value 
        
        fwhm_y = fit.y_stddev.value*ast.stats.gaussian_sigma_to_fwhm
        fwhm_x = fit.x_stddev.value*ast.stats.gaussian_sigma_to_fwhm 
        amplitude = fit.amplitude.value
        theta = fit.theta.value
        
        if debug:
            if threshold:  msg = 'Subimage thresholded / Model / Residuals'
            else: msg = 'Subimage (no threshold) / Model / Residuals'
            #pp_subplots(psf_subimage, fit(x, y), psf_subimage-fit(x, y), 
                        #colorb=True, grid=True, title=msg)
            print( 'FWHM_y =', fwhm_y)
            print( 'FWHM_x =', fwhm_x)
            print('centroid y =', mean_y)
            print( 'centroid x =', mean_x)
            print( 'centroid y subim =', fit.y_mean.value)
            print( 'centroid x subim =', fit.x_mean.value )
            print( 'peak =', amplitude)
            print( 'theta =', theta)
        
        if full_output:
            return mean_y, mean_x, fwhm_y, fwhm_x, amplitude, theta
        else:
            return mean_y, mean_x

    def FPA_trasform(xmax, ymax, crop, mean_x, mean_y, img_or_c, img_or_r, FPx, FPy, rot, pixelsize):
        # translate psf centroid to image reference frame
        ximg = xmax - crop + mean_x
        yimg = ymax - crop + mean_y
        
        # translate psf centroid to ccd reference frame
        xccd =  img_or_c - yimg
        yccd =  img_or_r - ximg
        
        # rotate and translate centroid to FPA reference frame
        
        xdef= FPx/(pixelsize)   - xccd*np.cos(np.deg2rad(rot)) + yccd*np.sin(np.deg2rad(rot))
        ydef= FPy/(pixelsize)   - xccd*np.sin(np.deg2rad(rot)) - yccd*np.cos(np.deg2rad(rot))
        
        return xdef, ydef
    
    def centroid_finder(sub_img):
        xsum = np.sum(sub_img,0) 
        ysum = np.sum(sub_img,1)                                               # sum energies along x and y axis
        
        
        Xpos = np.arange(0,np.shape(sub_img)[1],1)
        Ypos = np.arange(0,np.shape(sub_img)[0],1)
        
        xcm = int(np.round(np.sum(Xpos*xsum)/np.sum(xsum)))            
        ycm = int(np.round(np.sum(Ypos*ysum)/np.sum(ysum)))     
        
        return xcm, ycm
    
    def centroid_finder_float(sub_img):
        xsum = np.sum(sub_img,0) 
        ysum = np.sum(sub_img,1)                                               # sum energies along x and y axis
        
        
        Xpos = np.arange(0,np.shape(sub_img)[1],1)
        Ypos = np.arange(0,np.shape(sub_img)[0],1)
        
        xcm = np.sum(Xpos*xsum)/np.sum(xsum)          
        ycm = np.sum(Ypos*ysum)/np.sum(ysum)    
        
        return xcm, ycm
    
# following functions were secretly stolen from Pierre Royer script (many thanks to him!)

    def str_to_datetime(datetime_string: str):
        """ Convert the given string to a datetime object.
        Args:
            - datatime_string: String representing a datetime, in the format %Y-%m-%dT%H:%M:%S.%f%z.
        Returns: Datetime object.
        """
    
        return datetime.datetime.strptime(datetime_string.strip("\r"), TIME_FORMAT)
    
    def time_since_epoch_1958(datetime_string: str):
        """ Calculate the time since epoch 1958 for the given string representation of a datetime.
        Args:
            - datetime_string: String representing a datetime, in the format %Y-%m-%dT%H:%M:%S.%f%z.
        Returns: Time since the 1958 epoch [s].
        """
    
        time_since_epoch_1970 = tvc.str_to_datetime(datetime_string).timestamp()        # Since Jan 1st, 1970, midnight
    
        return time_since_epoch_1970 + EPOCH_1958_1970
    
    def get_frame_times(path):
        """
        Extract the absolute times from all frames in the input data files
        Concatenated into a 1d array
        """
        from astropy.io import fits
    
        result = []
        filenames=os.listdir(path)
        for filename in filenames:
            hduc = fits.open(os.path.join(path,filename),mode='readonly')
    
            extnames = np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object)
            iwcs = np.where([i.find("WCS-TAB") >= 0 for i in extnames])[0][0] + 1
            iimage = np.where([i.find("IMAGE") >= 0 for i in extnames])[0][0] + 1
    
            start_time = tvc.time_since_epoch_1958(hduc[iimage].header["DATE-OBS"])
    
            rel_time = np.array(hduc[iwcs].data,dtype=float)
    
            result.append(rel_time+start_time)
    
        return np.ravel(np.array(result))
    
    def dith_corr_extraction(path_obsid, path_fov_table, n_fields=40, n_dith=25, nid=4):
        """ Extract real commanded dithered positions from HK files (tested with SRON data).
        Args:
            - path_obsid: directory where all obsid images are contained
            - path_fov_table: path to the FoV HK table
            - n_fields: number of fields
            - n_dith: number of dithered position per field
            - nid: number of images per dithered position
        Returns: theta and phi arrays (n_fields, n_dith) extracted from FoV HK table.
        """
        OBStimes = tvc.get_frame_times(path_obsid)
        real_PHI= np.zeros(len(OBStimes))
        real_THETA= np.zeros(len(OBStimes))
        
        df = pd.read_csv(path_fov_table)
        PHI=df['FOV_ACT_PHI']
        THETA= df['FOV_ACT_THETA']
        
        # fov file timestamps
        FOVtimes=np.zeros(len(df["timestamp"]))
        for i in range(len(df["timestamp"])):
            FOVtimes[i] = tvc.time_since_epoch_1958(df["timestamp"][i])
        
        for ii in range(len(OBStimes)):
            min_int = np.where(FOVtimes < OBStimes[ii]-1)[0][-1]
            max_int = np.where(FOVtimes > OBStimes[ii]+1)[0][0]
            real_PHI[ii]= np.mean(PHI[min_int:max_int+1])
            real_THETA[ii]= np.mean(THETA[min_int:max_int+1])
        
        # plt.scatter(FOVtimes[:], df["FOV_ACT_THETA"][:], color="tab:blue", label="gimbal commanded theta")
        # plt.scatter(OBStimes[:], real_THETA[:],color="tab:orange", label="interpolated theta for images")
        # plt.legend()
        
        # correction for each dithering, average on img 1,2,3
        phi=np.zeros((n_fields,n_dith))
        theta=np.zeros((n_fields,n_dith))
        ndf=n_dith
        
        for ff in range(40):
            for dd in range(25):
                phi[ff,dd] = np.mean(real_PHI[(ff*ndf*nid+dd*nid+1):(ff*ndf*nid+(dd+1)*nid)]) # first image is not considered as it is saturated
                theta[ff,dd] = np.mean(real_THETA[(ff*ndf*nid+dd*nid+1):(ff*ndf*nid+(dd+1)*nid)]) # first image is not considered as it is saturated
        
        return phi, theta