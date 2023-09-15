"""
PLATO TVAC TEST CAMPAIN

CAM-TVPT-110 Image Geometry (IGM)

N-CAM, F-CAM

Synopsis:
    - Pre-process imagettes
    - Compute centroids positions for all targets
    - Optimize camera model 

See: PLATO-DLR-PL-TN-0074, 'Fast Camera On-Ground ATBD'
    
This file provides only a library of functions that are called in a Juypter 
Notebook to evaluate the data acquired at the TH.

Author: D.Grießbach

Versions:
    2021 11 08 - 0.1 Draft

"""

import math

import matlab.engine
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio


# get_centroid returns the parameters of a fitted Gaussian PSF
# containing [x0, y0, sigma, I, bg] as well as the number of iterations,
# with the center of mass [x0,y0], the SPF width sigma, the intensity I,
# and the background bg. 
def get_centroid(image, mlEngine):
    #convert to matlab campatible format
    image_ml = matlab.double(image.tolist())

    # calculate initial guess
    state_ml = mlEngine.initGauss(image_ml)
    # refine initial guess
    state_ml = mlEngine.lsqGaussIntegral_5D(image_ml, state_ml, 5)
    state = np.array(state_ml._data)

    return state

def test_centriod(mlEngine):
    #set Gaussian PSF parameters [x0, yo, sigma, I, bg]
    state0 = matlab.double([2.8, 3.2, 0.5, 1000, 100])   
    wndSize =   matlab.int8([6,6])
    
    flux_ml = mlEngine.createGauss(state0, wndSize)
    flux = np.array(flux_ml._data).reshape(flux_ml.size)
    
    # correct image for PRNU, here test with local PRNU of 1% @1sigma
    prnu = np.ones_like(flux) + np.random.randn(*flux.shape)/100
    flux = np.multiply(flux, prnu)
    
    state = get_centroid(flux, mlEngine)
    
    fig, ax = plt.subplots()
    ax.imshow(flux, origin='lower')
    ax.plot(state[0], state[1], '*', color='black')
    return state
    
def test_cameraModelOptimization(mlEngine):
    #load example calibration targets and measurements
    #[ccd#, xPix, yPix, xDir, yDir, zDir]
    mat = sio.loadmat('./matlabLib/calibration.mat')
    calib = mat.get('calib')
    calib_ml = matlab.double(calib.tolist())
    
    #provide initial camera model parameters
    #[f, k1,k2,k3, p1,p2,p3, 4x(x0,y0,gamma0), omega,phi,kappa]
    xInit = matlab.double([13750, 0,0,0, 0,0,0, 0,0,0, 0,0,math.pi/2 , 0,0,math.pi, 0,0,-math.pi/2, 0,0,0])
    xInit.reshape([22,1])
    flag = 3
    
    xOut = mlEngine.platoCamCalibration(xInit, calib_ml, flag)
    xOut = np.array(xOut._data).reshape(xOut.size)

    return xOut





