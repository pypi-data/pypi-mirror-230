import os
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "3 — Hartmann"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"
DATA_PATH = Path(os.environ.get("PLATO_DATA_STORAGE_LOCATION"))


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_hartmann_verification(
        use_angles: bool = False,
        exposure_time: float = 0.2,
        num_cycles: int = 5,
        n_rows: int = 1000,
        sort_fov_pos_in_azimuth: bool = True,
        reverse_azimuth_order: bool = False,
        description: str = "Ambient Hartmann Verif 40 positions",
        table_name: str = 'reference_full_40',
):
    """ Command a pre-defined set of FOV positions for Hartmann verification.

    Args:
        - use_angles: If False, use the (x, y) positions as provided by LDO; otherwise use the computed angles
                      (theta, phi).
        - exposure_time: Exposure time [s].
        - num_cycles: Number of exposures to acquire at each FOV position.
        - n_rows: Number of rows to read (in partial-readout mode) around each visited position.
        - sort_fov_pos_in_azimuth: If True, the positions will be visited in ascending azimuth, from -180 to +180
                                   degrees.
        - reverse_azimuth_order: If True, and sort_fov_pos_in_azimuth=True,  the positions will be visited in
                                 descending azimuth, from +180 to -180 degrees.
        - description: Description of the observation.
        - table_name: Name of the table with the pre-defined FOV positions in the setup (in setup.fov_positions).
    """

    from camtest.commanding.cam_aat_050_ambient_hartmann_verification import cam_aat_050_ambient_hartmann_verification
    from camtest import execute

    # use_angles : False: [x,y] positions from LDO. True : computed FoV angles [theta,phi]
    execute(cam_aat_050_ambient_hartmann_verification,
            num_cycles=num_cycles, exposure_time=exposure_time, n_rows=n_rows,
            table_name=table_name, use_angles=use_angles, sort_fov_pos_in_azimuth=sort_fov_pos_in_azimuth,
            reverse_azimuth_order=reverse_azimuth_order, description=description)


@exec_ui(display_name="Reduce",
         icons=(ICON_PATH / "reduce.svg", ICON_PATH / "reduce-selected.svg"))
def reduce_hartmann_verification(
        obsid: int = 3348,
        use_angles: bool = False,
        distorted_input: bool = True,
        distorted_output: bool = True,
        sort_fov_pos_in_azimuth: bool = False,
        reverse_order: bool = False,
        verbose: bool = True,
        n_layers: int = 5,
        table_name: str = 'reference_full_40',
        data_dir: Directory = "/Volumes/IZAR/plato/data/em/sron/obs/",
        output_dir: Directory = "/Volumes/IZAR/plato/data/reduced/",
):
    """ Reduction of a given Hartmann verification observation.

    For Hartmann (LDO x, y positions): use_angles=False, distorted_input=True
    For Flexible (computed thetas and phis): use_angles=True, distorted_input=False

    Args:
        - obsid: Obsid to reduce.
        - use_angles: If False, use the (x, y) positions as provided by LDO; otherwise use the computed angles
                      (theta, phi).
        - distorted_input:
        - distorted_output:
        - sort_fov_pos_in_azimuth: If True, the positions will be visited in ascending azimuth, from -180 to +180
                                   degrees.
        - reverse_azimuth_order: If True, and sort_fov_pos_in_azimuth=True,  the positions will be visited in
                                 descending azimuth, from +180 to -180 degrees.
        - verbose: Whether to print out verbose information.
        - n_layers: Number of layers in data every cube.
        - table_name: Name of the table with the pre-defined FOV positions in the setup (in setup.fov_positions).
        - data_dir: Folder where the input data is (usually the 'obs' folder).
        - output_dir: Folder where the reduction results will be stored.

    Returns:
        - Table with all results, also saved in FITS files.
    """
    import numpy as np
    import camtest.analysis.functions.fov_utils as fovu
    from camtest.analysis.functions.hartmann_utils import hartmann_reduction

    [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides] = \
        fovu.coords_from_table(table_name=table_name, use_angles=use_angles, distorted_input=distorted_input,
                               distorted_output=distorted_output, sort_fov_pos_in_azimuth=sort_fov_pos_in_azimuth,
                               reverse_order=reverse_order, verbose=verbose)

    layer_selection = np.array([1, 2, 3, 4], dtype=int)
    cube_selection = None

    data_dir = f"{str(data_dir)}/"  # make sure the folder name ends with a '/'
    output_dir = f"{str(output_dir)}/"  # make sure the folder name ends with a '/'

    ctab = hartmann_reduction(obsid=obsid, nlayers=n_layers, layer_selection=layer_selection, cube_selection=cube_selection,
                              fov_angles=angles_in, datadir=data_dir, outputdir=output_dir, verbose=True)

    print(f"{ctab = }")

    return ctab


@exec_ui(display_name="Analyse",
         icons=(ICON_PATH / "analysis.svg", ICON_PATH / "analysis-selected.svg"))
def analyse_hartmann_verification(
        obsids: ListList([int, str, str], [642, "IAS", "IAS Pre-Bolting"]),
        n_thetas: int = 4,
        reduced_dir: Directory = DATA_PATH / "reduced",
        output_dir: Directory = DATA_PATH / "analysed/pngs/",
        n_sigma: float = 3.,
        meas_error: float = 5.,
        maxsize: int = 100,
        figname: str = None,
        save: bool = True,
        verbose: bool = True,
):
    """ Analysis of a given Hartmann verification observation (after the reduction thereoff).

    Args:
        - obsids : Obsids to analyse and how to label each of them in the plot. This is a list of lists:
          [obsid, site, plot_label], of types [int, str, str]
        - n_thetas: Number of values of the boresight angle (theta) in the full hartmann verification
                  e.g. : 40 positions -> 5
                         76 positions -> 5       (6 if including the optical axis).
        - reduced_dir: Folder where the reduction results were be stored.
        - output_dir: Folder where the analysis results (png & txt file) will be stored.
        - n_sigma & meas_error: Define the tolerance to accept that 2 measurements are compatible within tolerance and
                                measurement uncertainty.  If meas_error is None, it is derived from the standard
                                deviation of the measurements (= assuming there's no systematic error on it, e.g. a
                                tilt).

        - maxsize : For outlier rejection: Hartmann patterns > maxsize are rejected/
        - figname : Figure name (allowing the user to further interact with it after this function finishes).
        - save : If True, the PNG and txt file (quantitative results) are written to output_dir.
        - verbose: Whether to print out verbose information.

    Returns:
        - Current figure
        - Current axes  instance on the current figure
        - String matching the content of the output text file, as well as the series of print statements issued when
          verbose=True
    """
    import matplotlib.pyplot as plt
    from camtest.analysis.functions import hartmann_utils
    from camtest import load_setup

    reduced_dir = f"{str(reduced_dir)}/"  # make sure the folder name ends with a '/'

    setup = load_setup()
    print(f"{setup=}")

    plotname, resultstr = hartmann_utils.hartmann_analysis_full(
        obsids, n_thetas=n_thetas, datadir=reduced_dir, maxsize=maxsize, figname=figname, setup=setup, n_sigma=n_sigma, meas_error=meas_error, verbose=verbose)

    if save:
        output_dir = f"{str(output_dir)}/"  # make sure the folder name ends with a '/'

        print(f"Saving plot to {output_dir + plotname}")
        plt.savefig(output_dir + plotname)

        txtname = f"{plotname.split('.')[0]}.txt"

        with open(output_dir + txtname, "w") as file:
            file.write(resultstr)

        print(f"Hartman analysis:  plot  saved as {output_dir}/{plotname}")
        print(f"                  result saved as {output_dir}/{txtname}")

    return plt.gcf(), plt.gca(), resultstr
