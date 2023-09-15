# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 15:00 2022
@author: Claudio Arena
Versions:
    2022 09 21 - 1.0 EM analysis
"""

import math
# %%
import os
from collections import OrderedDict

import astropy.io.fits as pyfits
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy.visualization import (PercentileInterval, LinearStretch, ImageNormalize)

import convenience as cv

matplotlib.use('TkAgg')

bcolors = {
    "ENDC": '\033[0m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m',

    "RED": '\033[91m',
    "Green": '\033[92m',
    "BLUE": '\033[94m',
    "Cyan": '\033[96m',
    "White": '\033[97m',
    "Yellow": '\033[93m',
    "Magenta": '\033[95m',
    "Grey": '\033[90m',
    "Black": '\033[90m',
    "Default": '\033[99m'
}

# As found in the original fit file
field_indexes = OrderedDict({
    "1F": 2,
    "1E": 7,
    "2F": 12,
    "2E": 17,
    "3F": 22,
    "3E": 27,
    "4F": 32,
    "4E": 37
})
# As found in the final ordered variable
ordered_fields = OrderedDict({
    "1F": 0,
    "1E": 1,
    "2F": 2,
    "2E": 3,
    "3F": 4,
    "3E": 5,
    "4F": 6,
    "4E": 7
})


# ########### METHODS TO SORT DATA INTO MANAGEABLE ARRAYS ###############
# From an obsid and a folder, returns a complete list of filenames
def get_filenames(obsid, workdir, print_out=False):
    filenames = cv.fileSelect([f'0{obsid}_', 'cube', 'fits'], location=workdir)
    if print_out:
        cv.print1(filenames)
    filenames = [workdir + filename for filename in filenames]
    return filenames


# Return true if the ccd naming in the fit file is as expected (i.e. 1E, 1F, ...)
def verify_ccds_order(fit):
    field_indexes_list = list(field_indexes)
    for field_name, field_index in field_indexes.items():
        expected = 'IMAGE_' + field_name[0] + '_' + field_name[1]
        actual = fit[field_index].name
        if expected != actual:
            return False

    return True


# Return all images, in an array indexed with frame number and field position, with dark frame subtracted
#If type is set to 'master', master image is returned, either as a median or mean, depending on value of 'master_method'
#If type is set to 'individual', individual frames are returned, in an array
def get_images(filename, first=0, last=None, invalid_images=[], output='master',
               master_method='median', dark=None, plot_stability=False):
    if output != 'master' and output != 'individual':
        return exit("Error! Type value not expected!")

    if output == 'master' and not(master_method == 'median' or master_method == 'mean'):
        return exit("Error! No valid master dark method selected")

    fit = pyfits.open(filename, ignore_missing_simple=True)
    if last is None:
        # if None, use until the last element
        last = fit[field_indexes["1F"]].data.shape[0] - 1

    if len(invalid_images) != last-first+1:
        invalid_images = [0] * (last-first+1)

    mask = np.zeros_like(fit[field_indexes["1F"]].data)
    for i in range(len(invalid_images)-1):
        mask[i, :, :] = invalid_images[i]

    res = verify_ccds_order(fit)
    if res is False:
        return exit("Error! Field order is not as expected")

    if output == 'individual':
        images = np.empty((last - first + 1, len(field_indexes.keys())), dtype=object)

    if output == 'master':
        master_frame = np.empty(len(field_indexes.keys()), dtype=object)
        master_frame_std = np.empty(len(field_indexes.keys()), dtype=object)

    if dark is None:
        dark = np.zeros(fit[field_indexes["1F"]].data.shape[1:]).astype('float64')

    if plot_stability:
        plt.figure()

    for n, field_index in enumerate(field_indexes.values()):
        # iterate, for each ccd, through all the images acquired

        #check stability first
        frames_mean = np.mean(fit[field_index].data[first:last+1], axis=(1, 2), dtype='float64')
        if np.std(frames_mean) > 5: #selected by trial and error
            print("Warning! High standard deviation across frames! std:", np.std(frames_mean))
        if plot_stability:
            plt.plot(frames_mean)

        #now sort through individual images
        if output == 'individual':
            for i in range(first, last + 1):
                images[i - first, n] = fit[field_index].data[i] - dark[n]

        if output == 'master':
            #mask array
            #data = np.ma.masked_array(fit[field_index].data.astype('float64'), mask=mask)
            data = fit[field_index].data.astype('float64')
            # since we are doing median, original data format should be ok. Otherwise:
            # median[n] = np.median(fit[field_index].data[first:last].astype('float64'), axis=0)
            if master_method == 'median':
                ##master_frame[n] = np.ma.median(data[first:last+1]-dark[n], axis=0)
                master_frame[n] = np.median(data[first:last+1]-dark[n], axis=0)
            elif master_method == 'mean':
                master_frame[n] = np.mean(data[first:last+1]-dark[n], axis=0, dtype='float64')

            master_frame_std[n] = np.std(data[first:last+1]-dark[n], axis=0)

    if output == 'individual':
        return images
    if output == 'master':
        return master_frame, master_frame_std


# ########### METHODS TO DISPLAY AND SAVE DATA ###############


def save_fit(path, filename, image, header=None):
    hdu = pyfits.PrimaryHDU(image.astype(np.float32))
    if header is not None:
        hdu.header = header
    hdul = pyfits.HDUList([hdu])
    hdul.writeto(path+filename, overwrite=True)

    return


def show_fit(image, title, save_dir='', save_name='', save=False, cmap='gnuplot'):
    norm = ImageNormalize(image, interval=PercentileInterval(99.5), stretch=LinearStretch())
    fig = plt.figure()
    pos = plt.imshow(image, cmap=cmap, norm=norm)
    plt.title(title)
    plt.xlabel("CCD column")
    plt.ylabel("CCD row")
    plt.colorbar(pos, extend='both')

    if save is True:
        plt.savefig(save_dir + save_name + ".png", dpi=100)
        plt.close(fig)

    return


# obtain n of imagesand of ccd, and reshape if only one image
def get_imagearray_info(image_array):
    if len(image_array.shape) == 2:
        n_images = image_array.shape[0]
        n_ccds = image_array.shape[1]
    else:
        n_images = 1
        n_ccds = image_array.shape[0]
        image_array = np.transpose(image_array.reshape(n_ccds, n_images))

    return n_images, n_ccds, image_array


# save an array of image with all fields and all frames into individual files
#provide a path, and this will save all frames to a subfolder named after the "filename"
#Format can be PNG (i.e. imshow save) or fit
def save_all_individually(save_dir, filename, image_array, format='fit'):
    n_images, n_ccds, image_array = get_imagearray_info(image_array)

    f_names = list(field_indexes.keys())
    save_dir = save_dir+filename+"\\"
    os.makedirs(save_dir)

    for n in range(n_images):
        for m in range(n_ccds):
            data = image_array[n, m]
            save_name = filename + "_" + str(f_names[m])
            if n_images > 1:
                save_name = save_name + "_"+str(n)

            if format == 'fit':
                save_fit(save_dir, save_name+".fit", data)
            elif format == 'png':
                plt.title(save_name)
                plt.imshow(data)
                plt.savefig(save_dir + save_name + ".png", dpi=100)
            else:
                return exit("Error! Format not recognised")
    return


# image is a single image, with all fields
def plot_all_fields(image, title, plot_type='image', save=False, save_dir='', override_hist_xlabel=''):
    if save is True:
        exist = os.path.exists(save_dir)
        if not exist:
            os.makedirs(save_dir)

    e_fields = {k: v for k, v in ordered_fields.items() if k.endswith('E')}
    f_fields = {k: v for k, v in ordered_fields.items() if k.endswith('F')}
    plot_fields(image, e_fields, title + ', E sides', plot_type, save, save_dir,
                override_hist_xlabel=override_hist_xlabel)
    plot_fields(image, f_fields, title + ', F sides', plot_type, save, save_dir,
                override_hist_xlabel=override_hist_xlabel)
    return


# image is a single image, with all fields
# type can be image or histogram
def plot_fields(image, fields, title, plot_type='image', save=False, save_dir='', override_hist_xlabel=''):
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(17, 6))
    fig.subplots_adjust(left=0.05, bottom=0.1, right=0.94, top=0.88, wspace=0.3)

    for n, (field_name, field_index) in enumerate(fields.items()):
        if plot_type == 'image':
            norm = ImageNormalize(image[field_index], interval=PercentileInterval(99.7), stretch=LinearStretch())
            im = axes[n].imshow(image[field_index], norm=norm, cmap='gnuplot', aspect='equal')
            plt.colorbar(im, ax=axes[n], extend='both')
            axes[n].set_xlabel("CCD column")
            axes[n].set_ylabel("CCD row")
        elif plot_type == 'histogram':
            norm = ImageNormalize(image[field_index], interval=PercentileInterval(99.7), stretch=LinearStretch())
            limit_min = math.floor(norm.vmin)
            limit_max = math.ceil(norm.vmax)
            im = axes[n].hist(image[field_index].ravel(), bins=round(limit_max - limit_min),
                              range=(limit_min, limit_max), density=True)
            axes[n].set_xticks(range(round(limit_min), round(limit_max+1)))
            if override_hist_xlabel == '':
                axes[n].set_xlabel("ADU [counts]")
            else:
                axes[n].set_xlabel(override_hist_xlabel)
            axes[n].set_ylabel("Probability density")
        elif plot_type == 'slice_col':
            im = axes[n].plot(np.mean(image[field_index], axis=1))
            axes[n].set_xlabel("CCD column")
            axes[n].set_ylabel("mean profile value")
        elif plot_type == 'slice_row':
            im = axes[n].plot(np.mean(image[field_index], axis=0))
            axes[n].set_xlabel("CCD row")
            axes[n].set_ylabel("mean profile value")

        axes[n].set_title(field_name)

    fig.suptitle(title, fontsize=16)
    if save is True and save_dir != '':
        plt.savefig(save_dir + title + ".png", dpi=100)
        plt.close(fig)

    return

# image is a single image, with one field
def plot_single_image(image, title, savename, save=False, save_dir=''):
    if save is True:
        exist = os.path.exists(save_dir)
        if not exist:
            os.makedirs(save_dir)

    fig = plt.figure(figsize=(4.5, 6))

    norm = ImageNormalize(image, interval=PercentileInterval(99.7), stretch=LinearStretch())
    im = plt.imshow(image, norm=norm, cmap='gnuplot', aspect='equal')
    plt.colorbar(im, extend='both')
    plt.xlabel("CCD column")
    plt.ylabel("CCD row")
    plt.title(title, fontsize=16)

    if save is True and save_dir != '':
        plt.savefig(save_dir + savename + ".png", dpi=100)
        plt.close(fig)

    return

def plot_single_slices(image, title, save=True, save_dir = ''):
    if save is True:
        exist = os.path.exists(save_dir)
        if not exist:
            os.makedirs(save_dir)

    fig = plt.figure()
    plt.plot(np.mean(image[0], axis=0))
    plt.xlabel("CCD column")
    plt.ylabel("mean profile value")
    plt.title("Charge Injection, CCD 1F, " + title +", mean column value")
    if save is True and save_dir != '':
        plt.savefig(save_dir + "slice column" + ".png", dpi=100)
        plt.close(fig)

    fig = plt.figure()
    plt.plot(np.mean(image[0], axis=1))
    plt.xlabel("CCD row")
    plt.ylabel("mean profile value")
    plt.title("Charge Injection, CCD 1F, " + title + ", mean row value")
    if save is True and save_dir != '':
        plt.savefig(save_dir + "slice row" + ".png", dpi=100)
        plt.close(fig)

    return
