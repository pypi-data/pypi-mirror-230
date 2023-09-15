import os
import fnmatch
import numpy as np
from astropy.io import fits

def fileMatch(fileList, stringList):
    """
    fileMatch(fileList, stringList)

    returns the list of files from fileList in which all strings from stringList can be found, in any order
    Case sensitive
    """
    while (len(stringList) > 1):
        fileList = fileMatch(fileList, [stringList.pop()])
    return [file for file in fileList if fnmatch.fnmatch(file, '*' + stringList[0] + "*")]

def fileSelect(stringList, location="./", listOrder=0):
    """
    fileSelect(stringList, location="./", listOrder=0)

    Returns a list of all files in 'location' with name matching every string in the list
    If listOrder is True, the ordering is forced to be identical to the one in stringList
    """
    allfiles = os.listdir(location)
    if listOrder:
        pattern = "*"
        i = 0
        while i < len(stringList):
            pattern += stringList[i] + "*"
            i += 1
        return [file for file in allfiles if fnmatch.fnmatch(file, pattern)]
    else:
        return fileMatch(allfiles, stringList)

def fits_per_layer(obsid, site, datadir, outputdir, full=True, mirroring='readout', overwrite=True, verbose=True):
    """
    Usage:

        from camtest.analysis.fits_per_layer import fits_per_layer

        obsid, site = 162, "CSL1"
        datadir = "/User/disk/platodata/"
        outputdir = "/User/disk/platodata/per_layer/"

        fits_per_layer(obsid=obsid, site=site, datadir=datadir, outputdir=outputdir, full=True, overwrite=True, verbose=True)

    Inputs:
        obsid = obsid (int)

        site  = TH designation string, in ["CSL", "CSL1", "CSL2", "IAS", "INTA", "SRON"]

        datadir = top directory with data, above the site (e.g. SRON)
                  e.g. /user/disk/platodata, when the data are in /user/disk/platodata/SRON/obs/nnnnn_SRON_camera

        outputdir = output directory, receiving the output fits files (flat directory, i.e. independent of the obsid)

        full  = bool (default=True).
                If True, assembles the 'half-ccd' including all pre- and over-scan(s).
                If False, only the image section is copied to the output

        mirroring = 'readout' (default) or 'image'
                readout : the E-side is organised "as it was readout": in the serial direction: prescan, image, overscan
                image : the E-side is organised to form a consistent FoV image with the F-side: overscan, image, prescan
                This is mapped in the image header entry "E_MIRROR"

        overwrite = bool (default=True). If False, pre-existing fits files will be preserved, else they will be overwritten

        verbose = bool (default=True). Allows to follow the progress of the function

    NB: intentionally self-consistent and written in plain python, targetting non-egse users.

    """
    sobsid = str(obsid).zfill(5)
    obsdir = datadir + f"{site}/obs/"
    obsidir = fileSelect([f'{sobsid}'], location=obsdir)[0] + '/'
    filenames = fileSelect([f'{sobsid}_', 'cube', 'fits'], location=obsdir + obsidir)
    ffilenames = [obsdir + obsidir + filename for filename in filenames]

    if verbose:

        print(f"Fits files identified for {obsid=}, {site=} : {ffilenames}\n")

        if mirroring == 'readout':
            print(f"Mirroring of E-SIDE in serial direction = readout order: PREscan, image, OVERscan")
        else:
            print(f"Mirroring of E-SIDE in serial direction = FoV represention: OVERscan, image, PREscan")

    for cn in range(len(filenames)):

        hduc = fits.open(ffilenames[cn])
        basename = os.path.splitext(filenames[cn])[0]

        extnames = ["PRIMARY"]
        extnames.extend(np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object))

        for ccd_number in [1,2,3,4]:
            for ccd_side in ["E", "F"]:

                ccdcode = f"{ccd_number}_{ccd_side}"

                try:

                    # EXTRACT IMAGE
                    iimg = np.where([i.find(f"IMAGE_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                    #row_start = -hduc[iimg].header["CRPIX2"]

                    if verbose:
                        print(f"IMAGE_{ccd_number}_{ccd_side} -- ext {iimg}: {extnames[iimg]}")

                    img_header = hduc[iimg].header
                    img = hduc[iimg].data
                    nlayers = img.shape[0]

                    # EXTRACT FRAME TIMES
                    iwcs = np.where([i.find(f"WCS-TAB_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                    wcs = np.array([hduc[iwcs].data[i][0] for i in range(nlayers)])

                    # EXTRACT SERIAL PRESCAN
                    ispre = np.where([i.find(f"SPRE_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                    spre = hduc[ispre].data

                    # EXTRACT SERIAL OVERSCAN
                    isover = np.where([i.find(f"SOVER_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                    sover = hduc[isover].data

                    # EXTRACT PARALLEL OVERSCAN
                    try:
                        ipover = np.where([i.find(f"POVER_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                        pover = hduc[ipover].data
                    except:
                        pover = None

                except:

                    if verbose:
                        print(f"IMAGE_{ccd_number}_{ccd_side} -- Not present in the data")

                    continue

                # EXTRACT THE LAYERS ONE BY ONE, RECONSTRUCT THE (HALF-)CCD AND EXPORT

                for layer in range(nlayers):

                    outputfilename = outputdir + basename + f"_{str(cn).zfill(2)}_ccd_{ccdcode}_layer_{str(layer).zfill(2)}.fits"

                    if not full:

                        result = img[layer, :, :]

                    else:

                        nrows = img.shape[1]
                        ncols = img.shape[2]
                        nspre = spre.shape[2]
                        nsover = sover.shape[2]
                        if pover is None:
                            npover = 0
                        else:
                            npover = pover.shape[1]

                        nrowstot = nrows + npover
                        ncolstot = ncols + nspre + nsover
                        result = np.zeros([nrowstot, ncolstot], dtype=img.dtype)

                        if ccd_side == "F":

                            result[0:nrowstot, 0:nspre] = spre[layer, :, :]
                            result[0:nrows, nspre:nspre+ncols] = img[layer, :, :]
                            result[0:nrowstot, nspre+ncols:ncolstot] = sover[layer, :, :]
                            if pover is not None:
                                result[nrows:nrowstot, nspre:nspre+ncols] = pover[layer, :, :]

                            # ARRAY-DATA COORDINATE OF THE FIRST COLUMN IN THE IMAGE SECTION
                            img_header["CRPIX1"] = nspre

                        else:

                            result[0:nrowstot, 0:nsover] = sover[layer, :, :]
                            result[0:nrows, nsover:nsover+ncols] = img[layer, :, :]
                            result[0:nrowstot, nsover+ncols:ncolstot] = spre[layer, :, :]
                            if pover is not None:
                                result[nrows:nrowstot, nsover:nsover+ncols] = pover[layer, :, :]

                            img_header["CRPIX1"] = -1 * (ncolstot + nsover)

                            if mirroring == 'readout':
                                result = np.fliplr(result)
                                img_header["CRPIX1"] = -1 * (ncolstot + nspre)
                                img_header["CDELT1"] = -1 * img_header["CDELT1"]
                                img_header["CD1_1"] = -1 * img_header["CD1_1"]
                                img_header["CD2_2"] = -1 * img_header["CD2_1"]

                    img_header["RELTIME"] = wcs[layer]
                    if mirroring == 'readout':
                        img_header["E_MIRROR"] = "READOUT"
                    else:
                        img_header["E_MIRROR"] = "FOV_IMG"

                    primary_hdu = fits.PrimaryHDU(header = hduc[0].header)
                    image_hdu = fits.ImageHDU(result)
                    hdul = fits.HDUList([primary_hdu, image_hdu])
                    hdul[1].header = img_header

                    hdul.writeto(outputfilename, overwrite=overwrite)

        hduc.close()

