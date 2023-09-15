# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 09:39:44 2021

@author: Martin Pertenais

Versions:
    2022 07 27 - 1.0 EM analysis
"""

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
# %%
import numpy as np
from matplotlib import cm

import CAM_TVPT_010_best_focus_analysis as bestfocus_library
import convenience as cv

#%% Parameters to update for each analysis
workdir = '//bafiler1/PG_PLADAT/CAM_EM_data/IAS/BestFocus-PSF/00500_IAS/'

num_stars = 40
num_frames = 4  # number of frames acquired per FoV position
num_bck = 2   #number of background frames acquired per FoV position
num_subpixel = 25    #number of dithering position per frame
num_layers = num_frames*num_subpixel    #total number of layer per FoV position
num_temp=1

obsid = 500
temperature = -74.0
#%% Identifying and storing the correct file names

filenames = cv.fileSelect([f'00{obsid}_','cube','fits'],location=workdir)
cv.print1(filenames)
ffilenames  = [workdir+filename for filename in filenames]

#%% Reading all the files and storing the data in a 3D array
# this takes some minutes to run (<10min for 1 temperature)

# fffiles ist a 3D array: number of temperatures analysed, number of FoV positions, mnumber of frames per FoV positions

#fffiles = np.empty((1,num_stars, int(num_layers/4)), dtype=object) 
fffiles = np.empty((1,num_stars, num_layers-1), dtype=object) 

for star_ID in range(num_stars):
    # for each FoV position:
    
    # 1st I read the first fits cube for each star (it should contain num_bck layers of dark)
    # in the commanding script, for each FoV position I first call the dark, then the signal
    if not num_bck == 0:
        hduc_dark = pyfits.open(ffilenames[star_ID*2], ignore_missing_simple=True)   
        # my darks are the fits index: 0,2,4,6 (for the first 4 FoV positions)
        
        dark_cube = hduc_dark[2].data    # this is a cube with num_dark layers
        #dark_cube = np.delete(dark_cube,0,0)    # this aims at removing the first layer (saturated)
        #dark = np.average(dark_cube,axis=0) # equivalent to cube[0,:,:] + cube[1;:,:], makes the average of all num_dark frames to create a master dark
        #dark = (dark_cube[1]+dark_cube[2]+dark_cube[3]+dark_cube[5])/4
        dark = dark_cube[1] # I just take the 2nd dark, as the first is saturated
   
    # then I read the signal fits    
        hduc = pyfits.open(ffilenames[star_ID*2 + 1], ignore_missing_simple=True)  # I have a single fits cube for each FoV position (40 fits in total)
   
    else:
        hduc = pyfits.open(ffilenames[star_ID], ignore_missing_simple=True)
        
    # I extract the data from it.
    data_cube = hduc[2].data    # cube with all the signal layers for this star (num_frames*num_subpixel = num_layers, nomimally 100)
    #data_cube = np.delete(data_cube,0,0)

    #for layer_ID in range(int(num_layers/4)):
    for layer_ID in range(num_layers-1):
        
        data_layer = data_cube[layer_ID+1] # 1 individual layer from 1 to 99 (if 4 frames for 25 sub-positions)
        # the first layer is ignored as saturated
        #data_layer = data_cube[4*layer_ID+2] # 2, 6, 10, 14,...98
        
        if num_bck==0:
            fffiles[0,star_ID,layer_ID] = data_layer.astype('float64')
        else:
            #now I correct for dark
            data_corrected = np.subtract(data_layer.astype('float64'),dark.astype('float64'))
            #data_corrected = np.subtract(data_layer[range(1000),:],dark[range(1000),:])    #used in case files have different size (for debugging)

            fffiles[0,star_ID,layer_ID] = data_corrected
#%% Analysis of the data
# this takes several hours per temperature

table1, table2, table3 = bestfocus_library.eef_vs_temp(fffiles=fffiles, temperatures = [temperature], imagette_size=10)

# the 3 tables can be used directly for further analysis
# the function also save a couple of text files in your folder with the EEF results

#%%
data_plot= np.loadtxt("eef_best_centroid.txt")
data_plot= np.loadtxt("IAS_coord.txt")

#%%
from CAM_TVPT_010_best_focus_analysis import equi_surface_radii_fullquadrant, equi_surface_coordinates_fullquadrant, \
    equi_surface_edges_fullquadrant
from matplotlib.patches import Circle
cells = [1,2,3,4]
radius = 81.5184
alledges=True
temperatures=[-77.6]
#data = np.random.rand(40,5)    # TO BE REPLACED by real data
#data = np.array(table2)
#data=data_plot[:,2]
num_temp = 5
temperatures = [-70, -75, -80, -85, -90]

radii = equi_surface_radii_fullquadrant()
xxs, yys = equi_surface_coordinates_fullquadrant()
#xs, ys = oneTo4quadrants(xxs, yys, cells)    # THIS needs to be changed to the actual coordinates visited
xs=data_plot[:,0]
ys=data_plot[:,1]

minimum = 0.7
maximum = 0.9
my_norm = cm.colors.Normalize(vmin = minimum, vmax = maximum, clip = True)
mapper = cm.ScalarMappable(norm = my_norm, cmap = 'jet')

fig, axs = plt.subplots(figsize=(24,5), nrows = 1, ncols = num_temp, squeeze=False)  #nrows = num_temp

# CIRCLES


# RADIAL EDGES
inxys, outxys = equi_surface_edges_fullquadrant(cells=cells, alledges=alledges)

for tt in range(num_temp): #range(num_temp)
    for r in radii:
        circle = Circle((0, 0), r, edgecolor=(0.5, 0.5, 0.5), facecolor="None", linestyle="--", linewidth="1")
        axs[0,tt].add_patch(circle)

    for edge in range(len(inxys)):
        axs[0,tt].plot([inxys[edge, 0], outxys[edge, 0]], [inxys[edge, 1], outxys[edge, 1]], c=(0.5, 0.5, 0.5), linestyle="--", linewidth="1")

    c = axs[0,tt].scatter(xs, ys, s=500, cmap = 'brg', c = mapper.to_rgba(data_plot[:,tt+2]), alpha = 0.75)
    axs[0,tt].set_ylabel(str(temperatures[tt]) + "°C", fontsize = 'x-large')
    axs[0,tt].set_aspect('equal')



fig.colorbar(mapper, shrink=1, ax = axs[0,4])
plt.show()

#%%

s=np.zeros(40)
#data_plot=table2[:,0]
data_plot= np.loadtxt("eef_-90_centroid.txt")
data_plot= np.loadtxt("IAS.txt")

for star_id in range(40):
    s[star_id] = 1000*(1-data_plot[star_id][2])    # TODO: map the coordinates from above with the EEF2


#bestfocus_library.equi_surface_plot_full(alledges=True)
from CAM_TVPT_010_best_focus_analysis import equi_surface_radii_fullquadrant, equi_surface_coordinates_fullquadrant, \
    equi_surface_edges_fullquadrant
from matplotlib.patches import Circle
cells = [1,2,3,4]
radius = 81.5184
alledges=True

radii = equi_surface_radii_fullquadrant()
xxs, yys = equi_surface_coordinates_fullquadrant()
#xs, ys = oneTo4quadrants(xxs, yys, cells)    # THIS needs to be changed to the actual coordinates visited

xs=data_plot[:,0]
ys=data_plot[:,1]

ax = plt.subplot(111, aspect=1.)

ax.scatter(xs, ys, s=s, c='k') 
plt.xlim(-radius, radius)
plt.ylim(-radius, radius)

# CIRCLES
for r in radii:
    circle = Circle((0, 0), r, edgecolor=(0.5, 0.5, 0.5), facecolor="None", linestyle="--", linewidth="1")
    ax.add_patch(circle)

# RADIAL EDGES
inxys, outxys = equi_surface_edges_fullquadrant(cells=cells, alledges=alledges)

for edge in range(len(inxys)):
    plt.plot([inxys[edge, 0], outxys[edge, 0]], [inxys[edge, 1], outxys[edge, 1]], c=(0.5, 0.5, 0.5), linestyle="--", linewidth="1")

plt.xlabel('[mm]', size=11)
plt.ylabel('[mm]', size=11)
plt.show()

#%% Plot of the EEF Distribution

#data = np.array(table1)
data= np.loadtxt("IAS.txt")

fig, axs = plt.subplots(figsize = (2*num_temp, 3), nrows = 1, ncols = num_temp, constrained_layout = True, squeeze=False)
N_BINS = 25
# equidistant spacing of bins
bin_array = np.linspace(0,1,N_BINS) #(0.5,0.9,10)

for k in range(num_temp):
    datak = data[:,k]
    axs[0,k].hist(datak, bins = bin_array)
    axs[0,k].set_title(str(temperatures[k]) + "°C", fontsize = 'x-large')
    axs[0,k].set_xlim((0.0,1.0))
    axs[0,k].vlines(np.mean(datak[~np.isnan(datak)]), ymin = 0, ymax = 15, colors = 'black')
plt.show()
