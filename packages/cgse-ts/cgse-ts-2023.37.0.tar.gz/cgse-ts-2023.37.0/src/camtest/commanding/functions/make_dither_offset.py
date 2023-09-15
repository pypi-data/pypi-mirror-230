from random import uniform

import numpy as np


def make_dither_offsets(num_dither_positions=25, dither_amplitude=0.012):
    """ Return dither offsets in field angles theta and phi, expressed in degrees.

    Args:
        - num_dither_positions: Number of dither positions.
        - dither_amplitude: in degrees

    Returns:
        - Array of dither offsets for field angle theta (i.e. the angular distance from the optical axis) [degrees].
        - Array of dither offsets for field angle phi (i.e. angle from the x-axis of the focal plane [degrees].
    """

    # See https://github.com/IvS-KULeuven/plato-test-scripts/issues/177

    delta_theta = np.array([])
    delta_phi = np.array([])

    for dither_index in range(num_dither_positions):

        delta_theta = np.append(delta_theta, uniform(-dither_amplitude, dither_amplitude))
        delta_phi = np.append(delta_phi, uniform(-dither_amplitude, dither_amplitude))

    return delta_theta, delta_phi
