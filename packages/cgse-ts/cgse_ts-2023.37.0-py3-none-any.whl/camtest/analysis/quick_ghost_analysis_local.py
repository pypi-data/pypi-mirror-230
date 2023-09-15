# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 15:49:55 2021

@author: pert_mr, further adapted by M. Ammler-von Eiff
"""
import os

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import numpy as np
from astropy.convolution import convolve, Box2DKernel
from matplotlib import colors

import convenience as cv

def write_fits(data,file):
    try:
        os.remove(file)
    except:
        print('no old FITS file to remove')
    hdu_out = pyfits.PrimaryHDU(data)
    hdul_out = pyfits.HDUList([hdu_out])
    hdul_out.writeto(file)
    hdul_out.close()


# TO BE UPDATED with the real workdir including the data
workdir = '/data/'

#num_layers = 4
obsid = 3054
fits_number = "2"

#filename = cv.fileSelect([f'0{obsid}_',f'{fits_number}_','cube','fits'],location=workdir)
filenames = cv.fileSelect([f'0{obsid}_','cube','fits'],location=workdir)
ffilenames  = [workdir+filename for filename in filenames]

#theta_array = [3.8, 7.6, 11.4, 15.2, 18.88]
#phi_array = [0, 30, 60, 90, 135, 225, 315]
#l = 0
#for phi in phi_array:
#    for theta in theta_array:
#        print(l*3+3,theta,phi)
#        l = l+1


num_layer = {"dark":2, "nonsat":11, "sat":3}
#%%
hduc = pyfits.open(workdir+filenames[1], ignore_missing_simple=True)

#%%  DARK FRAMES
star_ID=2 # FoV position [0-some)]

hduc_dark = pyfits.open(ffilenames[star_ID*3], ignore_missing_simple=True)   
# my darks are the fits index: 0,3,6,9 (for the first 4 FoV positions)

dark_cube_1F = hduc_dark[2].data
dark_cube_1E = hduc_dark[7].data
dark_cube_2F = hduc_dark[12].data
dark_cube_2E = hduc_dark[17].data
dark_cube_3F = hduc_dark[22].data
dark_cube_3E = hduc_dark[27].data
dark_cube_4F = hduc_dark[32].data
dark_cube_4E = hduc_dark[37].data

dark_1F = dark_cube_1F[1] #I ignore the first layer(#0), and load only the second one (#1)
dark_1E = dark_cube_1E[1]
dark_2F = dark_cube_2F[1]
dark_2E = dark_cube_2E[1]
dark_3F = dark_cube_3F[1]
dark_3E = dark_cube_3E[1]
dark_4F = dark_cube_4F[1]
dark_4E = dark_cube_4E[1]

path = workdir + 'reduced/'
write_fits(dark_1F,path+filenames[star_ID*3]+'_dark_1F.fits')
write_fits(dark_1E,path+filenames[star_ID*3]+'_dark_1E.fits')
write_fits(dark_2F,path+filenames[star_ID*3]+'_dark_2F.fits')
write_fits(dark_2E,path+filenames[star_ID*3]+'_dark_2E.fits')
write_fits(dark_3F,path+filenames[star_ID*3]+'_dark_3F.fits')
write_fits(dark_3E,path+filenames[star_ID*3]+'_dark_3E.fits')
write_fits(dark_4F,path+filenames[star_ID*3]+'_dark_4F.fits')
write_fits(dark_4E,path+filenames[star_ID*3]+'_dark_4E.fits')

#%% NON-SAT FRAMES

dark_1F = dark_1F.astype(np.float64)
dark_1E = dark_1E.astype(np.float64)
dark_2F = dark_2F.astype(np.float64)
dark_2E = dark_2E.astype(np.float64)
dark_3F = dark_3F.astype(np.float64)
dark_3E = dark_3E.astype(np.float64)
dark_4F = dark_4F.astype(np.float64)
dark_4E = dark_4E.astype(np.float64)

hduc_nonsat = pyfits.open(ffilenames[star_ID*3+1], ignore_missing_simple=True)   
# my nonsat are the fits index: 1,4,7,10 (for the first 4 FoV positions)

nonsat_cube_1F = hduc_nonsat[2].data
nonsat_cube_1E = hduc_nonsat[7].data
nonsat_cube_2F = hduc_nonsat[12].data
nonsat_cube_2E = hduc_nonsat[17].data
nonsat_cube_3F = hduc_nonsat[22].data
nonsat_cube_3E = hduc_nonsat[27].data
nonsat_cube_4F = hduc_nonsat[32].data
nonsat_cube_4E = hduc_nonsat[37].data

nonsat_1F = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_1E = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_2F = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_2E = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_3F = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_3E = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_4F = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))
nonsat_4E = np.zeros((np.size(nonsat_cube_1F[0],0),np.size(nonsat_cube_1F[0],1)))

#print('background subtraction non-saturated frames')
for layer in range(num_layer["nonsat"]-1):
    nonsat_1F += (nonsat_cube_1F[layer+1]-convolve(dark_1F, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_1E += (nonsat_cube_1E[layer+1]-convolve(dark_1E, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_2F += (nonsat_cube_2F[layer+1]-convolve(dark_2F, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_2E += (nonsat_cube_2E[layer+1]-convolve(dark_2E, Box2DKernel(20))/dark_2E)/num_layer["nonsat"]
    nonsat_3F += (nonsat_cube_3F[layer+1]-convolve(dark_3F, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_3E += (nonsat_cube_3E[layer+1]-convolve(dark_3E, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_4F += (nonsat_cube_4F[layer+1]-convolve(dark_4F, Box2DKernel(20)))/num_layer["nonsat"]
    nonsat_4E += (nonsat_cube_4E[layer+1]-convolve(dark_4E, Box2DKernel(20)))/num_layer["nonsat"]


# save frames:
print('saving background-corrected nonsaturated frames')
write_fits(nonsat_1F,path+filenames[star_ID*3+1]+'_nonsat_1F.fits')
write_fits(nonsat_1E,path+filenames[star_ID*3+1]+'_nonsat_1E.fits')
write_fits(nonsat_2F,path+filenames[star_ID*3+1]+'_nonsat_2F.fits')
write_fits(nonsat_2E,path+filenames[star_ID*3+1]+'_nonsat_2E.fits')
write_fits(nonsat_3F,path+filenames[star_ID*3+1]+'_nonsat_3F.fits')
write_fits(nonsat_3E,path+filenames[star_ID*3+1]+'_nonsat_3E.fits')
write_fits(nonsat_4F,path+filenames[star_ID*3+1]+'_nonsat_4F.fits')
write_fits(nonsat_4E,path+filenames[star_ID*3+1]+'_nonsat_4E.fits')

# quick look commands for nonsaturated frames:

#%%
crop = True

if crop == True:
    imagette_size = 50
    
    centroid = np.unravel_index(np.argmax(nonsat_1F, axis=None), nonsat_1F.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_1F.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_1F.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_1F = nonsat_1F[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_1E, axis=None), nonsat_1E.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_1E.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_1E.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_1E = nonsat_1E[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_2F, axis=None), nonsat_2F.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_2F.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_2F.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_2F = nonsat_2F[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_2E, axis=None), nonsat_2E.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_2E.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_2E.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_2E = nonsat_2E[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_3F, axis=None), nonsat_3F.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_3F.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_3F.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_3F = nonsat_3F[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_3E, axis=None), nonsat_3E.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_3E.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_3E.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_3E = nonsat_3E[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_4F, axis=None), nonsat_4F.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_4F.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_4F.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_4F = nonsat_4F[row_min:row_max, column_min:column_max]
    
    centroid = np.unravel_index(np.argmax(nonsat_4E, axis=None), nonsat_4E.shape)
    row_max     = int(min(centroid[0] + imagette_size/2,nonsat_4E.shape[0]))
    row_min     = int(max(centroid[0] - imagette_size/2,0))
    column_max  = int(min(centroid[1] + imagette_size/2,nonsat_4E.shape[1]))
    column_min  = int(max(centroid[1] - imagette_size/2,0))
    nonsat_4E = nonsat_4E[row_min:row_max, column_min:column_max]


fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2,4)
ax1.set_title("CCD 1E")
ax2.set_title("CCD 1F")
ax3.set_title("CCD 2E")
ax4.set_title("CCD 2F")
ax5.set_title("CCD 3E")
ax6.set_title("CCD 3F")
ax7.set_title("CCD 4E")
ax8.set_title("CCD 4F")

ax1.imshow(nonsat_1E, cmap ="rainbow", norm = colors.LogNorm())
ax2.imshow(nonsat_1F, cmap ="rainbow", norm = colors.LogNorm())
ax3.imshow(nonsat_2E, cmap ="rainbow", norm = colors.LogNorm())
ax4.imshow(nonsat_2F, cmap ="rainbow", norm = colors.LogNorm())
ax5.imshow(nonsat_3E, cmap ="rainbow", norm = colors.LogNorm())
ax6.imshow(nonsat_3F, cmap ="rainbow", norm = colors.LogNorm())
ax7.imshow(nonsat_4E, cmap ="rainbow", norm = colors.LogNorm())
ax8.imshow(nonsat_4F, cmap ="rainbow", norm = colors.LogNorm())




#%%
#%% SAT FRAMES

hduc_sat = pyfits.open(ffilenames[star_ID*3+2], ignore_missing_simple=True)   
# my darks are the fits index: 2, 5,8,11 (for the first 4 FoV positions)

sat_cube_1F = hduc_sat[2].data
sat_cube_1E = hduc_sat[7].data
sat_cube_2F = hduc_sat[12].data
sat_cube_2E = hduc_sat[17].data
sat_cube_3F = hduc_sat[22].data
sat_cube_3E = hduc_sat[27].data
sat_cube_4F = hduc_sat[32].data
sat_cube_4E = hduc_sat[37].data

sat_1F = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_1E = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_2F = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_2E = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_3F = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_3E = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_4F = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))
sat_4E = np.zeros((np.size(sat_cube_1F[0],0),np.size(sat_cube_1F[0],1)))

#print('background subtraction for saturated frames')
for layer in range(num_layer["sat"]-1):
    sat_1F += (sat_cube_1F[layer+1]-convolve(dark_1F, Box2DKernel(20)))/num_layer["sat"]
    sat_1E += (sat_cube_1E[layer+1]-convolve(dark_1E, Box2DKernel(20)))/num_layer["sat"]
    sat_2F += (sat_cube_2F[layer+1]-convolve(dark_2F, Box2DKernel(20)))/num_layer["sat"]
    sat_2E += (sat_cube_2E[layer+1]-convolve(dark_2E, Box2DKernel(20)))/num_layer["sat"]
    sat_3F += (sat_cube_3F[layer+1]-convolve(dark_3F, Box2DKernel(20)))/num_layer["sat"]
    sat_3E += (sat_cube_3E[layer+1]-convolve(dark_3E, Box2DKernel(20)))/num_layer["sat"]
    sat_4F += (sat_cube_4F[layer+1]-convolve(dark_4F, Box2DKernel(20)))/num_layer["sat"]
    sat_4E += (sat_cube_4E[layer+1]-convolve(dark_4E, Box2DKernel(20)))/num_layer["sat"]

#%%

# save frames:
print('writing saturated background-corrected frames')
write_fits(sat_1F,path+filenames[star_ID*3+2]+'_sat_1F.fits')
write_fits(sat_1E,path+filenames[star_ID*3+2]+'_sat_1E.fits')
write_fits(sat_2F,path+filenames[star_ID*3+2]+'_sat_2F.fits')
write_fits(sat_2E,path+filenames[star_ID*3+2]+'_sat_2E.fits')
write_fits(sat_3F,path+filenames[star_ID*3+2]+'_sat_3F.fits')
write_fits(sat_3E,path+filenames[star_ID*3+2]+'_sat_3E.fits')
write_fits(sat_4F,path+filenames[star_ID*3+2]+'_sat_4F.fits')
write_fits(sat_4E,path+filenames[star_ID*3+2]+'_sat_4E.fits')


fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2,4)
ax1.set_title("CCD 1E")
ax2.set_title("CCD 1F")
ax3.set_title("CCD 2E")
ax4.set_title("CCD 2F")
ax5.set_title("CCD 3E")
ax6.set_title("CCD 3F")
ax7.set_title("CCD 4E")
ax8.set_title("CCD 4F")

ax1.imshow(sat_1E, cmap ="rainbow", norm = colors.LogNorm())
ax2.imshow(sat_1F, cmap ="rainbow", norm = colors.LogNorm())
ax3.imshow(sat_2E, cmap ="rainbow", norm = colors.LogNorm())
ax4.imshow(sat_2F, cmap ="rainbow", norm = colors.LogNorm())
ax5.imshow(sat_3E, cmap ="rainbow", norm = colors.LogNorm())
ax6.imshow(sat_3F, cmap ="rainbow", norm = colors.LogNorm())
ax7.imshow(sat_4E, cmap ="rainbow", norm = colors.LogNorm())
ax8.imshow(sat_4F, cmap ="rainbow", norm = colors.LogNorm())

plt.show()
