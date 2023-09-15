from enum import Enum
from typing import Union

import numpy as np
from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList

from egse.state import GlobalState
from egse.system import time_since_epoch_1958


class DataProduct(str, Enum):

    IMAGE = "image"
    SERIAL_PRESCAN = "serial pre-scan"
    SERIAL_OVERSCAN = "serial over-scan"
    PARALLEL_OVERSCAN = "parallel over-scan"


DATA_PRODUCT_SUFFIX = {
    DataProduct.IMAGE: "IMAGE",
    DataProduct.SERIAL_PRESCAN: "SPRE",
    DataProduct.SERIAL_OVERSCAN: "SOVER",
    DataProduct.PARALLEL_OVERSCAN: "POVER"
}


def is_level2(fits_file: Union[str, HDUList]) -> bool:
    """ Check whether the given FITS file is a level-2 FITS file.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.

    Returns: True if the given FITS file is a level-2 FITS file; False otherwise.
    """

    return get_primary_header(fits_file)["LEVEL"] == 2


def get_overview(fits_file: Union[str, HDUList]):
    """ Print an overview of the content of the FITS file with the given name.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    hdul.info()

    if isinstance(fits_file, str):
        hdul.close()


def get_relative_time(fits_file: Union[str, HDUList], ccd_number: int = None, ccd_side = None) \
        -> Union[dict, np.array]:
    """ Return the relative time of the layers in the cube, w.r.t. the first exposure [s].

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: If the CCD number and CCD side are specified, an array with for each layer/exposure in the cube, the
             relative time w.r.t. the first layer/exposure; otherwise a dictionary with such an array for the specified
             CCD numbers and CCD sides.
    """

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)

    if ccd_number is None or ccd_side is None:

        relative_time = {}

        ccd_numbers = range(1, 5) if ccd_number is None else [ccd_number]
        ccd_sides = [fee_side.E, fee_side.F] if ccd_side is None else [ccd_side]

        for ccd_number in ccd_numbers:

            for ccd_side in ccd_sides:

                try:
                    relative_time[f"{ccd_number}{ccd_side.name[0]}"] = \
                        np.array(hdul[f"WCS-TAB_{ccd_number}_{fee_side(ccd_side).name[0]}"].data["TIME"])
                except KeyError:
                    pass

    else:
        relative_time = np.array(hdul[f"WCS-TAB_{ccd_number}_{fee_side(ccd_side).name[0]}"].data["TIME"])

    if isinstance(fits_file, str):
        hdul.close()

    return relative_time


def get_absolute_time(fits_file: Union[str, HDUList], ccd_number: int = None, ccd_side = None) \
        -> Union[dict, np.array]:
    """ Return the absolute time for the given side of the given CCD and exposure number.

    The absolute time is the number of seconds since the 1958 epoch.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Absolute time for the given side of the given CCD and exposure number [s].

    Returns: If the CCD number and CCD side are specified, an array with for each layer/exposure in the cube, the
             absolute time (in seconds since epoch 1958); otherwise a dictionary with such an array for the specified
             CCD numbers and CCD sides.
    """

    start_time = time_since_epoch_1958(get_primary_header(fits_file)["DATE-OBS"])
    relative_time = get_relative_time(fits_file, ccd_number=ccd_number, ccd_side=ccd_side)

    if ccd_number is None or ccd_side is None:

        for ccd_number, ccd_dict in relative_time.items():
            for ccd_side, rel_time in ccd_dict.items():
                relative_time[ccd_number][ccd_side] += start_time

        return relative_time

    else:
        return relative_time + start_time


###################
# Level 1 & Level 2
###################


def get_primary_header(fits_file: Union[str, HDUList]):
    """ Return the primary header of the given FITS file.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.

    Returns: Primary header of the given FITS file.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)

    primary_header = hdul["PRIMARY"].header

    if isinstance(fits_file, str):
        hdul.close()

    return primary_header


def get_ext_names(fits_file: Union[str, HDUList]):
    """ Return the list of extension names of the given FITS file.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.

    Returns: list of extension names of the given FITS file.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)

    ext_names = [hdul[i].header["EXTNAME"] for i in range(1, len(hdul))]
    ext_names.insert(0, "PRIMARY")

    if isinstance(fits_file, str):
        hdul.close()

    return ext_names


def _get_data(fits_file: HDUList, ccd_number: int, ccd_side, exposure_number: int, data_product: DataProduct):

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    try:

        suffix = DATA_PRODUCT_SUFFIX[data_product]

        if is_level2(fits_file):
            return fits_file[f"{suffix}_{ccd_number}_{fee_side(ccd_side).name[0]}"].data[exposure_number]
        else:
            return fits_file[f"{suffix}_{ccd_number}_{fee_side(ccd_side).name[0]}", exposure_number].data

    except KeyError:
        raise AttributeError(f"No {data_product} present for exposure {exposure_number} for the "
                             f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")

    except IndexError:
        raise AttributeError(f"Exposure {exposure_number} not present for the {data_product} for the "
                             f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")


def _get_header(fits_file: HDUList, ccd_number: int, ccd_side, exposure_number: int, data_product: DataProduct):

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    try:

        if is_level2(fits_file):
            raise AttributeError(f"To retrieve the {data_product} header for level-2 FITS files, use the "
                                 f"get_cube_header method.")

        else:
            suffix = DATA_PRODUCT_SUFFIX[data_product]
            return fits_file[f"{suffix}_{ccd_number}_{fee_side(ccd_side).name[0]}", exposure_number].header

    except KeyError:
        raise AttributeError(f"No {data_product} present for exposure {exposure_number} for the "
                             f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")

    except IndexError:
        raise AttributeError(f"Exposure {exposure_number} not present for the {data_product} for the "
                             f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")


def get_image_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the image data for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Image data for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    image_data = _get_data(hdul, ccd_number, ccd_side, exposure_number, DataProduct.IMAGE)

    if isinstance(fits_file, str):
        hdul.close()

    return image_data


def get_image_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the image header for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Image header for the given CCD and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    image_header = _get_header(hdul, ccd_number, ccd_side, exposure_number, DataProduct.IMAGE)

    if isinstance(fits_file, str):
        hdul.close()

    return image_header


def get_serial_prescan_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the serial pre-scan data for the given side of the given CCD and exposure number.

    Args:
        - filename: Name of the FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Serial pre-scan data for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_prescan_data = _get_data(hdul, ccd_number, ccd_side, exposure_number, DataProduct.SERIAL_PRESCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_prescan_data


def get_serial_prescan_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the serial pre-scan header for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Serial pre-scan header for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_prescan_header = _get_header(hdul, ccd_number, ccd_side, exposure_number, DataProduct.SERIAL_PRESCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_prescan_header


def get_serial_overscan_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the serial over-scan data for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Serial over-scan data for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_overscan_data = _get_data(hdul, ccd_number, ccd_side, exposure_number, DataProduct.SERIAL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_overscan_data


def get_serial_overscan_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the serial over-scan header for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Serial over-scan header for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_overscan_header = _get_header(hdul, ccd_number, ccd_side, exposure_number, DataProduct.SERIAL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_overscan_header


def get_parallel_overscan_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the parallel over-scan data for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Parallel over-scan data for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    parallel_overscan_data = _get_data(hdul, ccd_number, ccd_side, exposure_number, DataProduct.PARALLEL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return parallel_overscan_data


def get_parallel_overscan_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int):
    """ Return the parallel over-scan header for the given side of the given CCD and exposure number.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F)..
        - exposure_number: Exposure number (counting starts at zero).

    Returns: Parallel over-scan header for the given side of the given CCD, and exposure number.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    parallel_overscan_header = _get_header(hdul, ccd_number, ccd_side, exposure_number, DataProduct.PARALLEL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return parallel_overscan_header


#########
# Level 1
#########


def crop_flatfield(flatfield_fits_file: Union[str, HDUList], ccd_number: int, ccd_side, exposure_number: int,
                   data_fits_file: Union[str, HDUList]):
    """ Extract the relevant part of the flatfield for a given FITS file.

    We take the requested exposure from the requested side of the requested CCD from the flatfield FITS file and
    extract the region for which data is present in the given data FITS file.  Which part this is, can be derived from
    the corresponding header in the data FITS file.

    Args:
        - flatfield_fits_file: Either the name of the FITS file or the opened FITS file containing the flatfield.
                               Assumed is that this covers the whole CCD (spread over the two CCD sides).
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - exposure_number: Exposure number (counting starts at zero).
        - data_filename: Either the name of the data FITS file or the opened FITS file for which you need the flatfield.

    Returns: Relevant part of the flatfield.
    """

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    flatfield = get_image_data(flatfield_fits_file, ccd_number, ccd_side, exposure_number)

    # Determine which part of the flatfield we need

    v_start = get_primary_header(data_fits_file)["V_START"]

    if is_level2(data_fits_file):

        header = get_image_cube_header(data_fits_file, ccd_number, ccd_side)

    else:

        header = get_image_header(data_fits_file, ccd_number, ccd_side, 0)

    num_rows = header["NAXIS2"]
    num_columns = header["NAXIS1"]

    # Extract the relevant part from the flatfield

    if ccd_side == fee_side.LEFT_SIDE:

        # First row: v_start
        # Number of rows: as from the image header (NAXIS2)
        # First column: always 0
        # Number of columns: as from the image header (NAXIS1)

        return flatfield[v_start: v_start + num_rows, : num_columns]

    else:

        # First row: v_start
        # Number of rows: as from the image header (NAXIS2)
        # First column: 4510 - NAXIS1
        # Last column: always the last column of the CCD

        return flatfield[v_start: v_start + num_rows, GlobalState.setup.camera.ccd.num_columns - num_columns:]


#########
# Level 2
#########


def _get_cube_data(fits_file: HDUList, ccd_number: int, ccd_side, data_product: DataProduct):

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    if is_level2(fits_file):

        try:

            suffix = DATA_PRODUCT_SUFFIX[data_product]
            return fits_file[f"{suffix}_{ccd_number}_{fee_side(ccd_side).name[0]}"].data

        except KeyError:
            raise AttributeError(f"No {data_product} cube present for the "
                                 f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")

    else:
        raise AttributeError(f"The given FITS file is not a level-2 FITS file")


def _get_cube_header(fits_file: HDUList, ccd_number: int, ccd_side, data_product: DataProduct):

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    if is_level2(fits_file):

        try:

            suffix = DATA_PRODUCT_SUFFIX[data_product]
            return fits_file[f"{suffix}_{ccd_number}_{fee_side(ccd_side).name[0]}"].header

        except KeyError:

            raise AttributeError(f"No {data_product} cube present for the "
                                 f"{fee_side(ccd_side).name[0]}-side of CCD{ccd_number}.")

    else:

        raise AttributeError(f"The given FITS file is not a level-2 FITS file")


def get_image_cube_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the image data cube for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Image data cube for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    image_data = _get_cube_data(hdul, ccd_number, ccd_side, DataProduct.IMAGE)

    if isinstance(fits_file, str):
        hdul.close()

    return image_data


def get_image_cube_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the image cube header for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Image cube header for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    image_header = _get_cube_header(hdul, ccd_number, ccd_side, DataProduct.IMAGE)

    if isinstance(fits_file, str):
        hdul.close()

    return image_header


def get_serial_prescan_cube_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the serial pre-scan data cube for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Serial pre-scan data cube for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_prescan_data = _get_cube_data(hdul, ccd_number, ccd_side, DataProduct.SERIAL_PRESCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_prescan_data


def get_serial_prescan_cube_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the serial pre-scan cube header for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Serial pre-scan cube header for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_prescan_header = _get_cube_header(hdul, ccd_number, ccd_side, DataProduct.SERIAL_PRESCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_prescan_header


def get_serial_overscan_cube_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the serial over-scan data cube for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Serial over-scan data cube for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_overscan_data = _get_cube_data(hdul, ccd_number, ccd_side, DataProduct.SERIAL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_overscan_data


def get_serial_overscan_cube_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the serial over-scan cube header for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Serial over-scan cube header for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    serial_overscan_header = _get_cube_header(hdul, ccd_number, ccd_side, DataProduct.SERIAL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return serial_overscan_header


def get_parallel_overscan_cube_data(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the parallel over-scan data cube for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Parallel over-scan data cube for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    parallel_overscan_data = _get_cube_data(hdul, ccd_number, ccd_side, DataProduct.PARALLEL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return parallel_overscan_data


def get_parallel_overscan_cube_header(fits_file: Union[str, HDUList], ccd_number: int, ccd_side):
    """ Return the parallel over-scan cube header for the given side of the given CCD.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).

    Returns: Serial over-scan cube header for the given side of the given CCD.
    """

    hdul = fits_file if isinstance(fits_file, HDUList) else fits.open(fits_file)
    parallel_over_scan_cube = _get_cube_header(hdul, ccd_number, ccd_side, DataProduct.PARALLEL_OVERSCAN)

    if isinstance(fits_file, str):
        hdul.close()

    return parallel_over_scan_cube


def get_fp_coordinates(fits_file: Union[str, HDUList], ccd_number: int, ccd_side, row, column):
    """ Conversion to focal-plane coordinates.

    Convert the given (row, column) in the transmitted part of the given side of the given CCD to focal-plane
    coordinates.

    Args:
        - fits_file: Either the name of the FITS file or the opened FITS file.
        - ccd_number: CCD number (1/2/3/4).
        - ccd_side: CCD side (GlobalState.setup.camera.fee.ccd_sides.enum.E or
                    GlobalState.setup.camera.fee.ccd_sides.enum.F).
        - row: Row in the transmitted part of the given side of the given CCD.
        - column: Column in the transmitted part of the given side of the given CCD.

    Returns: Focal-plane coordinates (x_fp, y_fp) [mm].
    """

    if is_level2(fits_file):

        header = get_image_cube_header(fits_file, ccd_number, ccd_side)

    else:

        header = get_image_header(fits_file, ccd_number, ccd_side, 0)

    x_fp = header["CRVAL1"] + header["CD1_1"](column - header["CRPIX1"]) + header["CD1_2"](row - header["CRPIX2"])
    y_fp = header["CRVAL1"] + header["CD2_1"](column - header["CRPIX1"]) + header["CD2_2"](row - header["CRPIX2"])

    return x_fp, y_fp


def find_fits_ext(hdu, extname):
    """ find_fits_ext(hdu, extname)
    Browses the extention names in the cube, and returns the extension number(s) corresponding to "extname"
    """

    extnames = np.array(ff.get_ext_names(hdu))

    return list(np.where(extnames == extname)[0])


def get_fits_ext(hdu, extname, nth=0):
    """
    Identifies the list of extensions with the desired name, and returns the first one among them
    Use parameter 'nth' to replace "first" by 'nth'
    """

    ext_ids = find_fits_ext(hdu, extname)

    return np.array(hdu[ext_ids[nth]].data, dtype=float)

