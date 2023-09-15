# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 15:00 2022
@author: Claudio Arena
Versions:
    2022 09 21 - 1.0 EM analysis
"""

#%%
import numpy as np
import CAM_TVPT_050_autocompatibility_utilities as util

#%% Parameters to update for each analysis
#for each hduc, order of frames is listed in util.field_indexes

#IAS data structure:
#1 (0): 10 background images
#2 (1): Charge injection full: 10 frames, camera 1,2,3,4 both sides, ci width 100, gap 100, ci_vgd 17
#3 (2) TCS in extended mode, 10 backgrounds
#4 (3): 10 imagers, TCS off
#5 (4): Charge injection full, as before
IAS_EM = {
    #"path": 'G://PLATO_data/EM/IAS/TVPT-050 CAM autocompatibility/00547_IAS/',
    "path": 'D://Plato_Data//00547_IAS//',
    "obsid": 547,
    "num_frames": 10,
    "num_bck": 10,
    "num_cams": 8
}
TH = IAS_EM
save_plots = False

workdir = TH["path"]
obsid = TH["obsid"]
files = util.get_filenames(obsid, workdir, print_out=True)
fields_names = list(util.field_indexes.keys()) #useful to know what field is which


# %%%% WORK WITH DARKS %%%%

#%% Obtain dark median for all fields. exclude the first dark (first=1) as it might have issues
dark_TCS_ON_beforeCI, dark_std_TCS_ON_beforeCI = \
    util.get_images(files[0], first=1, master_method='median')
dark_TCS_ON_afterCI, dark_std_TCS_ON_afterCI = \
    util.get_images(files[2], first=1, master_method='median')
dark_TCS_OFF_beforeCI, dark_std_TCS_OFF_beforeCI = \
    util.get_images(files[3], first=1, master_method='median')

print("Images loaded")
## Space for special cases (i.e. contaminated darks)

##save frames with issues, for reference
save_dir = workdir + 'bad_frames/'
dark_TCS_ON_beforeCI_single = util.get_images(files[0], output='individual')
dark_TCS_ON_afterCI_single = util.get_images(files[2], output='individual')

im = dark_TCS_ON_beforeCI_single[1, 6]
util.plot_single_image(im, savename='Selected bad dark frame, TCS On, before CI, 4F',
                       title="Selected bad dark frame \n TCS On, before CI, 4F",
                       save=save_plots, save_dir=save_dir)
im = dark_TCS_ON_beforeCI_single[1, 7]
util.plot_single_image(im, savename='Selected bad dark frame, TCS On, before CI, 4E',
                       title="Selected bad dark frame \n TCS On, before CI, 4E",
                       save=save_plots, save_dir=save_dir)
im = dark_TCS_ON_afterCI_single[1, 6]
util.plot_single_image(im, savename='Selected bad dark frame, TCS On, after CI, 4F',
                       title="Selected bad dark frame \n TCS On, after CI, 4F",
                       save=save_plots, save_dir=save_dir)
#Free some ram
del dark_TCS_ON_beforeCI_single, dark_TCS_ON_afterCI_single, im

#Special for 4F, which has a bright band
dark_TCS_ON_afterCI_special_case, dark_std_TCS_ON_afterCI_special_case = \
    util.get_images(files[2], first=8, master_method='median')

dark_TCS_ON_afterCI[6] = dark_TCS_ON_afterCI_special_case[6]
dark_std_TCS_ON_afterCI[6] = dark_std_TCS_ON_afterCI_special_case[6]

#special case for 4E and 4F, bright area in the bottom
dark_TCS_ON_beforeCI_special_case, dark_std_TCS_ON_beforeCI_special_case = \
    util.get_images(files[0], first=3, master_method='median')

dark_TCS_ON_beforeCI[6] = dark_TCS_ON_beforeCI_special_case[6]
dark_TCS_ON_beforeCI[7] = dark_TCS_ON_beforeCI_special_case[7]
dark_std_TCS_ON_beforeCI[6] = dark_std_TCS_ON_beforeCI_special_case[6]
dark_std_TCS_ON_beforeCI[7] = dark_std_TCS_ON_beforeCI_special_case[7]
del dark_TCS_ON_beforeCI_special_case, dark_std_TCS_ON_beforeCI_special_case,\
    dark_TCS_ON_afterCI_special_case, dark_std_TCS_ON_afterCI_special_case
print("Special cases loaded")

#save fits for master darks
#util.save_all_individually(workdir, "dark_median1", dark_TCS_ON_beforeCI, format='fit')
#util.save_all_individually(workdir, "dark_median2", dark_TCS_ON_afterCI, format='fit')
#util.save_all_individually(workdir, "dark_median3", dark_TCS_OFF_beforeCI, format='fit')

#save pngs of all the fields
save_dir = workdir + 'Darks_plots/'

util.plot_all_fields(dark_TCS_ON_beforeCI, title="Dark median - TCS On, before CI", save=save_plots, save_dir=save_dir)
util.plot_all_fields(dark_TCS_ON_afterCI, title="Dark median - TCS On, after CI", save=save_plots, save_dir=save_dir)
util.plot_all_fields(dark_TCS_OFF_beforeCI, title="Dark median - TCS Off, before CI", save=save_plots, save_dir=save_dir)

CI_diff = dark_TCS_ON_beforeCI - dark_TCS_ON_afterCI
util.plot_all_fields(CI_diff, title="Dark diff - TCS On, before CI minus after CI", save=save_plots, save_dir=save_dir)
TCS_diff = dark_TCS_ON_beforeCI - dark_TCS_OFF_beforeCI
util.plot_all_fields(TCS_diff, title="Dark diff - before CI, TCS On minus TCS Off", save=save_plots, save_dir=save_dir)

util.plot_all_fields(dark_std_TCS_ON_beforeCI, title="Dark standard deviation - TCS On, before CI", save=save_plots, save_dir=save_dir)
util.plot_all_fields(dark_std_TCS_OFF_beforeCI, title="Dark standard deviation - TCS Off, before CI", save=save_plots, save_dir=save_dir)

util.plot_all_fields(CI_diff, title="Histogram of dark diff - TCS On, before CI minus after CI",
                     plot_type="histogram", save=save_plots, save_dir=save_dir)
util.plot_all_fields(TCS_diff, title="Histogram of dark diff - before CI, TCS On minus TCS Off",
                     plot_type="histogram", save=save_plots, save_dir=save_dir)

print("Standard deviation mean, TCS On before CI:")
for n in range(8):
    print(list(util.ordered_fields.keys())[n] + ": " + str(np.mean((dark_std_TCS_ON_beforeCI[n]), axis=(0, 1))))

print("Standard deviation mean, TCS Off before CI:")
for n in range(8):
    print(list(util.ordered_fields.keys())[n] + ": " + str(np.mean((dark_std_TCS_OFF_beforeCI[n]), axis=(0, 1))))

util.plot_all_fields(dark_std_TCS_OFF_beforeCI, title="Histogram of dark standard dev - before CI, TCS Off",
                     plot_type="histogram", save=save_plots, save_dir=save_dir)

# %%%% WORK WITH IMAGES CI %%%%

#%% Load image data. exclude the first two images (first=2) as they might have issues
chargeInjection_TCS_ON, chargeInjection_TCS_ON_std = util.get_images(files[1], first=2, dark=dark_TCS_ON_beforeCI)
chargeInjection_TCS_OFF, chargeInjection_TCS_OFF_std = util.get_images(files[4], first=2, dark=dark_TCS_OFF_beforeCI)

#save pngs of all the fields
save_dir = workdir + 'CI Plots/'

#median
util.plot_all_fields(chargeInjection_TCS_ON, title="Charge injection median, TCS On", save=save_plots, save_dir=save_dir)
util.plot_all_fields(chargeInjection_TCS_OFF, title="Charge injection median, TCS Off", save=save_plots, save_dir=save_dir)

#difference
CI_im_diff = chargeInjection_TCS_ON-chargeInjection_TCS_OFF
util.plot_all_fields(CI_im_diff,
                     title="Charge injection diff, TCS On minus TCS Off", save=save_plots, save_dir=save_dir)

#standard deviation
util.plot_all_fields(chargeInjection_TCS_ON_std,
                     title="Charge injection standard deviation, TCS On", save=save_plots, save_dir=save_dir)
util.plot_all_fields(chargeInjection_TCS_OFF_std,
                     title="Charge injection standard deviation, TCS Off", save=save_plots, save_dir=save_dir)

#difference as fraction of standard deviation
quadrature_error = np.zeros_like(chargeInjection_TCS_ON_std)
sq_sum = np.square(chargeInjection_TCS_ON_std) + np.square(chargeInjection_TCS_OFF_std)
for i in range(8):
    quadrature_error[i] = np.sqrt(sq_sum[i])

CI_im_diff_std = CI_im_diff / quadrature_error
util.plot_all_fields(CI_im_diff_std, plot_type="histogram",
                     title="Charge injection diff, divided by pixel standard deviation", save=save_plots, save_dir=save_dir,
                     override_hist_xlabel="Sigma factor")


#print st.dev = 0 percentage
print("percentage of pixels with st.dev of 0:")
for n in range(8):
    n_pix = np.count_nonzero(chargeInjection_TCS_ON_std[n] == 0)
    fraction = (n_pix / chargeInjection_TCS_ON_std[n].size) * 100
    print(list(util.ordered_fields.keys())[n] + ": " + str(fraction) + "%, n: " + str(n_pix))

#slices
util.plot_all_fields(chargeInjection_TCS_ON, title="Charge injection mean column values, TCS On",
                     plot_type='slice_col', save=save_plots, save_dir=save_dir)
util.plot_all_fields(chargeInjection_TCS_ON, title="Charge injection mean row values, TCS On",
                     plot_type='slice_row', save=save_plots, save_dir=save_dir)

#save individual slices
util.plot_single_slices(chargeInjection_TCS_ON, "TCS On", save=save_plots, save_dir=save_dir)
