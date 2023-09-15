"""

Version: 1.0 20211205. hk_avg_per_obsid & hk_per_frame
         1.1 202112    get_device_names, get_hk_names, get_device_for_hk
         1.2 20211213  get_hk : sort output wrt time + more flexible approach to 'datadir'
         1.3 20211214  csv_to_fits + solve issue #467 (proper handling of MaskedColumns wrt time-selections)
         1.4 20220208  get_hk_day, get_hk_date_range, hk_add_finetime, hk_interpolate, get_tm_dictionary, hk_select_keys

P. Royer
"""
import os
import sys
import astropy
import numpy as np
from astropy.io import ascii
from astropy.table import Table, Column
import camtest.analysis.convenience as cv
from scipy.interpolate import interp1d
from egse.system import time_since_epoch_1958


def get_hk(obsid, device, datadir, verbose=True, **kwargs):
    """
    Returns the HK table recorded from the input device during the input obsid, i.e. the content of <device>.csv

    INPUT
    obsid  : integer or string
    device : string that must appear in the HK filename, e.g. "SMC", "PUNA", "N-FEE-HK", "DPU", "AEU-PSU4", "AEU-CRIO"
    datadir: location of the HK csv files
    verbose: if true, will print the column names in the output table

    OUTPUT
    HK table with the complete content of the HK for the given device during the obsid  (astropy.table.table.Table)

    """
    # Correct full path in datadir:
    hktab = cv.csvLoad([str(obsid),device], location=datadir, listOrder=0, verbose=False, **kwargs)

    # datadir points to top directory .../site/obs/
    if hktab is None:
        obsidir = cv.fileSelect([str(obsid).zfill(5)], location=datadir)[0] + '/'
        hktab = cv.csvLoad([str(obsid),device], location=datadir+obsidir, listOrder=0, verbose=False, **kwargs)

        if hktab is None:
            print("WARNING: NO CORRESPONDING HK FILE FOUND")
            return None
        elif verbose:
                print(f"Reading HK from {datadir + obsidir}")

    elif verbose:
        print(f"Reading HK from {datadir}")


    # 1st column = either "timestamp" or "timecode_ts"
    try:
        finetime = np.array([time_since_epoch_1958(i) for i in hktab[hktab.colnames[0]]])
    except:
        finetime = np.zeros(len(hktab))
        for c, i in enumerate(hktab["timestamp"]):
            try:
                finetime[c] = time_since_epoch_1958(i)
            except:
                #print(c, i, time_since_epoch_1958(i))
                i = i.replace('60.000', '59.999')
                finetime[c] = time_since_epoch_1958(i)

    hktab.add_column(Column(finetime,name="finetime"))

    hktab.sort(keys='finetime', reverse=False)

    hktab.add_column(Column(hktab['finetime']-hktab['finetime'][0],name="reltime"))

    if verbose:
        for i,c in enumerate(hktab.columns):
            print(f"{i:2d}   {c:<s}")

    return hktab


def get_hk_day(date, device, keys=None, datadir=None, add_finetime=True, verbose=True):
    """

    """
    if datadir is None:
        datadir = os.getenv("PLATO_LOCAL_DATA_LOCATION")
        datadir = datadir.replace("/obs/", "/daily/")

    stringList = [device, "csv"]

    datedir = datadir + str(date) + '/'

    if not os.path.exists(datedir):

        print(f"ERROR: no data found for the input date {date}")
        return None

    else:

        files = cv.fileSelect(stringList=stringList, location=datedir, listOrder=0)

        if verbose:
            print("Extracting ", date, files)

        hktab = cv.csvLoad([device,'csv'], location=datedir, listOrder=0, verbose=False)

        # INCLUDE FINETIME
        ##################


        if add_finetime:

            if verbose:
                print()
                print("Include Finetime")

            hktab = hk_add_finetime(hktab)

        # SELECT KEYS
        #############

        if keys is not None:

            if verbose:
                print()
                print(f"Selecting columns {keys}")

            hkout = hk_select_keys(hkin=hktab, keys=keys, verbose=verbose)

        else:

            hkout = hktab

        return hkout

def hk_select_keys(hkin, keys, verbose=True):
    """

    """
    from astropy.table import Table, Column

    hkout = Table()

    for inkey in hkin.keys():

        if (inkey in keys) or (inkey in ["timestamp", "timecode", "finetime"]):
            hkout.add_column(col=hkin[inkey])

    return hkout


def hk_per_obsid(obsids, device, keys, datadir="/Volumes/IZAR/plato/data/em/sron/obs/",outputfile=None, func=np.nanmean, verbose=True):
    """
    obsids = list of obsids, e.g. [2200, 2345]
    device = identifier of one HK csv file, e.g. "HK-SYN"
    keys   = list of identifiers of HK entries, e.g. ["GSYN_TTS_L6_SN1A", "GSYN_TTS_TOU_01"]
    datadir= directory with the HK / obs, e.g. "/disk/owner/platodata/em/sron/obs/"
    outputfile : if given, the ascii table is writen to "outputfile" (full path)
    func   =    function to be applied to 'merge' each HK entry over the duration of the obsid
                default: numpy.nanmean

    Returns an ascii table with the average HK value for each of the HK keys, for each of the input obsids

    Note: The function 'func' is applied over the entire duration of the observation, not over the time frame
    corresponding to the actual image acquisition (may be very different, esp. with the use of start/end_observation)

    See also: hk_per_cube, hk_per_frame

    Example usage:
    obsids = [2345, 2672]
    device = "HK-SYN"
    keys   = ["GSYN_TRP1", "GSYN_TRP22"]
    datadir= "/disk/owner/platodata/em/sron/obs/"
    hktab = hk_avg_per_obsid(obsids=obsids, device=device, keys=eys, datadir=datadir)
    """
    # from camtest import GlobalState
    # if site is None:
    #     site = GlobalState.setup.site_id

    nobsids = len(obsids)

    htable = {}
    for key in keys:
        if (key == "timestamp") or (key == "timecode_ts"):
            htable["timestamp_0"] = np.zeros(nobsids, dtype=object)
            htable["finetime"] = np.zeros(nobsids)
        else:
            htable[key] = np.zeros(nobsids)

    for i, obsid in enumerate(obsids):

        obsidir = cv.fileSelect([str(obsid).zfill(5)], location=datadir)[0] + '/'

        if verbose:
            print(obsidir)

        hk = get_hk(obsid, device=device, datadir=datadir + obsidir, verbose=False)

        for key in keys:
            if (key == "timestamp") or (key == "timecode_ts"):
                htable["timestamp_0"][i] = hk[key][0]
                htable['finetime'][i] = np.round(func(hk['finetime']), 3)
            else:
                htable[key][i] = np.round(func(hk[key]), 3)

    tab = Table()
    cobsids = Column(data=obsids, name="obsid")
    tab.add_column(cobsids)
    for key in htable.keys():
        c = Column(data=htable[key], name=key)
        tab.add_column(col=c)

    if outputfile is not None:
        overwrite = True
        ascii.write(table=tab, output=outputfile, format='fixed_width', overwrite=overwrite)

    return tab


def hk_per_frame(obsids, device, keys, datadir="/Volumes/IZAR/plato/data/em/sron/obs/", outputfile=None, decimals=8, verbose=True):
    """
    obsids = list of obsids, e.g. [2200, 2345]
    device = identifier of one HK csv file, e.g. "HK-SYN"
    keys   = list of identifiers of HK entries, e.g. ["GSYN_TTS_L6_SN1A", "GSYN_TTS_TOU_01"]
    datadir= directory with the HK / obs, e.g. "/disk/owner/platodata/em/sron/obs/"
    outputfile : if given, the ascii table is writen to "outputfile" (full path)

    returns an ascii table with the HK value for each of the HK keys, interpolated at the acquisition time of every
    frame of the input obsids

    See also: hk_per_cube, hk_per_obsid

    Example usage:
    obsids = [2345, 2672]
    device = "HK-SYN"
    keys   = ["GSYN_TRP1", "GSYN_TRP22"]
    datadir= "/disk/owner/platodata/em/sron/obs/"
    outputfile="/home/me/plato/hk_table.txt"
    hktab = hk_per_frame(obsids=obsids, device=device, keys=eys, datadir=datadir, outputfile=outputfile)

    """

    # PREPARE HK TABLE

    htable = {}
    for key in keys:
        if not (key == "timestamp") and not (key == "timecode_ts"):
            htable[key] = []

    # LOOP OVER OBSIDS
    # ----------------

    all_obsids = []
    all_frame_times = []
    all_cubes = []
    all_layers = []
    all_filenames = []

    for i, obsid in enumerate(obsids):

        # IDENTIFY THE DATA DIRECTORIES
        # -----------------------------
        sobsid = str(obsid).zfill(5)
        obsidir = cv.fileSelect([sobsid], location=datadir)[0] + '/'

        if verbose: print(obsidir)

        # READ THE CSV FILE WITH THE HK FOR THE INPUT DEVICE
        # --------------------------------------------------
        hk = get_hk(obsid, device=device, datadir=datadir + obsidir, verbose=False)
        hk_finetime = hk['finetime']

        # Extract cubes
        # -------------
        filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir + obsidir)
        if verbose:
            print("  Cubes:")
            cv.print1(filenames)

        ffilenames = [datadir + obsidir + filename for filename in filenames]

        # Extract frame times
        # ----------------
        if verbose:
            print("  Extracting Frame Times")

        #frame_times = cv.get_frame_times(ffilenames)
        for c,afile in enumerate(ffilenames):
            frame_times = cv.get_frame_times([afile])
            all_frame_times += list(frame_times)
            all_obsids += [obsid for i in range(len(frame_times))]
            all_cubes += [c for i in range(len(frame_times))]
            all_layers += [i for i in range(len(frame_times))]
            all_filenames += [filenames[c] for i in range(len(frame_times))]

            # Interpolate HK entries on frame_times
            # -------------------------------------

            for key in keys:

                if not (key == "timestamp") and not (key == "timecode_ts"):

                    # Only MaskedColumn have a 'mask'
                    if isinstance(hk[key], astropy.table.column.MaskedColumn):
                        valid_time_sel = np.where(np.logical_not(hk[key].mask))
                        f = interp1d(hk_finetime[valid_time_sel], hk[key][valid_time_sel], kind='linear', fill_value='extrapolate')
                    else:
                        f = interp1d(hk_finetime, hk[key], kind='linear', fill_value='extrapolate')

                    htable[key] += list(f(frame_times))


    # Convert HK lists to astropy.table.Columns
    # -----------------------------------------

    if verbose:
        print(f"    HK entries: {len(htable)}")

    htable["filename"] = np.array(all_filenames, dtype=object)

    tab = Table()
    for key in htable.keys():
        try:
            c = Column(data=np.round(np.array(htable[key]), decimals=decimals), name=key)
        except:
            c = Column(data=htable[key], name=key)
        tab.add_column(col=c)

    # Insert columns relative to the structure of the obsid
    # -----------------------------------------------------

    htable["frame"] = np.array([i for i in range(len(all_frame_times))])
    htable["obsid"] = np.array(all_obsids)
    htable["cube"] = np.array(all_cubes)
    htable["layer"] = np.array(all_layers)
    htable["frame_times"] = np.array(all_frame_times)

    for key in ['frame_times', 'layer', 'cube', 'obsid', 'frame']:
        c = Column(data=htable[key], name=key)
        tab.add_column(col=c, index=0)

    # Output
    # ------

    if outputfile is not None:
        overwrite = True
        ascii.write(table=tab, output=outputfile, format='fixed_width', overwrite=overwrite)

    return tab


def hk_per_cube(obsids, device, keys, datadir="/Volumes/IZAR/plato/data/em/sron/obs/", outputfile=None, func=np.nanmean, decimals=8, verbose=True):
    """
    obsids = list of obsids, e.g. [2200, 2345]
    device = identifier of one HK csv file, e.g. "HK-SYN"
    keys   = list of identifiers of HK entries, e.g. ["GSYN_TTS_L6_SN1A", "GSYN_TTS_TOU_01"]
    datadir= directory with the HK / obs, e.g. "/disk/owner/platodata/em/sron/obs/"
    outputfile : if given, the ascii table is writen to "outputfile" (full path)
    func   =    function to be applied to 'merge' each HK entry over the duration of a each data cube
                default: numpy.nanmean

    Returns an ascii table with the HK value for each of the HK keys, averaged over the acquisition time of the frames
    of each cube in the input obsids

    See also: hk_per_obsid, hk_per_frame

    Example usage:
    obsids = [2345, 2672]
    device = "HK-SYN"
    keys   = ["GSYN_TRP1", "GSYN_TRP22"]
    datadir= "/disk/owner/platodata/em/sron/obs/"
    outputfile="/home/me/plato/hk_table.txt"
    hktab = hk_per_frame(obsids=obsids, device=device, keys=eys, datadir=datadir, outputfile=outputfile)

    """

    # PREPARE HK TABLE

    htable = {}
    for key in keys:
        if not (key == "timestamp") and not (key == "timecode_ts"):
            htable[key] = []

    # LOOP OVER OBSIDS
    # ----------------

    all_obsids = []
    all_cubes = []
    all_timestamps_0 = []
    all_finetimes = []
    all_filenames = []

    for i, obsid in enumerate(obsids):

        # IDENTIFY THE DATA DIRECTORIES
        # -----------------------------
        sobsid = str(obsid).zfill(5)
        obsidir = cv.fileSelect([sobsid], location=datadir)[0] + '/'

        if verbose: print(obsidir)

        # READ THE CSV FILE WITH THE HK FOR THE INPUT DEVICE
        # --------------------------------------------------
        hk = get_hk(obsid, device=device, datadir=datadir + obsidir, verbose=False)
        hk_finetime = hk['finetime']

        # Extract cubes
        # -------------
        filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir + obsidir)
        if verbose:
            print("  Cubes:")
            cv.print1(filenames)

        ffilenames = [datadir + obsidir + filename for filename in filenames]

        all_obsids += [obsid for i in range(len(ffilenames))]
        all_cubes += [c for c in range(len(ffilenames))]
        all_filenames += filenames

        # Extract frame times
        # ----------------
        if verbose:
            print("  Extracting Frame Times")

        #frame_times = cv.get_frame_times(ffilenames)
        for c, afile in enumerate(ffilenames):

            frame_times = cv.get_frame_times([afile])
            all_timestamps_0.append(frame_times[0])

            # TO DO : REPLACE THIS BLOCK BY THE COMMENTED LINE BELOW ONCE common-egse issue #1441 is fixed
            all_finetimes.append(func(frame_times))

            # Interpolate HK entries on frame_times
            # -------------------------------------

            for key in keys:

                if not (key == "timestamp") and not (key == "timecode_ts"):

                    # Only MaskedColumn have an attribute 'mask'
                    if isinstance(hk[key], astropy.table.column.MaskedColumn):
                        valid_time_sel = np.where(np.logical_not(hk[key].mask))
                        f = interp1d(hk_finetime[valid_time_sel], hk[key][valid_time_sel], kind='linear', fill_value='extrapolate')
                    else:
                        f = interp1d(hk_finetime, hk[key], kind='linear', fill_value='extrapolate')

                    htable[key].append(np.round(func(f(frame_times)), decimals=decimals))

    # Convert HK lists to astropy.table.Columns
    # -----------------------------------------

    if verbose:
        print(f"    HK entries: {len(htable)}")

    htable["filename"] = np.array(all_filenames, dtype=object)

    tab = Table()
    for key in htable.keys():
        print(f"{key} {len(htable[key])}")
        c = Column(data=htable[key], name=key)
        tab.add_column(col=c)

    # Insert columns relative to the structure of the obsid
    # -----------------------------------------------------

    htable["obsid"] = np.array(all_obsids)
    htable["cube"] = np.array(all_cubes)
    htable["timestamp_0"] = np.array(all_timestamps_0)
    htable["finetime"] = np.array(all_finetimes)

    for key in ['finetime', 'timestamp_0',  'cube', 'obsid']:
        print(f"{key} {len(htable[key])}")
        c = Column(data=htable[key], name=key)
        tab.add_column(col=c, index=0)

    # Output
    # ------

    if outputfile is not None:
        overwrite = True
        ascii.write(table=tab, output=outputfile, format='fixed_width', overwrite=overwrite)

    return tab


def get_device_names(obsid, datadir, verbose=False, em1=False):
    """
    get_device_names(obsid, datadir, verbose=False, em1=False)

    Get the list of available HK files for a given obsid and extract the device name from their names

    em1 : after SRON EM1, the structure of the finelame changed -> CSL em and SRON em1 are a special cases
          EM 1 == SRON OBSIDS < 2300
               == CSL  OBSIDS < 924
    """

    if em1:
        device_string_pos = 3
    else:
        device_string_pos = 2

    sobsid = str(obsid).zfill(5)
    obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'

    filenames = cv.fileSelect([f'{sobsid}_', 'csv'], location=datadir+obsidir)

    if verbose:
        print("HK files found for {obsid=}")
        cv.print1(filenames)

    keys = []
    for file in filenames:
        keys.append(file.split('_')[device_string_pos])

    if verbose:
        print("HK devices found for {obsid=}")
        cv.print1(keys)

    return np.array(keys)

def get_hk_names(obsid, datadir, device):
    """
    Get the list of available HK entries for a given device (for a given obsid)
    """
    #hktab = cv.csvLoad([str(obsid), device], location=datadir, listOrder=0, **kwargs)

    stringList = [str(obsid), device, 'csv']

    obsidir = cv.fileSelect([f'{str(obsid).zfill(5)}'],location=datadir)[0] + '/'

    files = cv.fileSelect(stringList=stringList, location=datadir+obsidir, listOrder=0)

    f = open(datadir+obsidir+files[0], 'r')

    line = f.readline()

    return np.array([entry.strip() for entry in line.split(',')])

def get_device_for_hk(obsid, datadir, name, exact_match=False, verbose=True):
    """
    Get the list of [device_name, hk_entry] in which HK entries with a given string can be found.

    exact_match :
        True: parameter name 'hk_name' must be an exact match (quicker)
        False: returns all HK entries having 'hk_name' as a substring

    Examples:

        get_device_for_hk(obsid=2205, datadir="/platodata/SRON/obs/", name="GSYN_TRP1", exact_match=True)
            0 ['SYN-HK' 'GSYN_TRP1']
            1 ['SYN' 'GSYN_TRP1']

        get_device_for_hk(obsid=2205, datadir="/platodata/SRON/obs/", name="GSYN_TRP1", exact_match=False)
            0 ['SYN-HK' 'GSYN_TRP1']
            1 ['SYN-HK' 'GSYN_TRP1_1']
            2 ['SYN-HK' 'GSYN_TRP1_2']
            3 ['SYN-HK' 'GSYN_TRP1_3']
            4 ['SYN-HK' 'GSYN_TRP10']
            5 ['SYN' 'GSYN_TRP1']
            6 ['SYN' 'GSYN_TRP1_1']
            7 ['SYN' 'GSYN_TRP1_2']
            8 ['SYN' 'GSYN_TRP1_3']
            9 ['SYN' 'GSYN_TRP10']
    """

    device_names = get_device_names(obsid, datadir)

    result = []

    for device in device_names:

        hk_names = get_hk_names(obsid, datadir, device)

        if exact_match:
            for hk_name in hk_names:
                if hk_name == name:
                    result.append([device, hk_name])
        else:
            for hk_name in hk_names:
                if hk_name.find(name) >= 0:
                    result.append([device, hk_name])

    result = np.array(result)

    if verbose:
        cv.print1(result)

    return result

def csv_to_fits(obsid, device, datadir, outputfile=None, overwrite=False, verbose=True):
    """
    csv_to_fits(obsid, device, datadir, outputfile=None, overwrite=False, verbose=True)

    obsid : e.g. 2188
    device : string from the target csv file,
             uniquely identifying the device in the setup used for 'obsid' (e.g. "ENSEMBLE")
    datadir : directory of the data. E.g. /platodata/em/SRON/obs/02188_SRON_00047/

    outputfile : output filename (full path). If None a default is used.
    overwrite : allow to overwrite a pre-existing <outputfile>.fits file

    verbose : debug prints
    """

    hktab = get_hk(obsid=obsid, device=device, datadir=datadir, verbose=verbose)

    if outputfile is None:
        outputfile = f"./obsid_{obsid}_device_{device}_HK_csv_to.fits"
        print(f"INFO: no output filename provided. Default output: {outputfile}")

    hktab.write(outputfile, overwrite=overwrite)

def hk_add_finetime(hktab, verbose=True):
    """
    hk_add_finetime(hktab, verbose=True)

    If the table doesn't contain 'finetime', it's added

    finetime is defined as "seconds since 1958"

    !! IT IS ASSUMED THAT THE FIRST COLUMN CONTAINS the 'timestamp', THE ACTUAL NAME OF THE COLUMN IS NOT CHECKED
       Before 20220205, it could be 'timestamp', 'timecode_ts', 'timecode',
       and in the case of the TCS : anything ending with '_ts' (-- changed by common-egse issues
    """
    if "finetime" not in hktab.colnames:

        if verbose:

            print(f"INFO: hk_add_finetime: reading time information from 1st column: {hktab.colnames[0]}")

        try:
            try:

                finetime = np.array([time_since_epoch_1958(i) for i in hktab[hktab.colnames[0]]])

            except:

                print(f"INFO: hk_add_finetime: attempt level 2 -- faulty timestamp with 60.000 seconds")

                finetime = np.zeros(len(hktab))
                #for c, i in enumerate(hktab["timestamp"]):
                for c, i in enumerate(hktab[hktab.colnames[0]]):
                    try:
                        finetime[c] = time_since_epoch_1958(i)
                    except:
                        #print(c, i, time_since_epoch_1958(i))
                        i = i.replace('60.000', '59.999')
                        finetime[c] = time_since_epoch_1958(i)

        except:

            print(f"INFO: hk_add_finetime: attempt level 3 -- OLD TCS non standard format")

            try:

                # Doesn't work due to masked values (missing entries)
                # finetime = np.array([time_since_epoch_1958(str(i)+'+0000') for i in hktab[hktab.colnames[0]]])

                c0 = hktab[hktab.colnames[0]]
                mask = np.ma.getmask(c0)
                finetime = np.zeros(len(c0), dtype=float)
                finetime[np.where(mask)] = np.nan
                for c, i in enumerate(c0):
                    if not mask[c]:
                        finetime[c] = time_since_epoch_1958(i + "+0000")

            except:

                print(sys.exc_info())
                print("ERROR: ADD_FINETIME - ALL ATTEMPTS FAILED - PLEASE CHECK THE TIMESTAMP FORMAT")
                return None

        hktab.add_column(Column(finetime,name="finetime"))

        hktab.sort(keys='finetime', reverse=False)

        hktab.add_column(Column(hktab['finetime']-hktab['finetime'][0],name="reltime"))

    return hktab


def hk_interpolate(hktab, time_step=60, decimals=6, outputfile= None, verbose=True):
    """
    hk_interpolate(hktab, time_step=60, decimals=6, outputfile=None, verbose=True)

    Time interpolation in a HK table, based on column 'finetime'

    WARNINGS
        - Integer columns will also be interpolated and the values may hence lose some of their meaning, e.g. status
          words or counters
        - String columns can't be interpolated, in particular all timestamp-related columns will be removed
          That concerns all column names containing "_ts" as well as "timestamp" and "timecode"

    """
    finetime = hktab['finetime']

    time_grid = np.arange(finetime[0], finetime[-1], step=time_step)

    keys = hktab.keys()

    htable = {}
    for key in keys:
        #if (key not in ["timestamp", "timecode"]) and (key.find("_ts")==-1):
        if (str(hktab[key].dtype).find('<U') != 0):
            htable[key] = []

    # for key in keys:
    #     print(f"{key} - {hktab[key].dtype}")

    for key in keys:
        #if (key not in ["timestamp", "timecode"]) and (key.find("_ts")==-1) and (hktab[key].dtype != np.dtype('bool')):
        if (str(hktab[key].dtype).find('<U') != 0):
            # Only MaskedColumn have a 'mask'
            # print(hktab[key].__class__, len(hktab[key]))
            if isinstance(hktab[key], astropy.table.column.MaskedColumn):
                valid_time_sel = np.where(np.logical_not(hktab[key].mask))
                if len(valid_time_sel[0]) > 1:
                    f = interp1d(finetime[valid_time_sel], hktab[key][valid_time_sel], kind='linear', fill_value='extrapolate')
                    htable[key] += list(f(time_grid))
                else:
                    htable[key] += [np.nan for i in range(len(time_grid))]
            else:
                f = interp1d(finetime, hktab[key], kind='linear', fill_value='extrapolate')
                htable[key] += list(f(time_grid))
        elif verbose:
            print(f"Column {key} is of type {hktab[key].dtype} --> skipped from the interpolation")

    # Convert HK lists to astropy.table.Columns
    # -----------------------------------------

    if verbose:
        print(f"    HK entries: {len(htable)}")

    tab = Table()
    for key in htable.keys():
        try:
            c = Column(data=np.round(np.array(htable[key]), decimals=decimals), name=key)
        except:
            c = Column(data=htable[key], name=key)
        tab.add_column(col=c)


    # OUTPUT
    # ------

    if outputfile is not None:
        overwrite = True
        ascii.write(table=tab, output=outputfile, format='fixed_width', overwrite=overwrite)


    return tab


def get_hk_date_range(start_date, end_date, datadir=None, device="SYN-HK", keys=None, time_step=60, outputfile=None, decimals=6, verbose=True):
    """
    SYNOPSIS
    get_hk_date_range(start_date, end_date, datadir=None, device="SYN-HK", time_step=60, outputfile=None, decimals=6, verbose=True)


    INPUT
    start_date, end_date : 20220205, 20220210  [int or string]
    datadir              : path to the daily HK files directory "/home/me/plato/SRON/plato-data/daily/"
    device               : device name, e.g. "SYN-HK" or ENSEMBLE"
    time_step            : time step for the interpolation. If 0, no interpolation is done.
    keys                 : list of parameter names to retrieve from the daily fines.
                           If None, all parameters are retrieved
    outputfile           : if given, the resulting table is printed in the "outputfile" in ascii (optional)
    decimals             : rounding of the HK, used when outputfile is not None
    verbose              : toggle INFO prints (boolean)

    LIMITATION:
    Before 20220205, TCS-HK.csv didn't have a proper timestamp column. Consequently the corresponding HK paramters
    cannot be retrieved with the present function before that date.

    EXAMPLE USE:
    A. Assuming env. variable PLATO_LOCAL_DATA_LOCATION is defined, and taking defaults device and time_step, no ascii output)
    hks = get_hk_table_days(start_date=start_date, end_date=end_date
    print(hks.colnames)

    B. Specifying everything
    datadir = "/Volumes/IZAR/plato/data/em/sron/daily/"
    outputdir = datadir.replace("/daily/", "/multi_day/")
    device="SYN-HK"
    start_date, end_date = 20211130, 20211202
    time_step = 60
    hks = get_hk_date_range(start_date=start_date, end_date=end_date, time_step=time_step, device=device, datadir=datadir, outputfile=outputdir+f"/hk_multi_day_{device}_{start_date}_{end_date}_step_{time_step}s.txt", decimals=6)

    C. As B. without any time interpolation --> potential for huge output file!
    time_step = 0
    hk0 = get_hk_date_range(start_date=start_date, end_date=end_date, time_step=time_step, device=device, datadir=datadir, outputfile=outputdir+f"/hk_multi_day_{device}_{start_date}_{end_date}_step_{time_step}s.txt")
    """
    from astropy import table

    if datadir is None:
        datadir = os.getenv("PLATO_LOCAL_DATA_LOCATION")
        datadir = datadir.replace("/obs/", "/daily/")

    # ASSEMBLE LIST OF DATES
    ########################
    alldays = np.array(os.listdir(datadir))
    idx_start = np.where(alldays == str(start_date))[0][0]
    idx_end   = np.where(alldays == str(end_date))[0][0]

    dates = alldays[idx_start:idx_end+1]

    # READ ALL HK FILES
    ###################
    hktables = []

    for date in dates:

        if verbose:
            print(f"Extracting {date}")

        hktables.append(get_hk_day(date=date, device=device, keys=keys, datadir=datadir, add_finetime=False,
                                   verbose=verbose))

    if verbose:
        print()
        print("Nb of records")
        for i,date in enumerate(dates):
            print (f"    {date} : {len(hktables[i])}")


    # STACK THE TABLES
    ###################
    if verbose:
        print()
        print("Stacking daily tables")

    hk_all = table.vstack(hktables)

    if verbose:
        print(f"{len(hk_all)}")

    # INCLUDE FINETIME
    ##################

    if verbose:
        print()
        print("Include Finetime")
        print(f"{len(hk_all)}")

    hk_all = hk_add_finetime(hk_all)

    # INTERPOLATE THE STACKED TABLE
    ###############################

    if (time_step is not None) and (time_step > 0):

        if verbose:
            print()
            print("Time - interpolation")

        hk_final = hk_interpolate(hk_all, time_step=time_step, decimals=decimals)

        if verbose:
            print(f"    Length of the interpolated table: {len(hk_final)}")

    else:

        hk_final = hk_all

    # OUTPUT
    ########

    if outputfile is not None:

        if verbose:
            print()
            print(f"Write to: {outputfile}")

        overwrite = True
        ascii.write(table=hk_final, output=outputfile, format='fixed_width', overwrite=overwrite)

    return hk_final

def get_tm_dictionary():
    """
    get_tm_dictionary()

    Reads the TM Dictionary from the egse distribution (~/plato-common-egse/src/egse/data/tm-dictionary.csv)
    """
    import egse
    filename = os.path.dirname(egse.__file__)+"/data/tm-dictionary.csv"
    result = ascii.read(filename, delimiter=";")
    return result

get_hk_dictionary = get_tm_dictionary

