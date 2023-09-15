from math import pow, sqrt

import sep


def find_sources(image):

    """ Find (point) sources in the given image.

    Find (point) sources in the given image, using the SExrtactor algorithm
    (Bertin & Arnouts 1996) as implemented in the "SEP" Python library for
    Source Extraction and Photometry
    (see: https://sep.readthedocs.io/en/v1.0.x/index.html and Barbary 2016).

    The row and column coordinates of the position of the extracted sources in
    the image are returned.

    Args:
        - image: Image in which to look for (point) sources, represented by a
                2D numpy array.

    Returns:
        - Two 1D numpy arrays with the row and column coordinates where the
          extracted sources are located within the given image.
    """

    # Background subtraction
    #   - Spatially varying background
    #   - Evaluate backgroudn as 2D array (same dimensions as image)

    background = sep.Background(image)
    background_image = background.back()

    background_subtracted_image = image - background_image

    # Source extraction (SExtractor)
    #   - thresh = 1.5
    #   - err = RMS of the background
    #   - threshold pixel value for detection = thresh * err
    #   - default values for all other parameters for SExtractor

    sources = sep.extract(background_subtracted_image, 1.5,
                          err=background.globalrms)

    # Return (row, column) coordinates of the found sources

    rows = sources["y"]
    columns = sources["x"]

    return rows, columns


def get_centroid_single_image(image):

    """ Calculate centroid of the (single) source in the given image.

    Args:
        - image: Image in which to look for a single (point) sources,
                  represented by a 2D numpy array.

    Returns:
        - row_centroid: Row coordinate of the centroid [pixels].
        - column_centroid: Column coordinate of the centroid [pixels].
    """

    row_centroid = 0
    column_centroid = 0

    weight = 0

    for row in range(image.shape[0]):

        for column in range(image.shape[1]):

            row_centroid += image[row][column] * row
            column_centroid += image[row][column] * column

            weight += image[row][column]

    row_centroid /= weight
    column_centroid /= weight

    return row_centroid, column_centroid


def get_rms_spot_size_single_image(image, row_centroid=None, column_centroid=None):

    """ Calculate the RMS spot size for a (single) source in the given image.

    If the centroid coordinates are not specified, these will be calculated.

    Args:
        - image: Image in which to look for a single (point) sources,
                represented by a 2D numpy array.
        - row_centroid: Row coordinate of the centroid [pixels].
        - column_centroid: Column coordinate of the centroid [pixels].
    """

    if (row_centroid is None) or (column_centroid is None):

        print("Coordinates for centroid not specified.  Calculating with " +
              "get_centroid_single_image.")
        row_centroid, column_centroid = get_centroid_single_image(image)

    spot_size = 0
    total_weight = 0

    for row in range(image.shape[0]):

        for column in range(image.shape[1]):

            weight = image[row][column]

            spot_size += (weight *
                         (pow(row - row_centroid, 2) +
                          pow(column - column_centroid, 2)))
            total_weight += weight

    spot_size = 2 * sqrt(spot_size / total_weight)

    return spot_size
