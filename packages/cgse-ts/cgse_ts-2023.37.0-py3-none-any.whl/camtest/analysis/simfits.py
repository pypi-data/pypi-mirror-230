#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:39:03 2020

@author: pierre
"""

import datetime

import matplotlib.pyplot as plt
import numpy as np


def info(hdul=None):
    """
    Input
    
    hdul : opened fits file
    
    Output
    
    list_image, list_prescane, list_prescanf, list_overscan = lists of extension IDs for
    WINDOW1     SPRESCANE1     SPRESCANF1     POVERSCAN1    respectively
    
    """
    list_image = []
    list_prescane = []
    list_prescanf = []
    list_overscan = []

    hlist = {"WINDOW1":list_image, "SPRESCANE1":list_prescane, "SPRESCANF1":list_prescanf, "POVERSCAN1":list_overscan,}
    
    for i in range(1,len(hdul)):
        ext  = hdul[i].header["EXTNAME"]
        hlist[ext].append(i)

    return list_image, list_prescane, list_prescanf, list_overscan


def reltime(hdul=None,t0=None):
    """
    Input
    hdul : opened fits file
    t0   : reference time (finetime format, e.g. 1593425727.0)
    
    Output
    array of (unique) frame times, relative to t0
    """
    if t0 is None:
        headert0 = hdul[0].header["DATE-OBS"]
        t0 = datetime.datetime.strptime(headert0, "%Y-%m-%d %H:%M:%S").timestamp()
    
    header_times = np.array([hdul[i].header["DATE-OBS"] for i in range(1,len(hdul))])
    finetime     = np.array([datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timestamp() for timestamp in header_times])
    
    reltime      = finetime - t0
    
    return np.unique(reltime)

def get(hdul=None, field_type='image', n=None):
    """
    Input
    
    hdul       : opened fits file
    field_type : in ['image', 'prescane', 'prescanf', 'overscan']
    n          : image number in fits file
    
    Output
    
    Data array = nth frame of type "field_type" in hdul
    """
    
    list_image, list_prescane, list_prescanf, list_overscan = info(hdul)
    
    field_hash = {"image": list_image, "prescane":list_prescane, "prescanf":list_prescanf, "overscan":list_overscan}
    
    data = hdul[field_hash[field_type][n]].data

    return data

def show(hdul=None, field_type='image', n=None, select=None, figname=None, verbose=True, **kwargs):
    """
    Input
    
    hdul       : opened fits file
    field_type : in ['image', 'prescane', 'prescanf', 'overscan']
    n          : image number in fits file
    select     : optional : if given, must be [xmin,xmax,ymin,ymax]
    
    kwargs     : applied to matplotlib.pyplot.imshow
    
    Output
    
    Extracts the requested dataset from 'hdul' and displays it
    """
    data = get(hdul=hdul, field_type=field_type, n=n)
    
    if verbose: print(f"Shape - original  : {data.shape}")
 
    if select:
        data = data[select[0]:select[1], select[2]:select[3]]
        if verbose: print(f"Shape - selection : {data.shape}")
    
    kwargs.setdefault('interpolation', 'none')
    kwargs.setdefault("origin", "lower")
    kwargs.setdefault("cmap", "jet")

    if select is None:
        figsize = {"image":(6,12), "prescane":(4,12),"prescanf":(4,12), "overscan":(16,4)}[field_type]
    else:
        figsize =  None
    
    if not figname: figname = f"{field_type}_{n}"
    
    plt.figure(figname,figsize=figsize)
    plt.imshow(data,**kwargs)
    plt.colorbar()
    return

