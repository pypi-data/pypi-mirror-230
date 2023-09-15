"""
This test suite contains tests for the image processing module.
"""

import logging

import numpy as np

from camtest.analysis.find_sources import find_sources

logger = logging.getLogger(__name__)


def test_find_sources():

    """
    Test the findSources() method.
    """

    logger.info(f"Inside test_find_sources(): __name__ = {__name__}")

    x, y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))
    data = np.sqrt(x**2 + y**2)
    sigma, mu = 0.05, 0.0
    image = np.exp(-((data - mu)**2 / (2.0 * sigma**2)))

    (rows, columns) = find_sources(image)

    assert len(rows) == 1
    assert len(columns) == 1
    assert abs(rows[0] - (200. - 1.) / 2.) <= 0.000005
    assert abs(columns[0] - (200. - 1.) / 2.) <= 0.000005
