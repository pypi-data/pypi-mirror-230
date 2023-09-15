"""
PLATO
    Observation Class
    get_observation convenience, to download an obsid  (demands rsync enabled with KUL data repository)

See demo in camtest/demos/demo_observation.py

Version : 0.1 20211216. Brainstorming version
          1.0 20211218. First version

P. Royer, R. Huygen
"""

import os
import re
import time
import numpy as np
import subprocess
from astropy.io import fits
from camtest import GlobalState
import camtest.analysis.convenience as cv
import camtest.analysis.functions.hk_utils as hku
import egse

class Observation:

    def __init__(self, obsid, site=None, data_dir=None):
        """
        Very basic constructor

        obsid   : integer
        site    : in ["CSL", "CSL1", "CSL2", "SRON", "IAS", "INTA"]
        data_dir: None --> environment variable PLATO_LOCAL_DATA_LOCATION is used
                  else --> full path pointing to the data directory containing 1 directory / obsid (the "obs" directory)
        """

        self.obsid = obsid
        self.strobsid = str(obsid).zfill(5)

        if data_dir is None:
            data_dir = os.getenv("PLATO_LOCAL_DATA_LOCATION")  #+"/obs/"

        self.data_dir = data_dir
        self.obsid_dir = cv.fileSelect([self.strobsid], location=data_dir)[0] + '/'
        self.dir = self.path = data_dir + self.obsid_dir

        if site is not None:
            self.site = site
        else:
            #     self.site = GlobalState.setup.site_id
            self.site = self.get_site()

        cm_finetime = self._get_finetime(device="CM")
        self.start_time = cm_finetime[0]
        self.end_time = cm_finetime[-1]

        self.setup_id = self.get_setup_id()

        self.obsid_full = self.get_obsid_full()

        self.ncubes = self.get_number_cubes()


    def get_filenames(self, selection=None, full_path=True):
        """
        Returns the names of the data files associated to this obsid

        selection, in:
            'csv' or 'hk' : only the csv files with the HK
            'cubes' : fits cubes
            'all' or None: everything

        full_path : True  : filenames are returned in full-path : data_dir + obsid_dir + data_filename
                    False : the path is ignored, the list of 'data_filename' is returned
        """

        if selection is None:
            filenames = cv.fileSelect([f'{self.strobsid}_'], location=self.path)
        else:
            filenames = cv.fileSelect([f'{self.strobsid}_', selection], location=self.path)

        if full_path:
            filenames = [self.path + filename for filename in filenames]

        return filenames


    def get_filenames_hk(self, full_path=True):
        """
        Returns the names of the csv data files with the HK
        """
        filenames = cv.fileSelect([f'{self.strobsid}_', 'csv'], location=self.path)

        if full_path:
            filenames = [self.path + filename for filename in filenames]

        return filenames

    get_filenames_csv = get_filenames_hk


    def get_filenames_cubes(self, full_path=True):
        """
        Returns the names of the csv data files with the HK
        """
        filenames = cv.fileSelect([f'{self.strobsid}_', 'cube', 'fits'], location=self.path)

        if full_path:
            filenames = [self.path + filename for filename in filenames]

        return filenames

    get_filenames_fits = get_filenames_cubes


    def __summary(self):
        """
        Prints cubes, extension names, key header entries & data structure structure, TBD
        """
        raise NotImplementedError


    def get_execution(self):
        """
        Print the corresponding obsid-table entry
        """

        flag = 0
        obs_table = cv.fileSelect(["obsid-table"], location=self.data_dir)
        if not obs_table:
            flag = 1
            obs_table = cv.fileSelect(["obsid-table"], location=self.data_dir+"../")[0]

        location = self.data_dir + flag * "../"

        with open(location + obs_table, "r") as file:
            for line in file:
                if re.search(self.strobsid, line):
                    print(line)


    def get_log(self):
        """
        """
        raise NotImplementedError


    def get_site(self):
        """
        Find the site used for self from the Configuration Manager HK
        """
        afile = self.get_filenames(selection='_CM_', full_path=True)[0]
        f = open(afile, 'r')
        f.readline()
        aline = f.readline()
        site = aline.split(",")[1]

        return site

    def get_setup_id(self):
        """
        Find the setup used for self from the Configuration Manager HK
        """
        #afile = self.get_filenames(selection='csv', full_path=False)[0]
        #setup_id = afile.split("_")[2]

        afile = self.get_filenames(selection='_CM_', full_path=True)[0]
        f = open(afile, 'r')
        f.readline()
        aline = f.readline()
        setup_id = aline.split(",")[2]

        return int(setup_id)


    def get_obsid_full(self):
        """
        Returns the origin obsid made of its three components: <obsid>_<site>_<setup_id>
        """
        return self.strobsid + "_" + self.site + "_" + str(self.setup_id).zfill(5)


    def print_cube_shapes(self, extension=2):
        """
        Visits the cubes and prints the datasize of "extension" of each
        extension can be either a string or a integer
        """
        filenames = self.get_filenames(selection='cube', full_path=True)

        print(f"\nVisiting extension {extension} of every cube:\n")

        for cn in range(len(filenames)):
            hduc = fits.open(filenames[cn])
            time.sleep(0.25)
            try:
                print(f"{cn:3d} {hduc[extension].data.shape}")
            except:
                print(f"{cn:3d} extension {extension} not found")


    def get_hk(self, device, verbose=True):
        """
        Get the HK table for device "device" acquired during this obsid.

        device = a unique string identifying a device among all csv files, e.g. "SYN-HK", "ENSEMBLE"
        """
        return hku.get_hk(obsid=self.obsid, device=device, datadir=self.path, verbose=verbose)


    def get_hk_per_frame(self, device, keys, outputfile=None, decimals=6):
        """
        Get the HK table for 'device' interpolated at the time of every frame from this obsid

        device = a unique string identifying a device among all csv files, e.g. "SYN-HK", "ENSEMBLE"

        keys = a list of the HK entries to include (list of strings, exact match)

        outputfile = None. If specified, the table is printed there

        decimals = 6 : allows to limit the nb of digits in the output (one single value for all keys)
        """
        return hku.hk_per_frame([self.obsid], device=device, keys=keys, datadir=self.data_dir,
                                outputfile=outputfile, decimals=decimals)


    def get_hk_per_cube(self, device, keys, outputfile=None, decimals=6, func=np.nanmean):
        """
        Get the HK table for 'device' averaged over the time of every frame within each cube

        device = a unique string identifying a device among all csv files, e.g. "SYN-HK", "ENSEMBLE"

        keys = a list of the HK entries to include (list of strings, exact match)

        outputfile = None. If specified, the table is printed there

        decimals = 6 : allows to limit the nb of digits in the output (one single value for all keys)
        """
        return hku.hk_per_cube([self.obsid], device=device, keys=keys, datadir=self.data_dir, func=func,
                               outputfile=outputfile, decimals=decimals)

    def get_hk_devices(self):
        """
        Returns the list of available devices producing HK for this obsid
        """
        return hku.get_device_names(self.obsid, self.data_dir)


    def get_hk_names(self, device):
        """
        Returns the list of available HK entries for this obsid and device
        """
        return hku.get_hk_names(self.obsid, self.data_dir, device=device)

    def get_frame_times(self):
        """
        Returns an array of frame-acquisition-times, in 'seconds since 1958' ('finetime')
        """

        filenames = self.get_filenames(selection='cube', full_path=True)

        return cv.get_frame_times(filenames)


    def get_frame_times_relative(self):
        """
        Returns an array of frame-acquisition-times, in 'seconds after the start of this obsid' (self.start_time)
        """
        return self.get_frame_times() - self.start_time


    def _get_finetime(self, device="CM"):
        """
        Extract the finetime from the HK of 'device'

        By default, the ControlManager device "CM"
        """
        hk = self.get_hk(device=device, verbose=False)
        return hk["finetime"]


    def _get_reltime(self, device="CM"):
        """
        Extract the finetime from the HK of 'device'

        By default, the ControlManager device "CM"
        """
        hk = self.get_hk(device=device, verbose=False)
        return hk["reltime"]


    def get_start_time(self):
        """
        Get the starting time of this obsid

        The starting time is defined by the first timestamp in the HK of the ControlManager after the start of the obsid
        """
        #return self._get_finetime()[0]
        return self.start_time

    def get_end_time(self):
        """
        Get the starting time of this obsid

        The ending time is defined by the last timestamp in the HK of the ControlManager recorded as part of this obsid
        """
        #return self._get_finetime()[-1]
        return self.end_time

    def get_duration(self):
        """
        Returns the duration, in seconds, between start and end times
        """
        return self.end_time - self.start_time


    def get_cube_hdu(self, cube_number, verbose=True):
        """
        Lists all data cubes belonging to this obsid

        Opens cube with #cube_number and returns the fits object
        """
        filenames = self.get_filenames_cubes(full_path=True)

        hduc = fits.open(filenames[cube_number])

        if verbose:
            print(hduc.info())

        return hduc

    def get_number_cubes(self):
        """
        Returns the number of cubes in this observation
        """
        return len(self.get_filenames_cubes())




def download_observation(obsid, selection=None, data_dir=None, site=None, camera=None, setup=None, em1=False):
    """
    SYNOPSIS
    get_observation(obsid, selection=None, data_dir=None, site=None, camera=None, setup=None, em1=False)

    EFFECT
    Downloads the observation from the data-repository @KUL via rsync

    INPUTS
    Mandatory:
        obsid : observation ID (integer)

    Optional
        site = None
            site must be in [None, "CSL", "CSL1", "CSL2", "SRON", "IAS", "INTA"]
            if site is None, it is assumed equivalent to setup.site_id, or GlobalState.setup.site_id if neither site not
            setup are provided

        camera = None
            camera.ID
            if camera is None, it is taken from setup.camera.ID

        data_dir = None:
            By default, the data are written to $PLATO_LOCAL_DATA_LOCATION/
            If data_dir is not None, the data are written in <data_dir>/

        selection = None:
            By default the data consists in
                - the HK, contained in csv files
                - the image data cubes, in fits format
            If selection is in ['hk', 'csv'], only the HK will be downloaded
            If selection is in ['cube', 'fits'], only the image data cubes will be downloaded

        setup : egse.setup.Setup. Used to extract the site

        em1 :  set em1 True for SRON EM #1 data
               (during SRON EM#1, the data directories did contain the setup number)

    """

    if em1:

        print("INFO: Targetting SRON EM #1 data")

        if isinstance(setup, egse.setup.Setup):
            strsetup = "_"+setup.get_id()
        else:
            strsetup = "_"+str(setup).zfill(5)

    else:

        strsetup = ""


    strobsid = str(obsid).zfill(5)

    # DETERMINE THE OUTPUT DIRECTORY
    ################################

    if site is None:
        if setup and isinstance(setup, egse.setup.Setup):
            site = setup.site_id
        else:
            try:
                site = GlobalState.setup.site_id
            except:
                print("ERROR: test site could not be determined. Please provide 'site', 'setup' or run load_setup")

    if camera is None:
        if setup and isinstance(setup, egse.setup.Setup):
            camera = setup.camera.ID
        else:
            try:
                camera = GlobalState.setup.camera.ID
            except:
                print("ERROR: camera could not be determined. Please provide 'camera', 'setup' or run load_setup")


    if data_dir is None:
        data_dir = os.getenv("PLATO_LOCAL_DATA_LOCATION")# + "/obs/"

    obsid_dir = f"{strobsid}_{site}{strsetup}_{camera}"

    output_dir = data_dir + obsid_dir

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # DOWNLOAD
    ##########

    if (site == "SRON"):
        target = f"copernicus.ster.kuleuven.be:/STER/platodata/{site}/plato-data/SRON/obs/{obsid_dir}/*"
    elif (site == "IAS"):
        target = f"copernicus.ster.kuleuven.be:/STER/platodata/{site}/data/IAS/obs/{obsid_dir}/*"
    elif (site.find("CSL") >= 0):
        target = f"copernicus.ster.kuleuven.be:/STER/platodata/{site}/data/obs/{obsid_dir}/*"
    elif (site.find("INTA") >= 0):
        target = f"copernicus.ster.kuleuven.be:/STER/platodata/{site}/data/obs/{obsid_dir}/*"

    if selection in ['hk', 'csv']:
        target += "csv"
        subprocess.run(["rsync", "-vau", target, output_dir])

    elif selection in ['cube', 'cubes', 'fits']:
        target += "cube*fits"
        subprocess.run(["rsync", "-vau", target, output_dir])

    else:
        subprocess.run(["rsync", "-vau", target+"csv", output_dir])
        subprocess.run(["rsync", "-vau", target+"cube*fits", output_dir])


